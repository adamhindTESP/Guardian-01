#!/usr/bin/env python3
"""
Guardian-01 v1.0.1 Evaluation Harness (NON-CERTIFYING)

- Reads JSONL datasets from training_data/
- Extracts assistant plan JSON (string)
- Validates plan using runtime GuardianValidator (G1)
- Reports overall + per-category pass/fail

NOTE:
This file is evaluation-only. It has NO execution authority and does not
modify any frozen gate artifacts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Frozen enforcement kernel (DO NOT MODIFY)
from runtime.guardian_validator import GuardianValidator, GuardianViolation  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "training_data"

# Default: evaluate everything in training_data/*.jsonl
DEFAULT_GLOBS = ["*.jsonl"]

# If your assistant content is a JSON string, we parse it.
# If it’s already a dict, we use it directly.
def _parse_plan_from_assistant_content(content: Any) -> Dict[str, Any]:
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        content = content.strip()
        # Sometimes content is already JSON; sometimes it’s wrapped as a JSON-encoded string.
        # First attempt: parse directly.
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
            # If parsed is not dict, fall through to error
        except json.JSONDecodeError:
            pass
    raise ValueError("Assistant content did not contain a JSON object plan")

def _extract_messages(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    msgs = record.get("messages")
    if not isinstance(msgs, list):
        raise ValueError("Record missing 'messages' list")
    return msgs

def _assistant_content_from_messages(msgs: List[Dict[str, Any]]) -> Any:
    # Find last assistant message (common pattern)
    for m in reversed(msgs):
        if m.get("role") == "assistant":
            return m.get("content")
    raise ValueError("No assistant message found in record")

def _category_from_record(record: Dict[str, Any]) -> str:
    cat = record.get("category")
    if isinstance(cat, str) and cat.strip():
        return cat.strip()
    return "uncategorized"

@dataclass
class Stat:
    total: int = 0
    passed: int = 0
    failed: int = 0

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
                raise ValueError(f"{path.name}:{line_no} invalid JSONL line: {e}") from e
    return out

def resolve_input_files(globs: List[str]) -> List[Path]:
    files: List[Path] = []
    for g in globs:
        files.extend(sorted(DATA_DIR.glob(g)))
    # Deduplicate while preserving order
    seen = set()
    uniq: List[Path] = []
    for p in files:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq

def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--glob",
        action="append",
        default=None,
        help="Glob(s) under training_data/ to evaluate (repeatable). Default: *.jsonl",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional max number of records to evaluate (0 = no limit).",
    )
    args = ap.parse_args(argv)

    globs = args.glob if args.glob else DEFAULT_GLOBS
    files = resolve_input_files(globs)

    print("Guardian-01 v1.0.1 Evaluation (NON-CERTIFYING)")
    print(f"Repo root: {REPO_ROOT}")
    print(f"Data dir : {DATA_DIR}")
    print(f"Globs    : {globs}")
    print(f"Files    : {len(files)}")
    for p in files:
        print(f"  - {p.relative_to(REPO_ROOT)}")

    validator = GuardianValidator()

    overall = Stat()
    by_cat: Dict[str, Stat] = {}
    violations: List[Tuple[str, str, str]] = []  # (category, file:line, message)

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
                msgs = _extract_messages(rec)
                assistant_content = _assistant_content_from_messages(msgs)
                plan_obj = _parse_plan_from_assistant_content(assistant_content)

                # Validate expects JSON string (per your current validator call style)
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
        print(f"{cat:24s} total={st.total:4d} pass={st.passed:4d} fail={st.failed:4d} pass%={pct:6.1f}")

    print("\n=== Sample Violations (first 25) ===")
    for cat, where, msg in violations[:25]:
        print(f"[{cat}] {where}: {msg}")

    print("\nEvaluation complete.")
    return 0 if overall.failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
