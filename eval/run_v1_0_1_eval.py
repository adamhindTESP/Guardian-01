import json
from runtime.guardian_validator import GuardianValidator, GuardianViolation
from pathlib import Path

PLANS_PATH = Path("training_data/golden_plans.jsonl")

def main():
    validator = GuardianValidator()

    with open(PLANS_PATH, "r") as f:
        plans = json.load(f)

    results = []

    for i, plan in enumerate(plans):
        try:
            validator.validate_plan(json.dumps(plan))
            results.append((i, "PASS"))
        except GuardianViolation as gv:
            results.append((i, f"VETO {gv.gate}: {gv.message}"))

    for r in results:
        print(r)

if __name__ == "__main__":
    main()
