Guardian-01 Action Set — v1.0.1 (LOCKED)

⸻

Purpose

This document describes the deterministic, safety-bounded action grammar used by Guardian-01.

It defines the only execution proposals that an untrusted planner may submit for validation.

Scope
	•	Household
	•	Assisted-living
	•	Safety-critical environments

Hard Safety Limits (Non-Negotiable)
	•	Maximum speed: 0.5 m/s
	•	Maximum force: 2.0 N

These limits are enforced by the Guardian Validator and cannot be overridden, learned, or adapted.

⸻

⚠️ Normative Authority (Critical)

This document is descriptive.

The normative, authority-bearing execution contract for Guardian Seed v1.0.1 is defined exclusively by:
	•	schema/guardian01_action_contract_v1.schema.json
	•	runtime/guardian_validator.py

If any conflict exists between this document and the schema or validator,
the schema and validator take precedence.

⸻

Core Safety Principle

The Guardian action set is:
	•	Closed (no custom or user-defined actions)
	•	Downhill-only (future versions may only restrict, never expand, authority)
	•	Non-learning (no adaptation, inference, or state accumulation)
	•	Fail-closed (any violation → veto)

The Guardian never reasons.
It only accepts or vetoes proposals.

⸻

Action List (Complete and Enforced)

The following actions constitute the entire permitted execution vocabulary for v1.0.1:

stop
wait
observe
speak
navigate
grasp
release

No other action types are valid.

Actions such as plan_route, manipulate, or navigate_step are planner-internal concepts and are not executable primitives in v1.0.1.

⸻

General Action Structure

All execution proposals MUST conform to this structure:

{
  "actions": [
    {
      "type": "<action_name>",
      "params": {
        "...": "..."
      }
    }
  ]
}

Rules:
	•	Actions are ordered
	•	No branching
	•	No loops
	•	No conditionals
	•	Maximum sequence length is enforced by schema

⸻

Action Definitions

1. stop

Purpose:
Immediately halt motion or activity.

Params:
None

{ "type": "stop" }


⸻

2. wait

Purpose:
Pause execution for a bounded duration.

Params:
	•	duration_s (required): 0.0 ≤ duration ≤ 30.0

{
  "type": "wait",
  "params": { "duration_s": 5.0 }
}


⸻

3. observe

Purpose:
Perform a perception update before physical interaction.

Params:
None required

{ "type": "observe" }


⸻

4. speak

Purpose:
Produce human-facing speech only.

Params:
	•	utterance (required, max 200 chars)

{
  "type": "speak",
  "params": { "utterance": "Please stand clear." }
}

Speech may not:
	•	Contain reasoning
	•	Issue commands to other systems
	•	Explain policy or safety logic

⸻

5. navigate

Purpose:
Move toward a named location or object.

Params:
	•	target (required): canonical string identifier
	•	speed_mps (optional, ≤ 0.5)

{
  "type": "navigate",
  "params": {
    "target": "kitchen",
    "speed_mps": 0.2
  }
}


⸻

6. grasp

Purpose:
Physically grasp an object.

Params:
	•	target (required)
	•	force_n (optional, ≤ 2.0)

{
  "type": "grasp",
  "params": {
    "target": "water_glass",
    "force_n": 0.3
  }
}


⸻

7. release

Purpose:
Release a previously grasped object.

Params:
	•	target (required)

{
  "type": "release",
  "params": { "target": "water_glass" }
}


⸻

Sequencing Safety Rules (Enforced)

The following rules are hard safety constraints enforced by the Guardian Validator:
	•	grasp requires a prior observe
	•	release requires a prior grasp
	•	navigate is forbidden immediately after grasp
	•	Any violation → VETO

These are structural rules, not learned behavior.

⸻

Canonical Valid Example

{
  "actions": [
    { "type": "navigate", "params": { "target": "water_glass" } },
    { "type": "observe" },
    { "type": "grasp", "params": { "target": "water_glass", "force_n": 0.3 } }
  ]
}

This proposal:
	•	Uses only allowed actions
	•	Respects sequencing
	•	Respects force limits
	•	Is structurally valid

⸻

Explicit Non-Goals

This action set does not provide:
	•	Route planning
	•	Intent inference
	•	Human following
	•	Autonomous task decomposition
	•	High-force manipulation
	•	Adaptive behavior

Those capabilities, if added, require new gates and new versions.

⸻

Versioning & Freeze Status

Version: v1.0.1
Status: LOCKED
	•	Action vocabulary frozen
	•	Parameter bounds frozen
	•	Sequencing rules frozen
	•	Validator behavior frozen

Any change requires:
	1.	New semantic version
	2.	Re-running certification tests
	3.	Updating GATES.md

⸻

Design Philosophy (Invariant)

The planner may reason freely.
The Guardian never does.

The Guardian only answers one question:

“Does this proposal satisfy the contract?”

If not — VETO.
