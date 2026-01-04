#!/usr/bin/env python3
"""
generate_planner_training_data.py

Converts Guardian Seed v1 (semantic, audited) into
planner training data (instruction → safe JSON).

Output:
training_data/
├── train.json
├── val.json
└── test.json
"""

import json
import random
from pathlib import Path
from typing import Dict, Any, List

RANDOM_SEED = 42
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15

random.seed(RANDOM_SEED)

# ---------------------------------------------------------------------
# Conversion logic
# ---------------------------------------------------------------------

def record_to_training_example(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert one Guardian Seed record into an instruction/response example.
    """

    category = record["category"]

    # Simple, neutral scenario text
    scenario_text = (
        f"Scenario category: {category.replace('_', ' ')}.\n"
        "Plan the safest possible action sequence."
    )

    limits = record["limits"]
    plan = record["plan"]

    # Strip training output down to ONLY what the planner should learn
    safe_plan = {
        "plan": [
            {k: v for k, v in step.items() if k != "_original"}
            for step in plan
        ],
        "limits": {
            "speed_mps": limits["speed_mps"],
            "force_n": limits["force_n"],
        },
    }

    instruction = (
        "You are an autonomous agent planner.\n"
        "You must propose an action plan that respects strict safety limits.\n\n"
        f"{scenario_text}\n\n"
        "Respond ONLY with valid JSON."
    )

    return {
        "messages": [
            {"role": "system", "content": "You are a safety-first planner."},
            {"role": "user", "content": instruction},
            {
                "role": "assistant",
                "content": json.dumps(safe_plan, indent=2),
            },
        ],
        "metadata": {
            "id": record["id"],
            "category": category,
            "version": record.get("version", "1.0"),
        },
    }


# ---------------------------------------------------------------------
# Dataset split
# ---------------------------------------------------------------------

def split_dataset(data: List[Dict[str, Any]]):
    random.shuffle(data)
    n = len(data)

    n_train = int(n * TRAIN_RATIO)
    n_val = int(n * VAL_RATIO)

    train = data[:n_train]
    val = data[n_train : n_train + n_val]
    test = data[n_train + n_val :]

    return train, val, test


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    seed_path = Path("guardian_semantic_normalized.json")
    output_dir = Path("training_data")

    if not seed_path.exists():
        raise FileNotFoundError(f"Missing {seed_path}")

    with seed_path.open("r", encoding="utf-8") as f:
        seed_records = json.load(f)

    print(f"📥 Loaded {len(seed_records)} Guardian Seed records")

    training_examples = [
        record_to_training_example(r) for r in seed_records
    ]

    train, val, test = split_dataset(training_examples)

    output_dir.mkdir(exist_ok=True)

    for name, split in [
        ("train.json", train),
        ("val.json", val),
        ("test.json", test),
    ]:
        path = output_dir / name
        with path.open("w", encoding="utf-8") as f:
            json.dump(split, f, indent=2)
        print(f"💾 Wrote {len(split)} → {path}")

    print("\n✅ Planner training data ready")
    print(f"Train / Val / Test = {len(train)} / {len(val)} / {len(test)}")


if __name__ == "__main__":
    main()
