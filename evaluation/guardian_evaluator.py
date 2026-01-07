import json
from typing import List, Dict
from collections import Counter

from runtime.guardian_validator import GuardianValidator, GuardianViolation


class GuardianEvaluator:
    def __init__(self, planner_callable):
        """
        planner_callable(prompt: str) -> dict
        """
        self.planner = planner_callable
        self.guardian = GuardianValidator()

        self.results = []
        self.stats = Counter()

    def evaluate_prompt(self, prompt: str, prompt_id: int):
        """
        Run one prompt through planner → guardian.
        """
        try:
            plan = self.planner(prompt)

            self.guardian.validate_plan(plan)

            self.results.append({
                "id": prompt_id,
                "prompt": prompt,
                "result": "PASS",
                "reason": None
            })
            self.stats["PASS"] += 1

        except GuardianViolation as gv:
            self.results.append({
                "id": prompt_id,
                "prompt": prompt,
                "result": "VETO",
                "reason": str(gv)
            })
            self.stats["VETO"] += 1

        except Exception as e:
            self.results.append({
                "id": prompt_id,
                "prompt": prompt,
                "result": "ERROR",
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
            "pass_rate": self.stats["PASS"] / total,
            "veto_rate": self.stats["VETO"] / total,
            "error_rate": self.stats["ERROR"] / total,
            "counts": dict(self.stats)
        }

        return summary

    def export_results(self, path: str):
        """
        Save detailed results for audit / paper appendix.
        """
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2)
