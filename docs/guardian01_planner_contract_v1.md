Guardian-01 Planner JSON Contract (v1.0.1)

Status: Frozen
Applies to: Planner training & evaluation
Authority: schema/guardian01_action_contract_v1.schema.json
Enforced by: runtime/guardian_validator.py

This document defines the only valid JSON output a planner may emit.
Any deviation results in an automatic Guardian veto.

⸻

1. Top-Level Structure (REQUIRED)

The planner MUST output a single JSON object of the following form:

{
  "actions": [
    {
      "type": "<action_type>",
      "params": { }
    }
  ]
}

No additional top-level keys are permitted.

⸻

2. actions (REQUIRED)
	•	MUST be a non-empty array
	•	MUST be ordered (no branching, no loops)
	•	MUST contain at most 16 actions
	•	Actions are evaluated strictly in sequence

⸻

3. type (REQUIRED)

Each action object MUST include a type field.

Allowed values (CLOSED SET):

stop
wait
observe
speak
navigate
grasp
release

Any other value → VETO (G1)

This enum is frozen and may only shrink in future versions.

⸻

4. params (OPTIONAL)
	•	The params object MAY be omitted if the action requires no parameters
	•	If present, params MUST contain only allowed keys
	•	No inferred, adaptive, or computed values are permitted

Allowed parameter keys:

Parameter	Type	Bounds
target	string	canonical identifier
duration_s	number	0.0 ≤ value ≤ 30.0
speed_mps	number	0.0 ≤ value ≤ 0.5
force_n	number	0.0 ≤ value ≤ 2.0
utterance	string	max 200 chars

Any out-of-bounds value → VETO (G2)
Any unknown parameter → VETO (G1)

⸻

5. Target Semantics

When present, target MUST be a string identifier only:

"params": {
  "target": "water_glass"
}

Structured targets (objects, expressions, references) are not permitted in v1.

⸻

6. Forbidden Fields (HARD VETO)

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

7. Formatting Rules (STRICT)
	•	Output MUST be valid JSON
	•	No comments
	•	No markdown
	•	No trailing commas
	•	No text before or after JSON

Invalid JSON → VETO (G1)

⸻

8. Execution Authority

Passing this contract does not authorize execution.

All planner outputs are proposals only.
Final authority remains with the Guardian Validator.

⸻

9. Freeze Declaration

This planner contract is frozen for Guardian Seed v1.0.1.

Any change requires:
	1.	New schema version
	2.	Validator update
	3.	Re-run of certification tests
	4.	Version bump
