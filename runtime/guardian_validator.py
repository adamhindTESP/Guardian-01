import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from pathlib import Path
from typing import Dict, Any


SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "guardian01_action_contract_v1.schema.json"

MAX_SPEED_MPS = 0.5
MAX_FORCE_N = 2.0


# -------------------------------
# Guardian Violation (VETO)
# -------------------------------
class GuardianViolation(Exception):
    def __init__(self, message: str, gate: str):
        super().__init__(message)
        self.message = message
        self.gate = gate

    def __str__(self):
        return f"VETO[{self.gate}]: {self.message}"


# -------------------------------
# Guardian Validator (Authority)
# -------------------------------
class GuardianValidator:
    """
    Implements the frozen Guardian veto logic:
    G1 — Syntax & schema
    G2 — Policy & limits
    G3 — Sequencing (context-free for v1)
    """

    def __init__(self):
        with open(SCHEMA_PATH, "r") as f:
            self.schema = json.load(f)

    def validate_plan(self, plan_output: str, sensor_data: Dict[str, Any] | None = None):
        """
        Entry point.
        - plan_output: RAW string from planner (untrusted)
        - Raises GuardianViolation on ANY failure
        """

        # -------------------
        # G1 — Syntax / JSON
        # -------------------
        try:
            plan = json.loads(plan_output)
        except json.JSONDecodeError as e:
            raise GuardianViolation(
                "Malformed JSON output",
                gate="G1_Syntax_Failure"
            ) from e

        # -------------------
        # G1 — Schema
        # -------------------
        try:
            validate(instance=plan, schema=self.schema)
        except ValidationError as e:
            raise GuardianViolation(
                f"Schema violation: {e.message}",
                gate="G1_Structure_Failure"
            ) from e

        actions = plan["actions"]

        # -------------------
        # G2 — Per-action limits
        # -------------------
        for idx, action in enumerate(actions):
            self._check_action_limits(action, idx)

        # -------------------
        # G3 — Sequencing rules
        # -------------------
        self._check_sequencing(actions)

        # ✅ FINAL PASS
        return True

    # -------------------------------
    # G2 — Limits
    # -------------------------------
    def _check_action_limits(self, action: dict, idx: int):
        params = action.get("params", {})

        speed = params.get("speed_mps")
        if speed is not None and speed > MAX_SPEED_MPS:
            raise GuardianViolation(
                f"Action {idx}: speed {speed} exceeds max {MAX_SPEED_MPS}",
                gate="G2_Policy_Violation"
            )

        force = params.get("force_n")
        if force is not None and force > MAX_FORCE_N:
            raise GuardianViolation(
                f"Action {idx}: force {force} exceeds max {MAX_FORCE_N}",
                gate="G2_Policy_Violation"
            )

    # -------------------------------
    # G3 — Sequencing
    # -------------------------------
    def _check_sequencing(self, actions: list):
        last_action = None

        for i, action in enumerate(actions):
            atype = action["type"].lower()

            # grasp requires prior observe
            if atype == "grasp":
                if not self._prior_action_exists(actions, i, "observe"):
                    raise GuardianViolation(
                        "grasp requires prior observe",
                        gate="G3_Sequencing_Violation"
                    )

            # release requires prior grasp
            if atype == "release":
                if not self._prior_action_exists(actions, i, "grasp"):
                    raise GuardianViolation(
                        "release requires prior grasp",
                        gate="G3_Sequencing_Violation"
                    )

            # navigate forbidden immediately after grasp
            if atype == "navigate" and last_action == "grasp":
                raise GuardianViolation(
                    "navigate forbidden immediately after grasp",
                    gate="G3_Sequencing_Violation"
                )

            last_action = atype

    @staticmethod
    def _prior_action_exists(actions, index, required_type):
        return any(
            a["type"].lower() == required_type
            for a in actions[:index]
        )
