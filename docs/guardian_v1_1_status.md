# Guardian Validator V1.1 — Status & Scope Mandate

## Current Certification Status

| Metric | Status |
| :--- | :--- |
| **V1.0.1 Baseline Status** | **FROZEN & CERTIFIED** (Pending final evaluation) |
| **V1.1 Hardening Status** | ⚠️ **DESIGN COMPLETE, NOT EVALUATED** |
| **V1.1 Use in V1.0.1 Results** | ⚠️ **FORBIDDEN** |

**Mandate:** The files associated with Guardian Validator V1.1 represent a
**design-complete but untested additive hardening layer** intended for
future versions of the Guardian architecture.

They are **STRICTLY NOT** part of:
- The V1.0.1 frozen core.
- The V1 arXiv evaluation.
- Any certified safety claim until V1.1 has passed its full suite of adversarial tests.

## Purpose

V1.1 introduces additive, fail-closed hardening layers wrapping the V1.0.1 Guardian Validator. This adheres to the **SCRAM Principle** by hardening the system boundaries without complicating the core authority.

These layers are intended to mitigate the following *known* V1.0.1 vulnerabilities:
- **Cumulative Risk:** Slow poisoning attacks (total force/energy integral).
- **Protocol Risk:** DoS, parser abuse, and crash risks (via sanitization and timeout).
- **Logical Risk:** Safety-target manipulation (via target blacklisting).
- **Information Risk:** Side-channel leakage (via timing obfuscation).

## Files in Scope (Design Intent Only)

- `runtime/guardian_validator_v1_1.py`
- `runtime/guardian_hardening_v1_1.py`

## Explicit Non-Claims (Legal and Engineering Disclaimer)

The following are NOT claimed for V1.1 at this time:
- Correctness (Must be proven via unit tests).
- Completeness (Resistance to all future adversarial strategies).
- Safety Certification (Requires full adversarial testing and audit).

## V1.1 Evaluation Plan (Future Gate Requirements)

Before V1.1 may be promoted beyond design status and incorporated into the main branch:
1. **Unit Test Pass:** 100% test coverage of all new hardening logic.
2. **Adversarial Test Execution:** Successful VETO against all known V1.1 attack vectors (Slow Poison, DoS attempts).
3. **Fail-Closed Verification:** Proven behavior that any violation results in a clean $\text{VETO}$ (not a software crash).
4. **Documentation:** Results must be documented and signed off, separate from the V1.0.1 audit trail.

## Relationship to V1.0.1 Baseline

- The **V1.0.1 Guardian Validator** remains the sole, deterministic authority.
- V1.1 does not alter:
  - The action set
  - The JSON schema
  - The physical limits (0.5 m/s, 2.0 N)
  - The sequencing rules

All V1.1 logic is **additive, fail-closed, and external** to the core V1.0.1 implementation.
