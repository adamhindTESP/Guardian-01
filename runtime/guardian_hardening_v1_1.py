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
- These checks are not part of V1.0.1 evaluation claims.
- Treat as design-complete, untested until you run a dedicated adversarial suite.

Design Goals
------------
1) Fail-closed: any internal exception should be treated as a veto by caller.
2) Conservative: unknown/ambiguous inputs are rejected or constrained.
3) Bounded: enforce size, character, and cumulative limits to resist DoS / slow-poison patterns.
4) Minimal coupling: this module knows nothing about robots, actuators, or sensors.

Integration Contract
--------------------
Expected usage from a wrapper validator (e.g., GuardianValidatorV1_1):

    clean = InputHardener().sanitize(raw_str)
    ...
    CumulativeLimitsTracker().validate(actions)
    SafetyTargetValidator().validate(actions)

Where `actions` is the parsed list of action dicts from the v1.0.1 schema:
    [{"type": "...", "params": {...}}, ...]
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

# Reuse the frozen GuardianViolation type so callers have a single veto type.
# IMPORTANT: this import is safe because we're not modifying the core module.
from runtime.guardian_validator import GuardianViolation


# ============================================================
# G1.1 — Input Hardening (sanitize, size cap, unicode normalize)
# ============================================================

@dataclass(frozen=True)
class InputHardenerConfig:
    max_chars: int = 10_000                 # cap raw payload size (characters)
    max_lines: int = 200                    # simple DoS guard
    strip_bom: bool = True
    normalize_unicode: str = "NFKC"         # NFKC reduces confusable variants
    forbid_control_chars: bool = True       # reject most C0 controls except \n \r \t
    forbid_null_bytes: bool = True
    forbid_non_ascii_zero_width: bool = True  # blocks ZW* invisibles commonly abused
    # Optional: reject obviously malicious substrings (cheap heuristic; not a guarantee)
    dangerous_substrings: Tuple[str, ...] = (
        "__import__", "import ", "exec(", "eval(", "os.system", "subprocess",
    )


class InputHardener:
    """
    Sanitizes raw planner output BEFORE json parsing.
    This is not a "security sandbox"—it's a bounded input guard.
    """

    # Zero-width characters that can hide payloads in plain sight
    _ZERO_WIDTH = {
        "\u200b",  # ZERO WIDTH SPACE
        "\u200c",  # ZERO WIDTH NON-JOINER
        "\u200d",  # ZERO WIDTH JOINER
        "\ufeff",  # ZERO WIDTH NO-BREAK SPACE / BOM
        "\u2060",  # WORD JOINER
    }

    def __init__(self, config: Optional[InputHardenerConfig] = None):
        self.cfg = config or InputHardenerConfig()

    def sanitize(self, raw: str) -> str:
        if raw is None:
            raise GuardianViolation("Empty input (None)", gate="G1_Size")

        # Enforce type early (fail-closed)
        if not isinstance(raw, str):
            raise GuardianViolation("Input must be a string", gate="G1_Type")

        # Size caps
        if len(raw) == 0:
            raise GuardianViolation("Empty input", gate="G1_Size")
        if len(raw) > self.cfg.max_chars:
            raise GuardianViolation("Input exceeds max size", gate="G1_Size")

        # Line caps (cheap DoS guard)
        if raw.count("\n") + 1 > self.cfg.max_lines:
            raise GuardianViolation("Input exceeds max line count", gate="G1_Size")

        # Strip BOM if requested
        if self.cfg.strip_bom and raw.startswith("\ufeff"):
            raw = raw.lstrip("\ufeff")

        # Normalize unicode (reduces confusables)
        if self.cfg.normalize_unicode:
            raw = unicodedata.normalize(self.cfg.normalize_unicode, raw)

        # Null bytes
        if self.cfg.forbid_null_bytes and "\x00" in raw:
            raise GuardianViolation("Null byte detected", gate="G1_Malicious")

        # Zero-width/invisible chars
        if self.cfg.forbid_non_ascii_zero_width:
            for ch in self._ZERO_WIDTH:
                if ch in raw:
                    raise GuardianViolation("Zero-width/invisible char detected", gate="G1_Malicious")

        # Control characters (except common whitespace)
        if self.cfg.forbid_control_chars:
            for ch in raw:
                o = ord(ch)
                # Allow: \t (9), \n (10), \r (13)
                if o < 32 and o not in (9, 10, 13):
                    raise GuardianViolation("Control character detected", gate="G1_Malicious")

        # Optional substring heuristics (don’t over-trust; just cheap early veto)
        lowered = raw.lower()
        for s in self.cfg.dangerous_substrings:
            if s.lower() in lowered:
                raise GuardianViolation("Dangerous substring detected", gate="G1_Malicious")

        return raw


