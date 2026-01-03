#!/usr/bin/env python3
"""
Guardian Seed — Training Dataset Validator (v1.0)

Validates Guardian action-set training datasets.

Supports:
- Multi-chunk datasets (list of chunks)
- Single-chunk datasets (dict)
- Normalized datasets

This validator checks STRUCTURE, not behavior.
"""

import json
import sys
from typing import Any


REQUIRED_CHUNK_FIELDS = {
    "chunk_id": str,
    "schema_version": str,
    "policy": str,
    "records": list,
}

REQUIRED_RECORD_FIELDS = {
    "category": str,
    "goals": list,
}

ALLOWED_GOAL_FIELDS = {"action", "target", "text"}


def error(msg: str):
    raise ValueError(msg)


def load_dataset(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_goal(goal: dict, chunk_id: str, record_idx: int, goal_idx: int):
    if not isinstance(goal, dict):
        error(f"[{chunk_id}] Record {record_idx} Goal {goal_idx} is not an object")

    if "action" not in goal:
        error(f"[{chunk_id}] Record {record_idx} Goal {goal_idx} missing 'action'")

    if not isinstance(goal["action"], str):
        error(f"[{chunk_id}] Record {record_idx} Goal {goal_idx} 'action' must be string")

    for key in goal.keys():
        if key not in ALLOWED_GOAL_FIELDS:
            error(
                f"[{chunk_id}] Record {record_idx} Goal {goal_idx} "
                f"contains unknown field '{key}'"
            )


def validate_record(record: dict, chunk_id: str, record_idx: int):
    if not isinstance(record, dict):
        error(f"[{chunk_id}] Record {record_idx} is not an object")

    for field, field_type in REQUIRED_RECORD_FIELDS.items():
        if field not in record:
            error(f"[{chunk_id}] Record {record_idx} missing '{field}'")
        if not isinstance(record[field], field_type):
            error(
                f"[{chunk_id}] Record {record_idx} '{field}' must be {field_type.__name__}"
            )

    goals = record["goals"]
    if not goals:
        error(f"[{chunk_id}] Record {record_idx} has empty goals list")

    for g_idx, goal in enumerate(goals):
        validate_goal(goal, chunk_id, record_idx, g_idx)


def validate_chunk(chunk: dict, index: int):
    if not isinstance(chunk, dict):
        error(f"Chunk {index} is not an object")

    for field, field_type in REQUIRED_CHUNK_FIELDS.items():
        if field not in chunk:
            error(f"Chunk {index} missing '{field}'")
        if not isinstance(chunk[field], field_type):
            error(
                f"Chunk {index} field '{field}' must be {field_type.__name__}"
            )

    chunk_id = chunk["chunk_id"]
    records = chunk["records"]

    if not records:
        error(f"[{chunk_id}] has empty records list")

    for r_idx, record in enumerate(records):
        validate_record(record, chunk_id, r_idx)


def main():
    if len(sys.argv) < 2:
        dataset_path = "guardian_normalized.json"
    else:
        dataset_path = sys.argv[1]

    dataset = load_dataset(dataset_path)

    # Normalize root to list
    if isinstance(dataset, list):
        chunks = dataset
    elif isinstance(dataset, dict):
        chunks = [dataset]
    else:
        error("Dataset root must be list or object")

    print(f"Loaded dataset with {len(chunks)} chunk(s)")

    for idx, chunk in enumerate(chunks):
        validate_chunk(chunk, idx)
        print(f"✓ Validated chunk {chunk.get('chunk_id', idx)}")

    print("✔ Dataset validation PASSED")


if __name__ == "__main__":
    main()
