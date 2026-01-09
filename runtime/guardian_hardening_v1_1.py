# runtime/guardian_hardening_v1_1.py
"""
Guardian Hardening V1.1 (DESIGN-ONLY / NOT EVALUATED)

This module provides *additive* hardening layers intended to wrap the
frozen Guardian Validator v1.0.1 WITHOUT changing:

- Action set
- JSON schema structure
- Hard limits (0.5 m/s, 2.0 N)
- Sequencing rules

MANDATE
-------
- These checks are NOT part of V1.0.1 evaluation or certification.
- Treat as design-complete, untested until a dedicated adversarial suite is run.

Design Goals
------------
1) Fail-closed: any internal exception must result in veto by caller.
2) Conservative: ambiguous or hostile inputs are rejected.
3) Bounded: size, structure, and cumulative limits enforced.
4) Stateless: no cross-plan memory or accumulation.
5) Minimal coupling: no robot, actuator, or sensor knowledge.

Integration Contract
--------------------
Used ONLY by a wrapper validator (e.g., GuardianValidatorV1_1).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from runtime.guardian_validator import GuardianViolation


# ============================================================
# G1.1 — Input Hardening
# ============================================================

@dataclass(frozen=True)
class InputHardenerConfig:
    max_chars: int = 10_000
    max_lines: int = 200
    max_nesting_depth: int = 50
    strip_bom: bool = True
    normalize_unicode: str = "NFKC"
    forbid_control_chars: bool = True
    forbid_null_bytes: bool = True
    forbid_zero_width: bool = True
    dangerous_substrings: Tuple[str, ...] = (
        "__import__", "import ", "exec(", "eval(", "os.system", "subprocess",
    )


class InputHardener:
    """
    Sanitizes raw planner output BEFORE JSON parsing.
    This is a bounded input guard, not a sandbox.
    """

    _ZERO_WIDTH = {
        "\u200b", "\u200c", "\u200d", "\ufeff", "\u2060"
    }

    def __init__(self, config: Optional[InputHardenerConfig] = None):
        self.cfg = config or InputHardenerConfig()

    def sanitize(self, raw: str) -> str:
        if not isinstance(raw, str):
            raise GuardianViolation("Input must be a string", gate="G1_Type")

        if len(raw) == 0:
            raise GuardianViolation("Empty input", gate="G1_Size")

        if len(raw) > self.cfg.max_chars:
            raise GuardianViolation("Input exceeds max size", gate="G1_Size")

        if raw.count("\n") + 1 > self.cfg.max_lines:
            raise GuardianViolation("Input exceeds max line count", gate="G1_Size")

        if self.cfg.strip_bom and raw.startswith("\ufeff"):
            raw = raw.lstrip("\ufeff")

        if self.cfg.normalize_unicode:
            raw = unicodedata.normalize(self.cfg.normalize_unicode, raw)

        if self.cfg.forbid_null_bytes and "\x00" in raw:
            raise GuardianViolation("Null byte detected", gate="G1_Malicious")

        if self.cfg.forbid_zero_width:
            for ch in self._ZERO_WIDTH:
                if ch in raw:
                    raise GuardianViolation("Zero-width character detected", gate="G1_Malicious")

        if self.cfg.forbid_control_chars:
            for ch in raw:
                o = ord(ch)
                if o < 32 and o not in (9, 10, 13):
                    raise GuardianViolation("Control character detected", gate="G1_Malicious")

        lowered = raw.lower()
        for s in self.cfg.dangerous_substrings:
            if s in lowered:
                raise GuardianViolation("Dangerous substring detected", gate="G1_Malicious")

        self._check_structure(raw)

        return raw

    def _check_structure(self, raw: str) -> None:
        if raw.count("{") != raw.count("}"):
            raise GuardianViolation("Unbalanced braces", gate="G1_Structure")
        if raw.count("[") != raw.count("]"):
            raise GuardianViolation("Unbalanced brackets", gate="G1_Structure")

        max_depth = 0
        current = 0
        for ch in raw:
            if ch in "{[":
                current += 1
                max_depth = max(max_depth, current)
                if max_depth > self.cfg.max_nesting_depth:
                    raise GuardianViolation("Excessive nesting depth", gate="G1_Structure")
            elif ch in "}]":
                current -= 1
                if current < 0:
                    raise GuardianViolation("Invalid nesting order", gate="G1_Structure")


# ============================================================
# G2.1 — Cumulative Limits (Stateless)
# ============================================================

@dataclass(frozen=True)
class CumulativeLimitsConfig:
    max_unique_targets: int = 6
    max_grasp_actions: int = 4
    max_total_wait_s: float = 60.0
    max_force_time_ns: float = 6.0
    default_grasp_contact_s: float = 1.0


class CumulativeLimitsTracker:
    """
    Tracks aggregate risk within a SINGLE plan.
    Stateless by design.
    """

    def __init__(self, config: Optional[CumulativeLimitsConfig] = None):
        self.cfg = config or CumulativeLimitsConfig()

    def validate(self, actions: List[Dict[str, Any]]) -> None:
        unique_targets: Set[str] = set()
        grasp_count = 0
        total_wait = 0.0
        force_time = 0.0

        for action in actions:
            atype = str(action.get("type", "")).lower()
            params = action.get("params") or {}

            t = params.get("target")
            if isinstance(t, str):
                unique_targets.add(t)

            if atype == "wait":
                d = params.get("duration_s")
                if isinstance(d, (int, float)):
                    total_wait += float(d)

            if atype == "grasp":
                grasp_count += 1
                f = params.get("force_n")
                if isinstance(f, (int, float)):
                    force_time += float(f) * self.cfg.default_grasp_contact_s

        if len(unique_targets) > self.cfg.max_unique_targets:
            raise GuardianViolation("Too many unique targets", gate="G2_Cumulative")

        if grasp_count > self.cfg.max_grasp_actions:
            raise GuardianViolation("Too many grasp actions", gate="G2_Cumulative")

        if total_wait > self.cfg.max_total_wait_s:
            raise GuardianViolation("Total wait time exceeded", gate="G2_Cumulative")

        if force_time > self.cfg.max_force_time_ns:
            raise GuardianViolation("Cumulative force-time exceeded", gate="G2_Cumulative")


# ============================================================
# G2.2 — Safety Target Validation (Normalized)
# ============================================================

@dataclass(frozen=True)
class SafetyTargetConfig:
    deny_substrings: Tuple[str, ...] = (
        "estop", "emergency", "kill", "power", "breaker",
        "safety", "interlock", "override", "battery", "mains",
        "panel", "fuse", "wire", "cable",
    )
    deny_exact: Tuple[str, ...] = (
        "emergencystop", "killswitch", "safetypin",
    )
    allow_exact: Tuple[str, ...] = ()


class SafetyTargetValidator:
    """
    Symbolic deny-by-default protection against safety-defeat targets.
    """

    def __init__(self, config: Optional[SafetyTargetConfig] = None):
        self.cfg = config or SafetyTargetConfig()
        self._deny_exact = {s for s in self.cfg.deny_exact}
        self._allow_exact = {s for s in self.cfg.allow_exact}

    def validate(self, actions: List[Dict[str, Any]]) -> None:
        for action in actions:
            params = action.get("params") or {}
            t = params.get("target")
            if not isinstance(t, str):
                continue

            norm = self._normalize_target(t)

            if self._allow_exact and norm not in self._allow_exact:
                raise GuardianViolation("Target not in allowlist", gate="G2_Target")

            if norm in self._deny_exact:
                raise GuardianViolation("Forbidden safety target", gate="G2_Target")

            for sub in self.cfg.deny_substrings:
                if sub in norm:
                    raise GuardianViolation("Forbidden safety target pattern", gate="G2_Target")

    @staticmethod
    def _normalize_target(target: str) -> str:
        s = target.lower()
        s = unicodedata.normalize("NFKC", s)
        s = re.sub(r"[^a-z0-9]", "", s)
        return s
