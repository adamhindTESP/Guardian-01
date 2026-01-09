"""
Guardian Test Suite Package

This package contains verification and adversarial test artifacts for the
Guardian Architecture.

AUTHORITY & SCOPE
-----------------
- Files in this package have NO execution authority.
- Tests produce EVIDENCE ONLY.
- Passing tests do NOT, by themselves, grant certification or gate advancement.

RELATIONSHIP TO GATES
---------------------
- Tests validate properties claimed in GATES.md.
- Gate advancement is governed solely by:
    * passing the required tests
    * documented evidence
    * explicit updates to GATES.md

NORMATIVE TESTS (v1.0.1)
------------------------
These tests support certified claims up to G3.5:

- test_g2_policy_kernel.py
- test_g3_trajectory_safety.py
- test_safety_coordinator.py
- test_failsafe_basic.py

DESIGN-ONLY / NON-CERTIFYING TESTS
---------------------------------
The following tests are explicitly NON-NORMATIVE and DO NOT support any
certified safety claim:

- test_v1_1_hardening_attacks.py
- Any tests referencing guardian_validator_v1_1 or guardian_hardening_v1_1

These exist for forward-looking hardening validation only.

PACKAGE DISCIPLINE
------------------
- Tests MUST be deterministic and auditable.
- Tests MUST fail closed (unexpected exceptions are failures).
- Any new test supporting a gate claim MUST be referenced explicitly
  in GATES.md with evidence.

"""

# This package intentionally exports nothing.
# Tests are discovered and executed via pytest.
__all__ = []
