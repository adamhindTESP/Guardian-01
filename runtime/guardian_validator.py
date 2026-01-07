import json
from jsonschema import validate, ValidationError
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "guardian01_action_contract_v1.schema.json"

MAX_SPEED_MPS = 0.5
MAX_FORCE_N = 2.0


class GuardianViolation(Exception):
    pass


class GuardianValidator:
    def __init__(self):
        with open(SCHEMA_PATH, "r") as f:
            self.schema = json.load(f)

    def validate_plan(self, plan: dict):
        """
        Entry point: raises GuardianViolation on any failure.
        Returns True if plan is accepted.
        """

        # 1️⃣ Structural validation (schema)
        try:
            validate(instance=plan, schema=self.schema)
        except ValidationError as e:
            raise GuardianViolation(f"Schema violation: {e.message}")

        actions = plan["actions"]

        # 2️⃣ Per-action hard limits
        for idx, action in enumerate(actions):
            self._check_action_limits(action, idx)

        # 3️⃣ Sequencing rules
        self._check_sequencing(actions)

        # ✅ Accepted
        return True

    def _check_action_limits(self, action: dict, idx: int):
        params = action.get("params", {})

        speed = params.get("speed_mps")
        if speed is not None and speed > MAX_SPEED_MPS:
            raise GuardianViolation(
                f"Action {idx}: speed {speed} exceeds max {MAX_SPEED_MPS}"
            )

        force = params.get("force_n")
        if force is not None and force > MAX_FORCE_N:
            raise GuardianViolation(
                f"Action {idx}: force {force} exceeds max {MAX_FORCE_N}"
            )

    def _check_sequencing(self, actions: list):
        last_action = None

        for i, action in enumerate(actions):
            atype = action["type"]

            # grasp requires prior observe
            if atype == "grasp":
                if not self._prior_action_exists(actions, i, "observe"):
                    raise GuardianViolation(
                        "grasp requires prior observe"
                    )

            # release requires prior grasp
            if atype == "release":
                if not self._prior_action_exists(actions, i, "grasp"):
                    raise GuardianViolation(
                        "release requires prior grasp"
                    )

            # navigate forbidden immediately after grasp
            if atype == "navigate" and last_action == "grasp":
                raise GuardianViolation(
                    "navigate forbidden immediately after grasp"
                )

            last_action = atype

    @staticmethod
    def _prior_action_exists(actions, index, required_type):
        return any(a["type"] == required_type for a in actions[:index])
