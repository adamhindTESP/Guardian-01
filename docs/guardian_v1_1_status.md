# Guardian Validator V1.1 — Status & Scope

## Current Status

⚠️ **NOT EVALUATED**  
⚠️ **NOT CERTIFIED**  
⚠️ **NOT USED IN V1.0.1 RESULTS**

The files associated with Guardian Validator V1.1 represent a
**design-complete but untested hardening layer** intended for
future versions of the Guardian architecture.

They are NOT part of:
- The V1.0.1 frozen core
- The V1 arXiv evaluation
- Any certified safety claim

## Purpose

V1.1 introduces **additive hardening layers** around the frozen
V1.0.1 Guardian Validator, without modifying its logic or contract.

These layers are intended to mitigate:
- Cumulative force / slow poisoning attacks
- Protocol-level DoS or parser abuse
- Safety-target manipulation
- Side-channel leakage via timing

## Files in Scope

- `runtime/guardian_validator_v1_1.py`
- `runtime/guardian_hardening_v1_1.py`

## Explicit Non-Claims

The following are NOT claimed for V1.1 at this time:
- Correctness
- Completeness
- Resistance to all adversarial strategies
- Safety certification

## Evaluation Plan (Future)

Before V1.1 may be promoted beyond design status:
1. Unit tests must be written and passed
2. Adversarial test cases must be executed
3. Fail-closed behavior must be verified
4. Results must be documented separately from V1.0.1

Until that time, V1.1 remains **design intent only**.

## Relationship to V1.0.1

- V1.0.1 remains frozen and authoritative
- V1.1 does not alter:
  - Action set
  - JSON schema
  - Physical limits
  - Sequencing rules

All V1.1 logic is additive and external.
