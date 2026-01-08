Guardian-01 Action Set — v1.0.1 (LOCKED)

Status: Frozen
Authority: Guardian Validator v1
Scope: Planner → Guardian execution interface
Guarantee: Deterministic, non-learning, downhill-only

This document defines the complete and closed action grammar permitted for Guardian-01.

Any deviation from this specification results in an automatic veto.

⸻

1. Global Safety Invariants (Non-Negotiable)

These invariants are enforced by the Guardian Validator and cannot be learned, negotiated, or overridden.
	•	Maximum speed: 0.5 m/s
	•	Maximum force: 2.0 N
	•	JSON-only interface
	•	Closed action set
	•	All actions must be validated
	•	Fail-closed (any violation → veto)

⸻

2. Action Plan Structure (REQUIRED)

The planner MUST output a single JSON object of the following form:

{
  "actions": [
    {
      "type": "<action_type>",
      "params": { }
    }
  ]
}

Rules:
	•	actions MUST be non-empty
	•	Actions are evaluated strictly in order
	•	No branching or loops
	•	Maximum 16 actions per plan
	•	No additional top-level keys permitted

⸻

3. Allowed Action Types (CLOSED SET)

Each action MUST specify a type field with one of the following values:
	•	stop
	•	wait
	•	observe
	•	speak
	•	navigate
	•	grasp
	•	release

Any other value → VETO (G1)

This enum is frozen and may only shrink in future versions.

⸻

4. Parameters (params) — OPTIONAL AND BOUNDED

The params object MAY be omitted if an action requires no parameters.

If present, it may contain only the following keys:

Parameter	Type	Bounds
target	string	canonical identifier
duration_s	number	0.0 ≤ value ≤ 30.0
speed_mps	number	0.0 ≤ value ≤ 0.5
force_n	number	0.0 ≤ value ≤ 2.0
utterance	string	max 200 characters

	•	Any unknown parameter → VETO (G1)
	•	Any out-of-bounds value → VETO (G2)

⸻

5. Target Semantics (v1)

When present, target MUST be a simple string identifier:

{
  "type": "grasp",
  "params": {
    "target": "water_glass",
    "force_n": 0.5
  }
}

Structured objects, expressions, or references are not permitted in v1.

⸻

6. Sequencing Safety Rules (HARD)

These rules are not learned.

They are enforced deterministically by
runtime/guardian_validator.py as part of G3 (Sequencing Safety).
	•	grasp requires a prior observe
	•	release requires a prior grasp
	•	navigate is forbidden immediately after grasp

Violations → VETO (G3)

⸻

7. Forbidden Content (HARD VETO)

The planner MUST NOT emit any of the following keys anywhere in output:

risk
safety
dignity
confidence
score
justification
explanation
analysis
reasoning

Planner self-reporting is prohibited.

⸻

8. Execution Authority

Passing this action set does not authorize execution.

All plans are proposals only.
Final authority remains with the Guardian.

⸻

9. Freeze Declaration

This action set is frozen for Guardian Seed v1.0.1.

Any change requires:
	1.	New schema version
	2.	Validator update
	3.	Re-running certification tests
	4.	Version bump
