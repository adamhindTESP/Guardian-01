"""
G1 Failsafe Robustness Tests — Guardian Validator v1.0.1

STATUS
------
Normative robustness tests for G1 (Action Contract Enforcement).

PURPOSE
-------
Verify that the Guardian Validator:
- FAILS CLOSED under malformed, adversarial, or pathological inputs
- NEVER crashes, hangs, or fails open
- ALWAYS returns a GuardianViolation for invalid inputs

SCOPE
-----
- These tests verify robustness, not semantic safety.
- These tests DO NOT advance certification gates.
- These tests DO NOT claim resistance to all denial-of-service attacks.
- Structural complexity defenses beyond basic parsing are deferred to V1.1+.

PASS CONDITION
--------------
Every test MUST raise GuardianViolation.
ANY crash, hang, or non-veto behavior is a CRITICAL FAILURE.

Run:
    python -m pytest tests/test_g1_failsafe_robustness.py -v
"""

import pytest

from runtime.guardian_validator import GuardianValidator, GuardianViolation


class TestG1FailsafeRobustness:
    """
    G1 Robustness Invariant:

    For ALL malformed or hostile inputs:
        outcome ∈ { VETO }
        outcome ∉ { CRASH, HANG, PASS }
    """

    def setup_method(self):
        self.validator = GuardianValidator()

    # -----------------------------
    # G1-R1 — Empty / Null Inputs
    # -----------------------------

    def test_empty_string_veto(self):
        """Empty input MUST veto (G1 fail-closed)."""
        with pytest.raises(GuardianViolation) as exc:
            self.validator.validate_plan("")
        assert exc.value.gate.startswith("G1")

    def test_null_byte_veto(self):
        """Null bytes MUST veto, not crash or parse."""
        payload = '{"actions": []}\x00'
        with pytest.raises(GuardianViolation) as exc:
            self.validator.validate_plan(payload)
        assert exc.value.gate.startswith("G1")

    # -----------------------------
    # G1-R2 — Malformed JSON
    # -----------------------------

    def test_incomplete_json_veto(self):
        """Truncated JSON MUST veto."""
        payload = '{"actions": ['
        with pytest.raises(GuardianViolation) as exc:
            self.validator.validate_plan(payload)
        assert exc.value.gate.startswith("G1")

    def test_syntactically_invalid_json_veto(self):
        """Invalid JSON syntax MUST veto."""
        payload = '{"actions": [}}'
        with pytest.raises(GuardianViolation) as exc:
            self.validator.validate_plan(payload)
        assert exc.value.gate.startswith("G1")

    # -----------------------------
    # G1-R3 — Unicode / Encoding Abuse
    # -----------------------------

    def test_unicode_flood_veto(self):
        """
        Large Unicode payload MUST veto.
        No claim is made about constant-time behavior.
        """
        payload = "🦠" * 10000
        with pytest.raises(GuardianViolation) as exc:
            self.validator.validate_plan(payload)
        assert exc.value.gate.startswith("G1")

    # -----------------------------
    # G1-R4 — Pathological Structure
    # -----------------------------
    @pytest.mark.xfail(reason="Structural complexity hardening added in V1.1")
    def test_extreme_nesting_veto(self):
        """
        Deep nesting SHOULD veto.
        Marked xfail for v1.0.1; enforced in V1.1 hardening.
        """
        payload = '{"a": ' * 5000 + '1' + '}' * 5000
        with pytest.raises(GuardianViolation):
            self.validator.validate_plan(payload)
