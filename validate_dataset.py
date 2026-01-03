#!/usr/bin/env python3
"""
validate_dataset.py — Offline training dataset validator (PRE-TRAIN GATE)

Purpose:
- Statistically validate training data BEFORE training
- Enforce guardian01_action_set_v1 strictly
- Catch schema drift, sequencing errors, forbidden semantics
- Fail fast on first violation

This validator:
❌ does NOT compute risk from sensors
❌ does NOT allow defaults to hide errors
✅ must PASS 100% before training is allowed
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

from validator_v1 import (
    GuardianValidatorV1,
    ValidationError,
    SCHEMA_VERSION
)

# -------------------------
# Configuration
# -------------------------

STRICT_MODE = True   # no silent fixes
DUMMY_SENSORS = {
    "front_cm": 100  # benign, far distance
}

# -------------------------
# Dataset Loader
# -------------------------

def load_json(path: Path) -> Any:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load {path}: {e}")

# -------------------------
# Record Extraction
# -------------------------

def extract_records(data: Any) -> List[Dict[str, Any]]:
    """
    Supports:
    - chunk format {chunk_id, records:[...]}
    - flat list [{category, goals, parameters}, ...]
    """
    if isinstance(data, dict) and "records" in data:
        return data["records"]

    if isinstance(data, list):
        return data

    raise ValidationError("Unrecognized dataset format")

# -------------------------
# Record Validation
# -------------------------

def validate_record(
    record: Dict[str, Any],
    validator: GuardianValidatorV1,
    source: str,
    index: int
) -> None:

    if "goals" not in record:
        raise ValidationError("Missing goals")

    plan = {
        "schema_version": SCHEMA_VERSION,
        "goals": record["goals"],
        "parameters": record.get("parameters", {})
    }

    # IMPORTANT:
    # Dataset must be validator-clean WITHOUT sensor dependence
    validator.validate(
        llm_output=json.dumps(plan),
        sensor_data=DUMMY_SENSORS
    )

# -------------------------
# File Validation
# -------------------------

def validate_file(path: Path, validator: GuardianValidatorV1) -> None:
    data = load_json(path)
    records = extract_records(data)

    if not records:
        raise ValidationError("No records found")

    for i, record in enumerate(records):
        try:
            validate_record(record, validator, path.name, i)
        except ValidationError as e:
            raise ValidationError(
                f"\n❌ DATASET VIOLATION\n"
                f"File: {path}\n"
                f"Record #: {i}\n"
                f"Category: {record.get('category')}\n"
                f"Error: {e}\n"
            )

# -------------------------
# Entry Point
# -------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: validate_dataset.py <dataset.json> [dataset2.json ...]")
        sys.exit(1)

    validator = GuardianValidatorV1()
    failures = 0

    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"❌ File not found: {path}")
            failures += 1
            continue

        try:
            validate_file(path, validator)
            print(f"✅ PASS: {path}")
        except ValidationError as e:
            print(str(e))
            failures += 1

    if failures > 0:
        print(f"\n❌ DATASET VALIDATION FAILED ({failures} file(s))")
        sys.exit(2)

    print("\n🟢 ALL DATASETS PASSED — SAFE TO TRAIN")
    sys.exit(0)

if __name__ == "__main__":
    main()
