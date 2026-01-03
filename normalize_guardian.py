import json

def normalize_record(chunk_id, idx, record):
    plan = []
    for g in record["goals"]:
        plan.append({
            "type": g["action"],
            "target": g.get("target", {"kind": "none", "id": None}),
            "text": g.get("text"),
            "duration_s": g.get("duration_s")
        })

    params = record.get("parameters", {})

    return {
        "schema": "guardian_action_v2",
        "id": f"{chunk_id}_{record['category']}_{idx:03d}",
        "category": record["category"],
        "context": record.get("context", {}),
        "plan": plan,
        "limits": {
            "speed_mps": params.get("target_speed_mps", 0.0),
            "force_n": params.get("max_force_n", 0.0),
            "step_distance_m": params.get("step_distance_m"),
            "reobserve_s": params.get("reobservation_s")
        }
    }

def normalize_dataset(chunks):
    out = []
    for chunk in chunks:
        cid = chunk["chunk_id"]
        for i, rec in enumerate(chunk["records"]):
            out.append(normalize_record(cid, i, rec))
    return out

if __name__ == "__main__":
    with open("raw_dataset.json", "r") as f:
        chunks = json.load(f)

    normalized = normalize_dataset(chunks)

    with open("guardian_normalized.json", "w") as f:
        json.dump(normalized, f, indent=2)

    print(f"Done. Normalized {len(normalized)} records.")