# ============================================================
# G2.1 — Cumulative limits (slow-poison / escalation resistance)
# ============================================================

@dataclass(frozen=True)
class CumulativeLimitsConfig:
    """
    These are conservative "plan-level" limits. They are NOT physics.
    They exist to block obvious escalation patterns within a single plan.

    Note: without execution telemetry, we must assume worst-case durations
    for some actions (e.g., grasp contact time).
    """
    # Maximum number of distinct targets referenced in a plan (helps reduce nonsense / mapping risk)
    max_unique_targets: int = 6

    # Force-time budget proxy (N·s). Conservative estimate: each grasp counts as default_grasp_contact_s.
    max_force_time_ns: float = 6.0
    default_grasp_contact_s: float = 1.0

    # Maximum number of grasps in one plan (blocks repeated poking)
    max_grasp_actions: int = 4

    # Optional: cap total "busy time" requested by waits (prevents stalling plans)
    max_total_wait_s: float = 60.0


class CumulativeLimitsTracker:
    """
    Tracks cumulative plan properties that are individually valid per-action
    but risky in aggregate (slow poisoning / repetition patterns).
    """

    def __init__(self, config: Optional[CumulativeLimitsConfig] = None):
        self.cfg = config or CumulativeLimitsConfig()

    def validate(self, actions: List[Dict[str, Any]]) -> None:
        if not isinstance(actions, list) or len(actions) == 0:
            # Core schema should catch this, but keep fail-closed
            raise GuardianViolation("Actions missing or not a list", gate="G2_Cumulative")

        unique_targets: Set[str] = set()
        grasp_count = 0
        total_wait = 0.0
        force_time = 0.0

        for idx, action in enumerate(actions):
            atype = str(action.get("type", "")).lower()
            params = action.get("params") or {}

            # Track targets (string only, schema ensures string)
            t = params.get("target")
            if isinstance(t, str) and t:
                unique_targets.add(t)

            # Aggregate waits
            if atype == "wait":
                d = params.get("duration_s")
                if isinstance(d, (int, float)):
                    total_wait += float(d)

            # Aggregate grasp force-time proxy
            if atype == "grasp":
                grasp_count += 1
                f = params.get("force_n")
                if isinstance(f, (int, float)):
                    force = float(f)
                else:
                    force = 0.0
                force_time += force * self.cfg.default_grasp_contact_s

        if len(unique_targets) > self.cfg.max_unique_targets:
            raise GuardianViolation(
                f"Too many unique targets ({len(unique_targets)} > {self.cfg.max_unique_targets})",
                gate="G2_Cumulative"
            )

        if grasp_count > self.cfg.max_grasp_actions:
            raise GuardianViolation(
                f"Too many grasp actions ({grasp_count} > {self.cfg.max_grasp_actions})",
                gate="G2_Cumulative"
            )

        if total_wait > self.cfg.max_total_wait_s:
            raise GuardianViolation(
                f"Total wait time too large ({total_wait:.2f}s > {self.cfg.max_total_wait_s:.2f}s)",
                gate="G2_Cumulative"
            )

        if force_time > self.cfg.max_force_time_ns:
            raise GuardianViolation(
                f"Cumulative force-time too large ({force_time:.3f} N·s > {self.cfg.max_force_time_ns:.3f} N·s)",
                gate="G2_Cumulative"
            )


