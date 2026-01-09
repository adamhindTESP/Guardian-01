# runtime/guardian_validator_v1_1.py
"""
Guardian Validator V1.1 (DESIGN-ONLY / NOT EVALUATED)

Purpose
-------
Wrap the *frozen* Guardian Validator V1.0.1 with additive, fail-closed
hardening layers (sanitization, timeout, cumulative/rate/target checks).

MANDATE
-------
- This module MUST NOT be used for any V1.0.1 evaluation or arXiv results.
- V1.0.1 remains the sole certified authority until V1.1 is tested.

Platform Note (IMPORTANT)
-------------------------
- POSIX (Linux/macOS): SIGALRM timeout can be enforced.
- Windows: SIGALRM/alarm is not supported. Timeout is *disabled* here by design
  until a Windows-safe watchdog (e.g., subprocess/multiprocessing) is implemented.
"""

from __future__ import annotations

import json
import random
import time
import signal
from typing import Any, Dict, Optional, Callable

from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Frozen V1.0.1 core authority (DO NOT MODIFY)
from runtime.guardian_validator import GuardianValidator, GuardianViolation

# Additive V1.1 hardening components (new files)
from runtime.guardian_hardening_v1_1 import (
    CumulativeLimitsTracker,
    SafetyTargetValidator,
    InputHardener,
)

# -----------------------------
# Timing obfuscation decorator
# -----------------------------
def timing_obfuscation(min_time_s: float = 0.01, max_jitter_s: float = 0.005) -> Callable:
    """
    Best-effort side-channel mitigation (NOT a formal constant-time guarantee).

    WARNING:
    - Adds latency/jitter. Do not enable in real-time control loops until validated.
    """
    def deco(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.time() - start
                if elapsed < min_time_s:
                    time.sleep((min_time_s - elapsed) + random.uniform(0.0, max_jitter_s))
        return wrapper
    return deco


# -----------------------------
# POSIX timeout helper
# -----------------------------
class _Timeout(Exception):
    pass


def _timeout_handler(signum, frame):
    raise _Timeout()


def _posix_alarm_supported() -> bool:
    # SIGALRM exists on POSIX; alarm exists on Unix. On Windows, SIGALRM is absent.
    return hasattr(signal, "SIGALRM") and hasattr(signal, "alarm")


class GuardianValidatorV1_1(GuardianValidator):
    """
    Guardian Validator V1.1
    -----------------------
    Composition:
      - V1.0.1 core checks (schema, limits, sequencing) remain unchanged.
      - V1.1 adds defensive layers:
          G1.1 InputHardener (sanitize + size cap)
          G1.2 Timeout around parsing/schema (POSIX only)
          G2.1 CumulativeLimitsTracker
          G2.2 SafetyTargetValidator
      - Fail-closed: ANY unexpected exception -> GuardianViolation
    """

    def __init__(self, *, enable_timing_obfuscation: bool = False, timeout_s: float = 1.0):
        super().__init__()

        # V1.1 layers
        self.input_hardener = InputHardener()
        self.cumulative_tracker = CumulativeLimitsTracker()
        self.target_validator = SafetyTargetValidator()

        # Controls (design-only; default OFF for obfuscation)
        self._enable_timing_obfuscation = bool(enable_timing_obfuscation)
        self._timeout_s = float(timeout_s)

    def _set_timeout(self):
        """
        Enforce a hard timeout on untrusted parse/validate work (POSIX only).
        On Windows: timeout is intentionally disabled for now (documented).
        """
        if _posix_alarm_supported():
            signal.signal(signal.SIGALRM, _timeout_handler)
            # alarm() takes integer seconds; be conservative
            secs = max(1, int(self._timeout_s))
            signal.alarm(secs)

    def _clear_timeout(self):
        if _posix_alarm_supported():
            signal.alarm(0)

    def _validate_core_v101(self, plan: dict) -> bool:
        """
        Run the frozen V1.0.1 logic using the already-loaded V1 schema.
        This is the *same* enforcement as v1.0.1; do not change behavior here.
        """
        # V1.0.1 G1 — Schema
        try:
            validate(instance=plan, schema=self.schema)
        except ValidationError as e:
            raise GuardianViolation(f"Schema violation: {e.message}", gate="G1_Structure_Failure") from e

        actions = plan["actions"]

        # V1.0.1 G2 — Per-action limits & required params
        for idx, action in enumerate(actions):
            self._check_action_limits(action, idx)

        # V1.0.1 G3 — Sequencing rules
        self._check_sequencing(actions)

        return True

    @timing_obfuscation(min_time_s=0.01, max_jitter_s=0.005)
    def _validate_plan_with_optional_obfuscation(self, plan_output: str, sensor_data: Optional[Dict[str, Any]] = None) -> bool:
        # NOTE: sensor_data intentionally unused in V1.1 (reserved for G4+)
        _ = sensor_data

        # Layer 1: Input hardening (sanitize + size cap, etc.)
        clean_input = self.input_hardener.sanitize(plan_output)

        # Layer 1b: Timeout around parsing/schema (POSIX only)
        self._set_timeout()
        try:
            # V1.0.1 G1 — Syntax / JSON
            try:
                plan = json.loads(clean_input)
            except json.JSONDecodeError as e:
                raise GuardianViolation("Malformed JSON output", gate="G1_Syntax_Failure") from e

            # Layer 2: Frozen V1.0.1 core checks
            self._validate_core_v101(plan)

            # Layer 3: V1.1 additive checks (SCRAM-style wrapping)
            actions = plan["actions"]
            self.cumulative_tracker.validate(actions)
            self.target_validator.validate(actions)

            return True

        except _Timeout:
            # POSIX timeout fired
            raise GuardianViolation("Validation timeout", gate="G1_Timeout")

        finally:
            self._clear_timeout()

    def validate_plan(self, plan_output: str, sensor_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        V1.1 entry point.

        Fail-closed rules:
        - GuardianViolation -> re-raise (expected veto)
        - Any other exception -> VETO as internal error (never crash)
        """
        try:
            if self._enable_timing_obfuscation:
                return self._validate_plan_with_optional_obfuscation(plan_output, sensor_data=sensor_data)
            else:
                # Call the same logic without timing jitter (avoid extra latency by default)
                return self._validate_plan_no_obfuscation(plan_output, sensor_data=sensor_data)

        except GuardianViolation:
            raise

        except Exception as e:
            # Any unexpected exception -> veto (fail-closed)
            raise GuardianViolation(f"Validator internal error: {type(e).__name__}", gate="G1_Internal_Error") from e

    def _validate_plan_no_obfuscation(self, plan_output: str, sensor_data: Optional[Dict[str, Any]] = None) -> bool:
        # NOTE: sensor_data intentionally unused in V1.1 (reserved for G4+)
        _ = sensor_data

        clean_input = self.input_hardener.sanitize(plan_output)

        self._set_timeout()
        try:
            try:
                plan = json.loads(clean_input)
            except json.JSONDecodeError as e:
                raise GuardianViolation("Malformed JSON output", gate="G1_Syntax_Failure") from e

            self._validate_core_v101(plan)

            actions = plan["actions"]
            self.cumulative_tracker.validate(actions)
            self.target_validator.validate(actions)

            return True

        except _Timeout:
            raise GuardianViolation("Validation timeout", gate="G1_Timeout")

        finally:
            self._clear_timeout()
