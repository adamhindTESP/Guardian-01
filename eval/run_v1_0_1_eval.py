#!/usr/bin/env python3
"""
Guardian-01 — v1.0.1 Evaluation Runner (FIXED)

Reads golden plans from training_data/golden_plans.jsonl
Validates each plan with GuardianValidator
Reports pass/fail counts and violations
"""

import json
from pathlib import Path

from runtime.guardian_validator import GuardianValidator, GuardianViolation


# --- Paths (repo-root relative) ---
REPO_ROOT = Path(__file__).resolve().parents[1]
PLANS_PATH = REPO_ROOT / "training_data" / "golden_plans.jsonl"


def load_jsonl(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing plans file: {path}")

    plans = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                plans.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no}: {e}") from e
    return plans


def main():
    print("Guardian-01 v1.0.1 Evaluation")
    print(f"Loading plans from: {PLANS_PATH}")

    plans = load_jsonl(PLANS_PATH)
    print(f"Loaded {len(plans)} plans\n")

    validator = GuardianValidator()

    passed = 0
    failed = 0
    violations = []

    for i, plan in enumerate(plans, start=1):
        try:
            validator.validate_plan(json.dumps(plan))
            passed += 1
        except GuardianViolation as gv:
            failed += 1
            violations.append((i, str(gv)))

    print("=== Evaluation Results ===")
    print(f"Total plans : {len(plans)}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")

    if violations:
        print("\n=== Violations ===")
        for idx, msg in violations:
            print(f"[Plan {idx}] {msg}")

    print("\nEvaluation complete.")


if __name__ == "__main__":
    main()
