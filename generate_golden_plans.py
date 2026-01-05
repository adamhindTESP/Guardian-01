#!/usr/bin/env python3
import json

DATA = [
    ("There's a water spill in the kitchen", {
        "schema_version": "guardian01_action_set_v1",
        "goals": [
            {"action": "observe", "target": {"kind": "location", "id": "kitchen_floor"}},
            {"action": "stop"},
            {"action": "speak", "params": {"text": "Hazard detected."}}
        ],
        "parameters": {"target_speed_mps": 0.1}
    }),
    ("Pick up the glass from the table", {
        "schema_version": "guardian01_action_set_v1",
        "goals": [
            {"action": "observe", "target": {"kind": "object", "id": "glass"}},
            {"action": "grasp", "target": {"kind": "object", "id": "glass"}}
        ],
        "parameters": {"max_force_n": 0.4}
    }),
    ("I smell smoke in the hallway", {
        "schema_version": "guardian01_action_set_v1",
        "goals": [
            {"action": "stop"},
            {"action": "observe", "target": {"kind": "location", "id": "hallway"}},
            {"action": "speak", "params": {"text": "Smoke detected."}},
            {"action": "wait", "params": {"duration_s": 300}}
        ],
        "parameters": {}
    }),
]

with open("training_data/golden_plans.jsonl", "w", encoding="utf-8") as f:
    for user, assistant in DATA:
        record = {
            "messages": [
                {"role": "user", "content": user},
                {"role": "assistant", "content": json.dumps(assistant)}
            ]
        }
        f.write(json.dumps(record) + "\n")

print("✅ golden_plans.jsonl written safely")
