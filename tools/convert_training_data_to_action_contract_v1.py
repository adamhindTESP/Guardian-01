#!/usr/bin/env python3
"""
Convert Guardian training JSONL batches into schema-valid Action Contract v1 plans.

Input formats supported:
1) Chat-style records:
   {"category": "...", "messages": [{"role":"user","content":...}, {"role":"assistant","content":"{...json...}"}]}

2) Raw plan dict lines (already JSON):
   {"schema_version": "...", "goals":[...], "parameters":{...}}
   {"actions":[...]}  (already schema-valid)

Outputs:
- training_data/normalized/<input_filename>.jsonl
  Each line is a *plan dict* that conforms to the frozen schema:
    {"actions":[{"type": "...", "params": {...}}, ...]}

Notes:
- This script is NON-authoritative tooling (safe w.r.t. freeze/gates).
- It clamps speed/force/duration to contract bounds and drops unknown fields.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---- Frozen contract bounds (mirror schema) ----
MAX_ACTIONS = 16
MAX_DURATION_S = 30.0
MAX_SPEED_MPS = 0.5
MAX_FORCE_N = 2.0
MAX_UTTERANCE_LEN = 200

ALLOWED_TYPES = {"stop", "wait", "observe", "speak", "navigate", "grasp", "release"}


def clamp(x: Any, lo: float, hi: float) -> float:
    try:
        v = float(x)
    except Exception:
        return lo
    return max(lo, min(hi, v))


def coerce_target(t: Any) -> Optional[str]:
    """
    Convert target representations into the contract's canonical string.
    - If {"kind": "...", "id": "..."} -> "id"
    - If {"id": "..."} -> "id"
    - If string -> string
    Otherwise -> None
    """
    if t is None:
        return None
    if isinstance(t, str):
        s = t.strip()
        return s or None
    if isinstance(t, dict):
        if "id" in t and isinstance(t["id"], str):
            s = t["id"].strip()
            return s or None
        # sometimes nested like {"target":{"kind":...,"id":...}}
    return None


def normalize_action_from_goal(goal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Old shape examples:
      {"action":"observe","target":{"kind":"location","id":"kitchen"}}
      {"action":"speak","params":{"text":"..."}}
      {"action":"wait","params":{"duration_s":300}}
    New shape required:
      {"type":"observe","params":{"target":"kitchen"}}
      {"type":"speak","params":{"utterance":"..."}}
      {"type":"wait","params":{"duration_s":30}}
    """
    a = goal.get("action") or goal.get("type")
    if not isinstance(a, str):
        return None
    a = a.strip()
    if a not in ALLOWED_TYPES:
        # If someone used "say" etc, treat as vetoable by dropping it.
        return None

    out: Dict[str, Any] = {"type": a}

    # Gather params from multiple possible places
    params_in: Dict[str, Any] = {}
    if isinstance(goal.get("params"), dict):
        params_in.update(goal["params"])
    # some old shapes put fields at top-level
    for k in ("target", "duration_s", "speed_mps", "force_n", "utterance", "text"):
        if k in goal and k not in params_in:
            params_in[k] = goal[k]

    params_out: Dict[str, Any] = {}

    # target
    if a in {"observe", "navigate", "grasp", "release"}:
        tgt = coerce_target(params_in.get("target"))
        if tgt is None:
            # also check if goal had {"target":{...}}
            tgt = coerce_target(goal.get("target"))
        if tgt is not None:
            params_out["target"] = tgt

    # wait duration
    if a == "wait":
        if "duration_s" in params_in:
            params_out["duration_s"] = clamp(params_in["duration_s"], 0.0, MAX_DURATION_S)

    # bounded motion params (optional)
    if "speed_mps" in params_in:
        params_out["speed_mps"] = clamp(params_in["speed_mps"], 0.0, MAX_SPEED_MPS)
    if "force_n" in params_in:
        params_out["force_n"] = clamp(params_in["force_n"], 0.0, MAX_FORCE_N)

    # speak utterance
    if a == "speak":
        utter = params_in.get("utterance")
        if not utter and "text" in params_in:
            utter = params_in.get("text")
        if isinstance(utter, str):
            utter = utter.strip()[:MAX_UTTERANCE_LEN]
            if utter:
                params_out["utterance"] = utter

    if params_out:
        out["params"] = params_out

    return out


