# Guardian-01 Planner JSON Contract (v1)

**Status:** Locked  
**Applies to:** Phase 3+ (Planner Learning)  
**Authority:** Guardian Validator v1  
**Scope:** Planner output format ONLY

This document defines the **only valid JSON output** a planner may emit.
Any deviation results in an **automatic Guardian veto**.

---

## 1. Top-Level Structure (REQUIRED)

The planner MUST output a single JSON object with the following structure:

```json
{
  "schema_version": "guardian01_action_set_v1",
  "goals": [],
  "parameters": {}
}

No additional top-level keys are permitted.

⸻

2. schema_version (REQUIRED)

"schema_version": "guardian01_action_set_v1"

	•	MUST be present
	•	MUST match exactly
	•	Any mismatch → veto

⸻

3. goals (REQUIRED)

goals MUST be a non-empty array of action objects.

"goals": [
  {
    "action": "<action_type>",
    "target": { ... },
    "params": { ... }
  }
]


⸻

4. Allowed Actions (CLOSED SET)

The action field MUST be one of the following strings:
	•	"navigate"
	•	"navigate_step"
	•	"observe"
	•	"speak"
	•	"grasp"
	•	"release"
	•	"stop"
	•	"wait"
	•	"plan_route"
	•	"manipulate"

Any other action → veto

⸻

5. target Object (REQUIRED for actions that reference the world)

When present, target MUST be an object of the form:

{
  "kind": "location" | "object",
  "id": "<string>"
}

Rules:
	•	kind MUST be "location" or "object"
	•	id MUST be a string
	•	Missing or malformed target → veto

⸻

6. params Object (OPTIONAL)

Each goal MAY include a params object.

Allowed parameter keys:
	•	target_speed_mps
	•	max_force_n
	•	observe_duration_s
	•	reobservation_s

Example:

"params": {
  "target_speed_mps": 0.15,
  "max_force_n": 0.5
}

All numeric values are validated against Guardian physical limits.

Out-of-bounds values → veto

⸻

7. parameters (OPTIONAL, TOP-LEVEL)

The top-level parameters object MAY be present to define shared defaults.

"parameters": {
  "target_speed_mps": 0.15
}

Defaults may be overridden per-goal.

⸻

8. Forbidden Fields (HARD VETO)

The planner MUST NOT include any of the following keys anywhere in output:
	•	risk
	•	safety
	•	dignity
	•	confidence
	•	score
	•	justification
	•	explanation
	•	analysis
	•	reasoning

Planner self-reporting is prohibited.

⸻

9. Formatting Rules (STRICT)
	•	Output MUST be valid JSON
	•	No comments
	•	No trailing commas
	•	No markdown
	•	No prose
	•	No additional text before or after JSON

Invalid JSON → automatic veto

⸻

10. Execution Authority

Passing this contract does not authorize execution.

All outputs are proposals only.
Final execution authority remains with the Guardian Validator.

⸻

This contract is immutable once training begins.
Changes require a new schema version and restart at Phase 0.