# ============================================================
# G2.2 — Safety target validation (blacklist / deny-by-default)
# ============================================================

@dataclass(frozen=True)
class SafetyTargetConfig:
    """
    This is a symbolic guardrail. It does not require perception.
    Denylist blocks obvious "safety defeat" identifiers.
    Allowlist is optional; if enabled, unknown targets are denied.
    """
    deny_substrings: Tuple[str, ...] = (
        "e-stop", "estop", "emergency", "kill", "power", "breaker",
        "safety", "pin", "interlock", "override", "battery", "mains",
        "outlet", "socket", "panel", "fuse", "wire", "cable",
    )
    deny_exact: Tuple[str, ...] = (
        "emergency_stop", "e_stop", "estop", "kill_switch",
        "safety_pin", "breaker_panel", "electrical_panel",
    )
    # If allowlist is non-empty, enforce allowlist (unknown -> veto).
    allow_exact: Tuple[str, ...] = ()


class SafetyTargetValidator:
    """
    Blocks plans that reference clearly safety-critical targets by name.

    This is intentionally conservative and symbol-based. It is *not* a
    substitute for G4+ physical safeguards or canonical mapping.
    """

    def __init__(self, config: Optional[SafetyTargetConfig] = None):
        self.cfg = config or SafetyTargetConfig()
        self._deny_exact = {s.lower() for s in self.cfg.deny_exact}
        self._allow_exact = {s.lower() for s in self.cfg.allow_exact}
        self._deny_sub = tuple(s.lower() for s in self.cfg.deny_substrings)

    def validate(self, actions: List[Dict[str, Any]]) -> None:
        for idx, action in enumerate(actions):
            params = action.get("params") or {}
            t = params.get("target")
            if not isinstance(t, str) or not t:
                continue

            tl = t.lower()

            # If allowlist is enabled, deny unknown targets
            if self._allow_exact:
                if tl not in self._allow_exact:
                    raise GuardianViolation(
                        f"Target not in allowlist: '{t}'",
                        gate="G2_Target_Forbidden"
                    )

            # Exact deny
            if tl in self._deny_exact:
                raise GuardianViolation(
                    f"Forbidden target: '{t}'",
                    gate="G2_Target_Forbidden"
                )

            # Substring deny (catches variants like "emergencyStop", "EStopButton", etc.)
            for sub in self._deny_sub:
                if sub in tl:
                    raise GuardianViolation(
                        f"Forbidden target pattern '{sub}' in '{t}'",
                        gate="G2_Target_Forbidden"
                    )


# ============================================================
# Optional: speak rate limiting (if you want it later)
# ============================================================

@dataclass(frozen=True)
class SpeakRateConfig:
    max_consecutive_speak: int = 3
    max_total_utterance_chars: int = 400


class SpeakRateLimiter:
    """
    Optional additive guard: blocks 'speak spam' inside a single plan.
    Not currently wired into GuardianValidatorV1_1 unless you call it.
    """

    def __init__(self, config: Optional[SpeakRateConfig] = None):
        self.cfg = config or SpeakRateConfig()

    def validate(self, actions: List[Dict[str, Any]]) -> None:
        consec = 0
        total_chars = 0

        for action in actions:
            atype = str(action.get("type", "")).lower()
            params = action.get("params") or {}

            if atype == "speak":
                consec += 1
                utt = params.get("utterance") or ""
                if isinstance(utt, str):
                    total_chars += len(utt)

                if consec > self.cfg.max_consecutive_speak:
                    raise GuardianViolation("Too many consecutive speak actions", gate="G2_Rate_Limit")

                if total_chars > self.cfg.max_total_utterance_chars:
                    raise GuardianViolation("Total utterance chars exceeded", gate="G2_Rate_Limit")
            else:
                consec = 0