def normalize_plan(plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Accepts either:
    - already-valid {"actions":[...]}
    - old {"goals":[...], "parameters":{...}, "schema_version":...}
    Returns:
    - {"actions":[...]} limited to MAX_ACTIONS, minItems=1
    """
    # If already has actions in new format, try to sanitize minimally
    if isinstance(plan.get("actions"), list):
        actions_out: List[Dict[str, Any]] = []
        for item in plan["actions"][:MAX_ACTIONS]:
            if not isinstance(item, dict):
                continue
            t = item.get("type")
            if not isinstance(t, str) or t.strip() not in ALLOWED_TYPES:
                continue
            t = t.strip()
            a: Dict[str, Any] = {"type": t}
            p = item.get("params")
            if isinstance(p, dict) and p:
                p2: Dict[str, Any] = {}
                if "target" in p:
                    tgt = coerce_target(p.get("target"))
                    if tgt:
                        p2["target"] = tgt
                if "duration_s" in p and t == "wait":
                    p2["duration_s"] = clamp(p["duration_s"], 0.0, MAX_DURATION_S)
                if "speed_mps" in p:
                    p2["speed_mps"] = clamp(p["speed_mps"], 0.0, MAX_SPEED_MPS)
                if "force_n" in p:
                    p2["force_n"] = clamp(p["force_n"], 0.0, MAX_FORCE_N)
                if "utterance" in p and t == "speak" and isinstance(p["utterance"], str):
                    u = p["utterance"].strip()[:MAX_UTTERANCE_LEN]
                    if u:
                        p2["utterance"] = u
                if p2:
                    a["params"] = p2
            actions_out.append(a)

        if not actions_out:
            return None
        return {"actions": actions_out}

    # Old format: goals[]
    goals = plan.get("goals")
    if isinstance(goals, list):
        actions_out: List[Dict[str, Any]] = []
        for g in goals:
            if not isinstance(g, dict):
                continue
            a = normalize_action_from_goal(g)
            if a:
                actions_out.append(a)
            if len(actions_out) >= MAX_ACTIONS:
                break
        if not actions_out:
            return None
        return {"actions": actions_out}

    return None


def extract_assistant_plan(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    From a chat-style JSONL line:
      {"messages":[..., {"role":"assistant","content":"{...}"}]}
    Return parsed assistant JSON dict.
    """
    msgs = record.get("messages")
    if not isinstance(msgs, list):
        return None

    assistant_content = None
    for m in reversed(msgs):
        if isinstance(m, dict) and m.get("role") == "assistant":
            assistant_content = m.get("content")
            break

    if not isinstance(assistant_content, str):
        return None

    assistant_content = assistant_content.strip()
    if not assistant_content:
        return None

    try:
        obj = json.loads(assistant_content)
    except Exception:
        return None

    return obj if isinstance(obj, dict) else None


def convert_file(in_path: Path, out_dir: Path) -> Tuple[int, int, int]:
    """
    Returns: (total_lines, converted_ok, converted_failed)
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / in_path.name

    total = ok = bad = 0

    with open(in_path, "r", encoding="utf-8") as fin, open(out_path, "w", encoding="utf-8") as fout:
        for line in fin:
            total += 1
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except Exception:
                bad += 1
                continue

            plan_obj: Optional[Dict[str, Any]] = None

            # Case A: chat record with messages -> parse assistant content
            if isinstance(obj, dict) and "messages" in obj:
                plan_obj = extract_assistant_plan(obj)
            # Case B: plan dict directly
            elif isinstance(obj, dict):
                plan_obj = obj

            if not isinstance(plan_obj, dict):
                bad += 1
                continue

            normalized = normalize_plan(plan_obj)
            if not normalized:
                bad += 1
                continue

            fout.write(json.dumps(normalized, ensure_ascii=False) + "\n")
            ok += 1

    return total, ok, bad


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    training_data = repo_root / "training_data"
    out_dir = training_data / "normalized"

    if not training_data.exists():
        print(f"ERROR: training_data not found at: {training_data}")
        return 2

    # Convert all likely batch files + golden files
    patterns = [
        "batch_*.jsonl",
        "golden_plans*.jsonl",
    ]

    files: List[Path] = []
    for pat in patterns:
        files.extend(sorted(training_data.glob(pat)))

    if not files:
        print(f"No input files found in {training_data} matching {patterns}")
        return 1

    grand_total = grand_ok = grand_bad = 0
    print(f"Converting {len(files)} file(s) -> {out_dir}")
    for f in files:
        total, ok, bad = convert_file(f, out_dir)
        grand_total += total
        grand_ok += ok
        grand_bad += bad
        print(f"- {f.name}: lines={total}  ok={ok}  failed={bad}")

    print("\n=== Summary ===")
    print(f"Total lines read : {grand_total}")
    print(f"Plans converted  : {grand_ok}")
    print(f"Failed lines     : {grand_bad}")
    print(f"Output directory : {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
