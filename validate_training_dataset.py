#!/usr/bin/env python3
"""
Guardian Seed — Training Dataset Validator (v1.1)

Supports:
- Phase 2 normalized datasets (chunk-based JSON)
- Phase 3 training datasets (JSONL, chat-based)

This validator checks STRUCTURE, not behavior.
"""

import json
import sys
from typing import Any


# ---------- Phase 2 (legacy) rules ----------

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

ALLOWED_GOAL_FIELDS = {"action", "target", "params", "text"}


# ---------- Helpers ----------

def error(msg: str):
    raise ValueError(msg)


# ---------- Phase 3 (JSONL) support ----------

def load_jsonl(path: str):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                error(f"JSONL parse error on line {line_no}: {e}")
    return records


def validate_jsonl_example(example: dict, index: int):
    if "messages" not in example:
        error(f"[Line {index}] Missing 'messages'")

    messages = example["messages"]
    if not isinstance(messages, list) or len(messages) < 2:
        error(f"[Line {index}] 'messages' must be a list with user+assistant")

    if messages[0].get("role") != "user":
        error(f"[Line {index}] First message must be role=user")

    if messages[1].get("role") != "assistant":
        error(f"[Line {index}] Second message must be role=assistant")

    content = messages[1].get("content")
    if not isinstance(content, str):
        error(f"[Line {index}] Assistant content must be stringified JSON")

    try:
        plan = json.loads(content)
    except json.JSONDecodeError as e:
        error(f"[Line {index}] Assistant content is invalid JSON: {e}")

    # Minimal contract checks
    if "schema_version" not in plan:
        error(f"[Line {index}] Missing 'schema_version'")

    if "goals" not in plan or not isinstance(plan["goals"], list):
        error(f"[Line {index}] Missing or invalid 'goals'")

    if "parameters" not in plan or not isinstance(plan["parameters"], dict):
        error(f"[Line {index}] Missing or invalid 'parameters'")


# ---------- Phase 2 validation (unchanged) ----------

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


# ---------- Main ----------

def main():
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "guardian_normalized.json"

    if dataset_path.endswith(".jsonl"):
        dataset = load_jsonl(dataset_path)
        print(f"Loaded JSONL dataset with {len(dataset)} examples")

        for i, example in enumerate(dataset, 1):
            validate_jsonl_example(example, i)

        print("✔ JSONL training dataset validation PASSED")
        return

    # Legacy JSON path
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    chunks = dataset if isinstance(dataset, list) else [dataset]

    print(f"Loaded dataset with {len(chunks)} chunk(s)")

    for idx, chunk in enumerate(chunks):
        validate_chunk(chunk, idx)
        print(f"✓ Validated chunk {chunk.get('chunk_id', idx)}")

    print("✔ Dataset validation PASSED")


if __name__ == "__main__":
    main()
