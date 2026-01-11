#!/usr/bin/env python3
"""
Guardian-01 v1.0.1 Evaluation Harness (NON-CERTIFYING)

- Reads JSONL datasets from training_data/
- Accepts BOTH:
    • Chat-style records with messages[]
    • Direct schema-level plans: {"actions":[...]}
- Validates plans using frozen GuardianValidator (G1)
- Reports overall + per-category pass/fail

⚠️ Evaluation-only. NO execution authority.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ❄️ Frozen enforcement kernel (DO NOT MODIFY)
from runtime.guardian_validator import GuardianValidator, GuardianViolation  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "training_data"
DEFAULT_GLOBS = ["*.jsonl"]

# -------------------------
# Parsing helpers
# -------------------------

def _parse_plan_from_assistant_content(content: Any) -> Dict[str, Any]:
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        content = content.strip()
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    raise ValueError("Assistant content did not contain a JSON object plan")

def _extract_messages(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    msgs = record.get("messages")
    if not isinstance(msgs, list):
        raise ValueError("Record missing 'messages' list")
    return msgs

def _assistant_content_from_messages(msgs: List[Dict[str, Any]]) -> Any:
    for m in reversed(msgs):
        if m.get("role") == "assistant":
            return m.get("content")
    raise ValueError("No assistant message found")

def _extract_plan_from_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepts either:
    1) Direct schema-level plan: {"actions":[...]}
    2) Chat-style record with messages[]
    """
    # Case 1 — already schema-valid
    if "actions" in record and isinstance(record["actions"], list):
        return record

    # Case 2 — chat-style wrapper
    msgs = _extract_messages(record)
    assistant_content = _assistant_content_from_messages(msgs)
    return _parse_plan_from_assistant_content(assistant_content)

def _category_from_record(record: Dict[str, Any]) -> str:
    cat = record.get("category")
    return cat.strip() if isinstance(cat, str) and cat.strip() else "uncategorized"

# -------------------------
# Stats
# -------------------------

@dataclass
class Stat:
    total: int = 0
    passed: int = 0
    failed: int = 0

# -------------------------
# IO helpers
# -------------------------

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"{path.name}:{line_no} invalid JSON: {e}") from e
    return out

def resolve_input_files(globs: List[str]) -> List[Path]:
    files: List[Path] = []
    for g in globs:
        files.extend(sorted(DATA_DIR.glob(g)))
    seen = set()
    uniq: List[Path] = []
    for p in files:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq

# -------------------------
# Main
# -------------------------

def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", action="append", default=None,
                    help="Glob(s) under training_data/ (repeatable)")
    ap.add_argument("--limit", type=int, default=0,
                    help="Max records to evaluate (0 = all)")
    args = ap.parse_args(argv)

    globs = args.glob if args.glob else DEFAULT_GLOBS
    files = resolve_input_files(globs)

    print("Guardian-01 v1.0.1 Evaluation (NON-CERTIFYING)")
    print(f"Repo root : {REPO_ROOT}")
    print(f"Data dir  : {DATA_DIR}")
    print(f"Globs     : {globs}")
    print(f"Files     : {len(files)}")
    for f in files:
        print(f"  - {f.relative_to(REPO_ROOT)}")

    validator = GuardianValidator()

    overall = Stat()
    by_cat: Dict[str, Stat] = {}
    violations: List[Tuple[str, str, str]] = []

    evaluated = 0

    for fp in files:
        records = load_jsonl(fp)
        for idx, rec in enumerate(records, start=1):
            if args.limit and evaluated >= args.limit:
                break

            evaluated += 1
            cat = _category_from_record(rec)
            by_cat.setdefault(cat, Stat())

            overall.total += 1
            by_cat[cat].total += 1

            try:
                plan_obj = _extract_plan_from_record(rec)
                validator.validate_plan(json.dumps(plan_obj))
                overall.passed += 1
                by_cat[cat].passed += 1

            except (GuardianViolation, Exception) as e:
                overall.failed += 1
                by_cat[cat].failed += 1
                violations.append((cat, f"{fp.name}:{idx}", str(e)))

        if args.limit and evaluated >= args.limit:
            break

    print("\n=== Evaluation Results ===")
    print(f"Total records : {overall.total}")
    print(f"Passed        : {overall.passed}")
    print(f"Failed        : {overall.failed}")

    print("\n=== By Category ===")
    for cat, st in sorted(by_cat.items(), key=lambda kv: (-kv[1].failed, kv[0])):
        pct = (100.0 * st.passed / st.total) if st.total else 0.0
        print(f"{cat:24s} total={st.total:4d} pass={st.passed:4d} "
              f"fail={st.failed:4d} pass%={pct:6.1f}")

    print("\n=== Sample Violations (first 25) ===")
    for cat, where, msg in violations[:25]:
        print(f"[{cat}] {where}: {msg}")

    print("\nEvaluation complete.")
    return 0 if overall.failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
