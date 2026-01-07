import json
from typing import List, Dict
from collections import Counter

from runtime.guardian_validator import GuardianValidator, GuardianViolation


class GuardianEvaluator:
    def __init__(self, planner_callable):
        """
        planner_callable(prompt: str) -> str

        IMPORTANT:
        - The planner returns RAW text output (untrusted).
        - JSON parsing and validation are owned by GuardianValidator.
        """
        self.planner = planner_callable
        self.guardian = GuardianValidator()

        self.results = []
        self.stats = Counter()

    def evaluate_prompt(self, prompt: str, prompt_id: int):
        """
        Run one prompt through:
        Planner (untrusted) → GuardianValidator (authority)
        """
        try:
            # 🔹 Planner returns raw text (NOT parsed JSON)
            plan_output = self.planner(prompt)

            # 🔹 Guardian owns parsing + validation + veto
            self.guardian.validate_plan(plan_output)

            self.results.append({
                "id": prompt_id,
                "prompt": prompt,
                "result": "PASS",
                "gate": None,
                "reason": None
            })
            self.stats["PASS"] += 1

        except GuardianViolation as gv:
            self.results.append({
                "id": prompt_id,
                "prompt": prompt,
                "result": "VETO",
                "gate": gv.gate,
                "reason": gv.message
            })
            self.stats["VETO"] += 1
            self.stats[f"VETO_{gv.gate}"] += 1

        except Exception as e:
            self.results.append({
                "id": prompt_id,
                "prompt": prompt,
                "result": "ERROR",
                "gate": "INTERNAL_ERROR",
                "reason": str(e)
            })
            self.stats["ERROR"] += 1

    def run(self, prompts: List[str]) -> Dict:
        """
        Evaluate a list of prompts.
        """
        for i, prompt in enumerate(prompts):
            self.evaluate_prompt(prompt, i)

        total = len(prompts)

        summary = {
            "total": total,
            "pass_rate": self.stats["PASS"] / total if total else 0.0,
            "veto_rate": self.stats["VETO"] / total if total else 0.0,
            "error_rate": self.stats["ERROR"] / total if total else 0.0,
            "counts": dict(self.stats)
        }

        return summary

    def export_results(self, path: str):
        """
        Save detailed results for audit / paper appendix.
        """
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2)
