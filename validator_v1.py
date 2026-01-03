#!/usr/bin/env python3
"""
validator_v1.py — Schema-locked independent validator (G4-ready)

Authoritative safety gate for Guardian-01.
LLM outputs are treated as untrusted proposals.

Enforces:
- guardian01_action_set_v1 ONLY
- Closed action set
- Numeric hard bounds
- Sequencing invariants
- Zero trust in LLM self-reporting

This module is the policy.
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# =========================
# Errors
# =========================

class ValidationError(Exception):
    """Raised when an LLM proposal violates safety or schema rules."""
    pass

# =========================
# Schema Lock
# =========================

SCHEMA_VERSION = "guardian01_action_set_v1"

# =========================
# Action Set (LOCKED)
# =========================

class ActionType(Enum):
    NAVIGATE = "navigate"
    NAVIGATE_STEP = "navigate_step"
    STOP = "stop"
    OBSERVE = "observe"
    SPEAK = "speak"
    GRASP = "grasp"
    RELEASE = "release"
    WAIT = "wait"
    PLAN_ROUTE = "plan_route"
    MANIPULATE = "manipulate"

# =========================
# Physical Limits (GLOBAL)
# =========================

PHYSICAL_LIMITS = {
    "max_speed_mps": 0.5,
    "min_speed_mps": 0.05,
    "max_force_n": 2.0,
    "min_force_n": 0.1,
    "min_safe_distance_m": 0.3
}

# =========================
# Defaults
# =========================

DEFAULTS = {
    "target_speed_mps": 0.15,
    "max_force_n": 0.5,
    "observe_duration_s": 5.0,
    "reobservation_s": 2.0
}

# =========================
# Schema Definitions
# =========================

ACTION_SCHEMAS = {
    ActionType.NAVIGATE: {
        "required": ["target"],
        "params": ["target_speed_mps"]
    },
    ActionType.NAVIGATE_STEP: {
        "required": ["step_distance_m"],
        "params": ["step_distance_m", "reobservation_s"]
    },
    ActionType.OBSERVE: {
        "required": [],
        "params": ["duration_s"]
    },
    ActionType.SPEAK: {
        "required": ["text"],
        "params": ["text"]
    },
    ActionType.GRASP: {
        "required": ["target"],
        "params": ["max_force_n"]
    },
    ActionType.RELEASE: {
        "required": ["target"],
        "params": []
    },
    ActionType.STOP: {
        "required": [],
        "params": []
    },
    ActionType.WAIT: {
        "required": ["duration_s"],
        "params": ["duration_s"]
    },
    ActionType.PLAN_ROUTE: {
        "required": ["target"],
        "params": []
    },
    ActionType.MANIPULATE: {
        "required": ["target"],
        "params": ["max_force_n"]
    }
}

# =========================
# Blacklist (Semantic)
# =========================

BLACKLIST = {
    "override", "bypass", "force", "coerce",
    "without_consent", "self_destruct",
    "rush", "fast", "quickly",
    "approach_human", "near_human"
}

# =========================
# Output Object
# =========================

@dataclass
class ValidatedPlan:
    schema_version: str
    goals: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    independent_risk: float
    safety_margin: float
    original_json: str

# =========================
# Validator Core
# =========================

class GuardianValidatorV1:
    """
    Deterministic, deception-proof validator.
    This is the *actual* Guardian-01 policy.
    """

    def validate(self, llm_output: str, sensor_data: Dict[str, Any]) -> ValidatedPlan:
        # ---- Parse JSON
        try:
            data = json.loads(llm_output)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")

        # ---- Schema version lock
        if data.get("schema_version") != SCHEMA_VERSION:
            raise ValidationError("Schema version mismatch")

        # ---- Reject self-reports
        self._reject_self_reports(data)

        # ---- Extract goals
        goals = data.get("goals")
        if not goals or not isinstance(goals, list):
            raise ValidationError("Missing or invalid goals list")

        # ---- Validate each goal
        for idx, goal in enumerate(goals):
            self._validate_goal(goal, idx)

        # ---- Sequencing rules
        self._validate_sequence(goals)

        # ---- Parameters (inject defaults)
        parameters = self._normalize_parameters(data.get("parameters", {}))

        # ---- Physical bounds
        self._check_physical_bounds(goals, parameters)

        # ---- Semantic blacklist
        self._check_blacklist(goals)

        # ---- Independent metrics
        risk = self._compute_risk(goals, parameters, sensor_data)
        margin = self._compute_margin(sensor_data)

        logger.debug(f"✓ Valid plan | risk={risk:.3f} margin={margin:.3f}")

        return ValidatedPlan(
            schema_version=SCHEMA_VERSION,
            goals=goals,
            parameters=parameters,
            independent_risk=risk,
            safety_margin=margin,
            original_json=llm_output
        )

    # =========================
    # Internal Checks
    # =========================

    def _reject_self_reports(self, data: Dict[str, Any]) -> None:
        forbidden = {"risk", "dignity", "confidence", "safety", "secure", "score"}
        for k in data:
            if k in forbidden:
                raise ValidationError(f"Self-report blocked: {k}")

    def _validate_goal(self, goal: Dict[str, Any], idx: int) -> None:
        if "action" not in goal:
            raise ValidationError(f"Goal {idx}: missing action")

        try:
            action = ActionType(goal["action"])
        except ValueError:
            raise ValidationError(f"Illegal action: {goal['action']}")

        schema = ACTION_SCHEMAS[action]

        for req in schema["required"]:
            if req not in goal:
                raise ValidationError(f"{action.value}: missing required field '{req}'")

        if "target" in goal:
            self._validate_target(goal["target"])

    def _validate_target(self, target: Dict[str, Any]) -> None:
        if not isinstance(target, dict):
            raise ValidationError("Target must be an object")

        if target.get("kind") not in {"location", "object"}:
            raise ValidationError("Target.kind must be 'location' or 'object'")

        if "id" not in target:
            raise ValidationError("Target.id required")

    def _validate_sequence(self, goals: List[Dict[str, Any]]) -> None:
        seen_observe = False
        holding = False
        step_count = 0

        for goal in goals:
            action = ActionType(goal["action"])

            if action == ActionType.OBSERVE:
                seen_observe = True

            if action == ActionType.GRASP:
                if not seen_observe:
                    raise ValidationError("GRASP requires prior OBSERVE")
                holding = True

            if action == ActionType.RELEASE:
                holding = False

            if action == ActionType.NAVIGATE and holding:
                raise ValidationError("Cannot NAVIGATE while holding object")

            if action == ActionType.NAVIGATE_STEP:
                step_count += 1
                if step_count > 3:
                    raise ValidationError("Too many consecutive NAVIGATE_STEP")
            else:
                step_count = 0

    def _normalize_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(DEFAULTS)
        normalized.update(params)
        return normalized

    def _check_physical_bounds(self, goals: List[Dict[str, Any]], params: Dict[str, Any]) -> None:
        speed = params.get("target_speed_mps")
        if speed is not None:
            if not (PHYSICAL_LIMITS["min_speed_mps"] <= speed <= PHYSICAL_LIMITS["max_speed_mps"]):
                raise ValidationError("Speed out of bounds")

        force = params.get("max_force_n")
        if force is not None:
            if not (PHYSICAL_LIMITS["min_force_n"] <= force <= PHYSICAL_LIMITS["max_force_n"]):
                raise ValidationError("Force out of bounds")

    def _check_blacklist(self, goals: List[Dict[str, Any]]) -> None:
        text = " ".join(json.dumps(g).lower() for g in goals)
        for bad in BLACKLIST:
            if bad in text:
                raise ValidationError(f"Blacklisted semantic content: {bad}")

    # =========================
    # Independent Metrics
    # =========================

    def _compute_risk(self, goals, params, sensors) -> float:
        base = 0.2
        speed = params.get("target_speed_mps", 0.0)
        speed_risk = (speed / PHYSICAL_LIMITS["max_speed_mps"]) ** 2 * 0.6

        front_m = sensors.get("front_cm", 100) / 100
        safe = PHYSICAL_LIMITS["min_safe_distance_m"] * 2.0
        proximity_risk = max(0.0, 1.0 - (front_m / safe))

        return max(base, speed_risk, proximity_risk)

    def _compute_margin(self, sensors) -> float:
        front_m = sensors.get("front_cm", 100) / 100
        safe = PHYSICAL_LIMITS["min_safe_distance_m"] * 2.0
        return min(1.0, front_m / safe)

# =========================
# Factory
# =========================

def get_validator() -> GuardianValidatorV1:
    return GuardianValidatorV1()
