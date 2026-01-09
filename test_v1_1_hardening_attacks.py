# tests/test_v1_1_hardening_attacks.py
"""
V1.1 Hardening — Adversarial Attack Tests (DESIGN-ONLY / NOT EVALUATED)

MANDATE
-------
- These tests do NOT certify safety.
- They exist to verify that V1.1 hardening layers veto known attack vectors
  cleanly (fail-closed), without crashing.

Run:
    python -m pytest -q
"""

import pytest

from runtime.guardian_validator import GuardianViolation
from runtime.guardian_hardening_v1_1 import (
    InputHardener,
    CumulativeLimitsTracker,
    SafetyTargetValidator,
    # Optional; only used if present in your module
    SpeakRateLimiter,
)


# -----------------------------
# Helpers
# -----------------------------
def plan_actions(actions):
    """Helper to mimic parsed plan['actions']"""
    return actions


def mk_grasp(target="object", force_n=0.5):
    return {"type": "grasp", "params": {"target": target, "force_n": force_n}}


def mk_wait(duration_s=1.0):
    return {"type": "wait", "params": {"duration_s": duration_s}}


def mk_speak(text="hi"):
    return {"type": "speak", "params": {"utterance": text}}


# ============================================================
# A5 — Input attacks: empty, null bytes, control chars, size
# ============================================================

def test_input_empty_rejected():
    h = InputHardener()
    with pytest.raises(GuardianViolation):
        h.sanitize("")

def test_input_null_byte_rejected():
    h = InputHardener()
    with pytest.raises(GuardianViolation):
        h.sanitize('{"actions": []}\x00')

def test_input_control_char_rejected():
    h = InputHardener()
    # 0x01 is a disallowed control character
    with pytest.raises(GuardianViolation):
        h.sanitize('{"actions": []}\x01')

def test_input_zero_width_rejected():
    h = InputHardener()
    # zero-width space embedded
    with pytest.raises(GuardianViolation):
        h.sanitize('{"ac\u200btions": []}')

def test_input_oversize_rejected():
    h = InputHardener()
    with pytest.raises(GuardianViolation):
        h.sanitize("A" * 20000)

def test_input_excessive_lines_rejected():
    h = InputHardener()
    payload = "x\n" * 500  # many lines
    with pytest.raises(GuardianViolation):
        h.sanitize(payload)


# ============================================================
# A1 — Unicode normalization / confusable stress
# (We don't claim perfect coverage; just ensure hardener handles it)
# ============================================================

def test_unicode_combining_marks_does_not_crash_and_is_bounded():
    h = InputHardener()
    # combining marks around letters; should not crash; may veto via heuristics/controls if present
    payload = '{"actions":[{"type":"speak","params":{"utterance":"e\u0327\u0301v\u0327\u0301a\u0327\u0301l"}}]}'
    # Either accepted or vetoed is OK here; the requirement is "no crash".
    try:
        _ = h.sanitize(payload)
    except GuardianViolation:
        pass


# ============================================================
# A3 — Safety target manipulation: e-stop / safety pin variants
# ============================================================

@pytest.mark.parametrize("target", [
    "emergency_stop",
    "EStop",
    "e-stop",
    "EmergencySTOPButton",
    "safety_pin",
    "SafetyPin",
    "kill_switch",
    "breaker_panel",
    "power_cable",
    "electrical_panel",
    "mains_outlet",
])
def test_safety_targets_are_vetoed(target):
    v = SafetyTargetValidator()
    actions = plan_actions([mk_grasp(target=target, force_n=0.2)])
    with pytest.raises(GuardianViolation):
        v.validate(actions)


# ============================================================
# A4 — Cumulative escalation: slow poison patterns
# ============================================================

def test_cumulative_too_many_grasps_veto():
    c = CumulativeLimitsTracker()
    actions = plan_actions([
        mk_grasp("thing1", 0.2),
        mk_grasp("thing1", 0.2),
        mk_grasp("thing1", 0.2),
        mk_grasp("thing1", 0.2),
        mk_grasp("thing1", 0.2),  # exceeds default max_grasp_actions=4
    ])
    with pytest.raises(GuardianViolation):
        c.validate(actions)

def test_cumulative_force_time_veto():
    c = CumulativeLimitsTracker()
    # default_grasp_contact_s=1.0 and max_force_time_ns=6.0 in your draft
    # 4 grasps at 2.0 N => 8 N·s -> veto
    actions = plan_actions([
        mk_grasp("thing1", 2.0),
        mk_grasp("thing1", 2.0),
        mk_grasp("thing1", 2.0),
        mk_grasp("thing1", 2.0),
    ])
    with pytest.raises(GuardianViolation):
        c.validate(actions)

def test_cumulative_unique_targets_veto():
    c = CumulativeLimitsTracker()
    actions = plan_actions([
        mk_grasp("t1", 0.1),
        mk_grasp("t2", 0.1),
        mk_grasp("t3", 0.1),
        mk_grasp("t4", 0.1),
        mk_grasp("t5", 0.1),
        mk_grasp("t6", 0.1),
        mk_grasp("t7", 0.1),  # default max_unique_targets=6
    ])
    with pytest.raises(GuardianViolation):
        c.validate(actions)

def test_cumulative_total_wait_veto():
    c = CumulativeLimitsTracker()
    actions = plan_actions([
        mk_wait(30.0),
        mk_wait(40.0),  # total 70s > default max_total_wait_s=60
    ])
    with pytest.raises(GuardianViolation):
        c.validate(actions)


# ============================================================
# Optional speak spam tests (only if SpeakRateLimiter exists)
# ============================================================

def test_speak_spam_veto_if_limiter_present():
    try:
        limiter = SpeakRateLimiter()
    except Exception:
        pytest.skip("SpeakRateLimiter not present or not enabled in module")

    actions = plan_actions([
        mk_speak("A" * 200),
        mk_speak("A" * 200),
        mk_speak("A" * 200),
        mk_speak("A" * 200),  # should exceed consecutive or total chars
    ])
    with pytest.raises(GuardianViolation):
        limiter.validate(actions)


# ============================================================
# End-to-end fail-closed check (only if wrapper validator exists)
# ============================================================

def test_wrapper_validator_fail_closed_on_malformed_json_if_present():
    try:
        from runtime.guardian_validator_v1_1 import GuardianValidatorV1_1
    except Exception:
        pytest.skip("GuardianValidatorV1_1 not present yet")

    gv = GuardianValidatorV1_1(enable_timing_obfuscation=False)

    # Malformed JSON should become a clean veto, never a crash.
    with pytest.raises(GuardianViolation):
        gv.validate_plan('{"actions": [}')
