#!/usr/bin/env python3
"""
normalize_with_semantics.py — Structural normalization WITH semantic preservation

Purpose:
- Convert raw validated Guardian chunks into a semantically annotated substrate
- Preserve contextual meaning of overloaded actions (especially 'stop')
- Produce Guardian Seed v1 candidate dataset

Output:
- guardian_semantic_normalized.json
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# ============================================================================
# SEMANTIC CONFIGURATION
# ============================================================================

STOP_SEMANTICS = {
    "emergency_halt": {
        "categories": ["medical_emergency", "fire_hazard", "human_safety_emergency"],
        "priority": "highest",
        "requires_override": True,
        "max_speed_after_stop_mps": 0.0,
    },
    "prudent_pause": {
        "categories": [
            "night_low_light",
            "partial_sensor_degradation",
            "sensor_conflict_resolution",
            "multiple_humans_pets",
        ],
        "priority": "medium",
        "requires_override": False,
        "max_speed_after_stop_mps": 0.15,
    },
    "procedural_pause": {
        "categories": [
            "multi_room_inspection",
            "task_progress_reporting",
            "energy_efficient_path",
            "complex_multi_step",
        ],
        "priority": "low",
        "requires_override": False,
        "max_speed_after_stop_mps": 0.25,
    },
    "safety_boundary": {
        "categories": [
            "forbidden_zone_boundary",
            "slippery_surface_response",
            "wildlife_encounter",
            "electrical_hazard_caution",
        ],
        "priority": "high",
        "requires_override": True,
        "max_speed_after_stop_mps": 0.0,
    },
}

EMERGENCY_KEYWORDS = [
    "emergency",
    "hazard",
    "critical",
    "fire",
    "medical",
    "accident",
    "seizure",
    "fall",
]

# ============================================================================
# HELPERS
# ============================================================================

def create_record_id(chunk_id: str, category: str, payload: str) -> str:
    h = hashlib.md5(payload.encode()).hexdigest()[:6]
    return f"{chunk_id}_{category}_{h}"

def interpret_stop(category: str, params: Dict) -> Dict[str, Any]:
    cat = category.lower()

    for semantic, cfg in STOP_SEMANTICS.items():
        if any(cat == c or cat.startswith(c + "_") for c in cfg["categories"]):
            return {
                "type": "stop",
                "semantic_interpretation": semantic,
                "priority": cfg["priority"],
                "requires_human_override": cfg["requires_override"],
                "max_resume_speed_mps": cfg["max_speed_after_stop_mps"],
            }

    if any(k in cat for k in EMERGENCY_KEYWORDS):
        return {
            "type": "stop",
            "semantic_interpretation": "emergency_halt",
            "priority": "highest",
            "requires_human_override": True,
            "max_resume_speed_mps": 0.0,
        }

    if params.get("target_speed_mps", 0.0) == 0.0 and params.get("max_force_n", 0.0) == 0.0:
        return {
            "type": "stop",
            "semantic_interpretation": "safety_boundary",
            "priority": "high",
            "requires_human_override": True,
            "max_resume_speed_mps": 0.0,
        }

    return {
        "type": "stop",
        "semantic_interpretation": "procedural_pause",
        "priority": "low",
        "requires_human_override": False,
        "max_resume_speed_mps": 0.25,
    }

def derive_limits(params: Dict, category: str, goals: List[Dict]) -> Dict[str, Any]:
    limits = {
        "speed_mps": params.get("target_speed_mps", 0.0),
        "force_n": params.get("max_force_n", 0.0),
        "contextual_bounds": {},
    }

    if any(g.get("action") in ("grasp", "manipulate") for g in goals):
        limits["contextual_bounds"]["manipulation_context"] = True
        limits["contextual_bounds"]["requires_pre_observation"] = True

    cat = category.lower()
    if any(k in cat for k in EMERGENCY_KEYWORDS):
        limits["contextual_bounds"]["emergency_context"] = True
        limits["contextual_bounds"]["requires_human_acknowledgment"] = True
        limits["contextual_bounds"]["emergency_speed_cap_mps"] = min(
            limits["speed_mps"], 0.3
        )

    if any(k in cat for k in ["night", "dark", "low_light", "glare"]):
        limits["contextual_bounds"]["impaired_visibility"] = True
        limits["contextual_bounds"]["max_speed_override_mps"] = min(
            limits["speed_mps"], 0.2
        )

    return limits

def derive_tags(category: str, goals: List[Dict], params: Dict) -> List[str]:
    tags = set()
    tags.add(category)

    for g in goals:
        if "action" in g:
            tags.add(f"action:{g['action']}")

    cat = category.lower()
    if any(k in cat for k in EMERGENCY_KEYWORDS):
        tags.add("safety:emergency")

    if params.get("target_speed_mps", 0) < 0.1:
        tags.add("motion:slow")
    elif params.get("target_speed_mps", 0) < 0.25:
        tags.add("motion:moderate")
    else:
        tags.add("motion:fast")

    return sorted(tags)

# ============================================================================
# NORMALIZATION
# ============================================================================

def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    goals = record["goals"]
    params = record.get("parameters", {})
    category = record["category"]
    chunk_id = record.get("chunk_id") or record.get("_chunk_id", "unknown")

    payload = json.dumps(record, sort_keys=True)
    record_id = create_record_id(chunk_id, category, payload)

    plan = []
    for g in goals:
        if g["action"] == "stop":
            a = interpret_stop(category, params)
        else:
            a = {
                "type": g["action"],
                "semantic_interpretation": "standard_action",
                "priority": "normal",
            }

        if "target" in g:
            a["target"] = g["target"]
        if "duration_s" in g:
            a["duration_s"] = g["duration_s"]
        if "text" in g:
            a["text"] = g["text"]

        a["_original"] = g
        plan.append(a)

    return {
        "schema": "guardian_semantic_v1",
        "id": record_id,
        "chunk_id": chunk_id,
        "category": category,
        "plan": plan,
        "limits": derive_limits(params, category, goals),
        "semantic_tags": derive_tags(category, goals, params),
        "original": {
            "goals": goals,
            "parameters": params,
        },
        "normalization_timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0",
    }

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("guardian_semantic_normalized.json"))
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        raw = json.load(f)

    records = raw if isinstance(raw, list) else raw["records"]
    normalized = [normalize_record(r) for r in records]

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2, ensure_ascii=False)

    print(f"✅ Normalized {len(normalized)} records → {args.output}")

if __name__ == "__main__":
    main()
