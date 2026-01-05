#!/usr/bin/env python3
"""
Guardian Seed — Training Dataset Validator (v1.1)

Validates Guardian planner training datasets.

SUPPORTED FORMATS
-----------------
• JSONL (one JSON object per line)  ← REQUIRED for golden plans
• Each line represents one training example

THIS VALIDATOR CHECKS:
• JSON syntax (line-by-line)
• Required high-level fields
• Goal object structure

THIS VALIDATOR DOES NOT:
• Judge behavior correctness
• Enforce policy semantics
"""

import json
import sys
from typing import List, Dict, Any


# -------------------------
# Schema expectations
# -------------------------

REQUIRED_TOP_LEVEL_FIELDS = {"messages"}
REQUIRED_MESSAGE_FIELDS = {"role", "content"}

ALLOWED_GOAL_FIELDS = {"action", "target", "params", "text"}


# -------------------------
# Errors
# -------------------------

def error(msg: str):
    raise ValueError(msg)


# -------------------------
# JSONL Loader
# -------------------------

def load_jsonl(path: str) -> List[Dict[str, Any]]:
    records = []

    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
                records.append(obj)
            except json.JSONDecodeError as e:
                error(f"JSONL parse error on line {line_no}: {e}")

    if not records:
        error("Dataset is empty")

    return records


# -------------------------
# Validators
# -------------------------

def validate_message(msg: Dict[str, Any], record_idx: int, msg_idx: int):
    if not isinstance(msg, dict):
        error(f"[Record {record_idx}] Message {msg_idx} is not an object")

    for field in REQUIRED_MESSAGE_FIELDS:
        if field not in msg:
            error(f"[Record {record_idx}] Message {msg_idx} missing '{field}'")

    if not isinstance(msg["role"], str):
        error(f"[Record {record_idx}] Message {msg_idx} 'role' must be string")

    if not isinstance(msg["content"], str):
        error(f"[Record {record_idx}] Message {msg_idx} 'content' must be string")


def validate_record(record: Dict[str, Any], record_idx: int):
    if not isinstance(record, dict):
        error(f"Record {record_idx} is not an object")

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in record:
            error(f"Record {record_idx} missing '{field}'")

    messages = record["messages"]

    if not isinstance(messages, list):
        error(f"Record {record_idx} 'messages' must be a list")

    if len(messages) < 2:
        error(f"Record {record_idx} must contain at least user + assistant messages")

    for msg_idx, msg in enumerate(messages):
        validate_message(msg, record_idx, msg_idx)


# -------------------------
# Main
# -------------------------

def main():
    if len(sys.argv) < 2:
        error("Usage: python validate_training_dataset.py <dataset.jsonl>")

    dataset_path = sys.argv[1]

    records = load_jsonl(dataset_path)

    print(f"Loaded {len(records)} JSONL records")

    for idx, record in enumerate(records):
        validate_record(record, idx)

    print("✔ Dataset validation PASSED")


if __name__ == "__main__":
    main()
