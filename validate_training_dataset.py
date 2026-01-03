#!/usr/bin/env python3
"""
validate_training_dataset.py

Validates Guardian training datasets against validator_v1.py.
FAIL FAST: stops on first invalid record.
"""

import json
from validator_v1 import GuardianValidatorV1, ValidationError

DATASET_FILE = "guardian_normalized.json"

def main():
    with open(DATASET_FILE, "r") as f:
        dataset = json.load(f)

    schema_version = dataset.get("schema_version")
    records = dataset.get("records")

    if not records:
        raise RuntimeError("No records found in dataset")

    validator = GuardianValidatorV1()

    # Dummy conservative sensor input (safe default)
    dummy_sensors = {
        "front_cm": 100,
        "human_near": False
    }

    for i, record in enumerate(records):
        try:
            plan = {
                "schema_version": schema_version,
                "goals": record["goals"],
                "parameters": record.get("parameters", {})
            }

            validator.validate(
                llm_output=json.dumps(plan),
                sensor_data=dummy_sensors
            )

        except ValidationError as e:
            print(f"\n❌ DATASET FAIL")
            print(f"Record #{i}")
            print(f"Category: {record.get('category')}")
            print(f"Error: {e}")
            return

    print("\n✅ DATASET PASS — ALL RECORDS VALID")

if __name__ == "__main__":
    main()
