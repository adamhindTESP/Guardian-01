#!/usr/bin/env python3
import json
from pathlib import Path

OUT = Path("training_data")
OUT.mkdir(exist_ok=True)

SCENARIOS = [
    {
        "plan": {
            "schema_version": "guardian01_action_set_v1",
            "goals": [
                {"action": "stop"},
                {"action": "observe", "target": {"kind": "location", "id": "kitchen_floor"}},
                {"action": "speak", "params": {"text": "Water detected on floor. Slip hazard."}}
            ],
            "parameters": {"target_speed_mps": 0.1}
        },
        "phrases": [
            "There's water on the kitchen floor",
            "The kitchen floor is wet",
            "I spilled water in the kitchen",
            "There's a puddle on the kitchen floor",
            "The floor is slippery in the kitchen"
        ]
    },
    {
        "plan": {
            "schema_version": "guardian01_action_set_v1",
            "goals": [
                {"action": "stop"},
                {"action": "observe", "target": {"kind": "location", "id": "hallway"}},
                {"action": "speak", "params": {"text": "Smoke detected indoors."}},
                {"action": "wait", "params": {"duration_s": 300}}
            ],
            "parameters": {}
        },
        "phrases": [
            "I smell smoke in the hallway",
            "There's smoke inside",
            "Something smells like it's burning indoors",
            "I see smoke in the house",
            "The hallway smells smoky"
        ]
    },
    {
        "plan": {
            "schema_version": "guardian01_action_set_v1",
            "goals": [
                {"action": "stop"},
                {"action": "observe", "target": {"kind": "location", "id": "bathroom"}},
                {"action": "speak", "params": {"text": "Human assistance required."}}
            ],
            "parameters": {}
        },
        "phrases": [
            "Grandma fell in the bathroom",
            "Someone fell down in the bathroom",
            "A person is on the floor in the bathroom",
            "There’s been a fall in the bathroom",
            "Someone collapsed in the bathroom"
        ]
    },
    {
        "plan": {
            "schema_version": "guardian01_action_set_v1",
            "goals": [
                {"action": "stop"},
                {"action": "observe", "target": {"kind": "location", "id": "hallway"}}
            ],
            "parameters": {}
        },
        "phrases": [
            "Something is blocking the hallway",
            "The hallway is blocked",
            "There’s an obstacle in the hallway",
            "I can’t get through the hallway",
            "The hallway path is blocked"
        ]
    },
    {
        "plan": {
            "schema_version": "guardian01_action_set_v1",
            "goals": [
                {"action": "stop"},
                {"action": "observe", "target": {"kind": "location", "id": "living_room"}},
                {"action": "speak", "params": {"text": "Broken glass detected on floor."}}
            ],
            "parameters": {}
        },
        "phrases": [
            "There’s broken glass on the floor",
            "A glass shattered in the living room",
            "Broken glass is on the floor",
            "I dropped a glass and it broke",
            "There are glass shards on the floor"
        ]
    },
    {
        "plan": {
            "schema_version": "guardian01_action_set_v1",
            "goals": [
                {"action": "navigate", "target": {"kind": "location", "id": "charging_station"}},
                {"action": "stop"}
            ],
            "parameters": {"target_speed_mps": 0.12}
        },
        "phrases": [
            "Go charge yourself",
            "Move to the charger",
            "Return to the charging station",
            "You need to recharge",
            "Head to your charging dock"
        ]
    },
    {
        "plan": {
            "schema_version": "guardian01_action_set_v1",
            "goals": [
                {"action": "wait", "params": {"duration_s": 60}}
            ],
            "parameters": {}
        },
        "phrases": [
            "Wait here",
            "Stay where you are",
            "Hold position",
            "Pause for a minute",
            "Don't move"
        ]
    }
]

with open(OUT / "golden_plans_indoor_v1.jsonl", "w", encoding="utf-8") as f:
    for scenario in SCENARIOS:
        for phrase in scenario["phrases"]:
            record = {
                "messages": [
                    {"role": "user", "content": phrase},
                    {"role": "assistant", "content": json.dumps(scenario["plan"])}
                ]
            }
            f.write(json.dumps(record) + "\n")

print("✅ golden_plans_indoor_v1.jsonl generated")
