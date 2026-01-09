"""
Guardian Runtime Package

This package contains execution- and validation-relevant runtime components
for the Guardian Architecture.

AUTHORITY & SCOPE
-----------------
- Files in this package MAY participate in safety enforcement.
- Only explicitly documented artifacts are normative for certification.
- Importing this package DOES NOT grant execution authority by itself.

NORMATIVE ARTIFACTS (v1.0.1)
----------------------------
- guardian_validator.py     (G1 Action Contract Enforcement Kernel)

NON-NORMATIVE / DESIGN-ONLY
---------------------------
- guardian_validator_v1_1.py
- guardian_hardening_v1_1.py

These files are design-complete but NOT evaluated and MUST NOT be used
to support any certified safety claim.

PACKAGE DISCIPLINE
------------------
- This package is intentionally explicit (no implicit namespace behavior).
- Any change to normative artifacts requires:
    * version bump
    * test re-execution
    * documentation update

"""

# Explicit exports (kept minimal by design)
__all__ = [
    "guardian_validator",
]
