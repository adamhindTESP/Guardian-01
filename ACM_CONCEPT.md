Adaptive Constraint Manager (ACM) — Concept & Design Intent

Status: Design Placeholder (Not Implemented)
Version: Draft v0.1
Applies To: Guardian-01 (Future V2+)
Last Updated: 2026-01-05

⸻

1. Purpose

The Adaptive Constraint Manager (ACM) is a future, deterministic control layer designed to adjust numerical safety limits enforced by the Guardian without ever transferring authority to a learned system.

The ACM exists to answer a single question:

How can an autonomous planner earn higher performance (speed, force, dexterity) through demonstrated reliability, while preserving absolute safety guarantees?

The ACM does not replace the Guardian.
The ACM does not modify Guardian rules.
The ACM does not learn.

⸻

2. Core Safety Invariant

Authority never transfers to the Planner.

At all times:
	•	The Planner proposes
	•	The Guardian decides
	•	The ACM only adjusts numeric limits within hard ceilings

If the ACM fails, is disabled, or behaves unexpectedly:
	•	The system reverts immediately to conservative default limits.

⸻

3. What the ACM Is

The ACM is a deterministic, auditable constraint calculator that:
	•	Reads Guardian audit logs
	•	Computes a trust score
	•	Outputs current allowable limits
	•	Never approves actions
	•	Never interprets intent
	•	Never overrides vetoes

The Guardian remains the final execution authority.

⸻

4. What the ACM Is NOT

The ACM is not:
	•	A learned model
	•	A neural network
	•	A reinforcement learner
	•	A reward mechanism
	•	A planner
	•	A safety classifier
	•	A substitute for Guardian veto logic

The ACM does not decide safety.
It only sets how conservative the Guardian must be.

⸻

5. Architectural Placement

Planner (LLM, learned)
   │
   ▼
Guardian (G1–G3)  ← Final authority (immutable)
   │
   ▼
ACM (deterministic, optional)
   │
   ▼
Numeric Limits (speed, force, etc.)

Important:
The Planner has no visibility into ACM state, thresholds, or trust scores.

⸻

6. Inputs (Read-Only)

The ACM may only read:
	•	Guardian audit logs
	•	Veto reasons (G1 / G2 / G3)
	•	Execution outcomes (PASS / VETO)
	•	Environmental safety flags (from Guardian-approved sensors)

The ACM may never read:
	•	Planner internal states
	•	Planner logits
	•	Planner reasoning traces
	•	Planner prompts
	•	Planner training data

⸻

7. Outputs (Constrained)

The ACM outputs only numeric parameters, such as:
	•	max_speed_mps
	•	max_force_n
	•	max_joint_torque_nm
	•	max_reach_distance_m

All outputs must satisfy:

default_safe_limit ≤ current_limit ≤ hard_ceiling

Hard ceilings are never exceeded.

⸻

8. Trust Score (Conceptual)

The ACM may compute a trust score using metrics such as:
	•	Rolling veto rate (e.g., last 100 proposals)
	•	Ratio of G2 (policy) vs G3 (contextual) vetoes
	•	Consecutive safe passes
	•	Absence of policy violations

Example (illustrative only):

if veto_rate < 5% and no G2 violations in last 100 actions:
    increase limits slightly
else:
    decrease limits or revert to defaults

All calculations must be:
	•	Deterministic
	•	Stateless beyond bounded windows
	•	Fully auditable

⸻

9. Envelope Expansion Rules

Envelope expansion is:
	•	Incremental
	•	Reversible
	•	Context-dependent
	•	Capped

Example constraints:
	•	Speed increases in steps (e.g., +0.1 m/s)
	•	Immediate collapse on any G2 policy violation
	•	Automatic reset in presence of humans or hazards
	•	Absolute ceilings defined at compile time

⸻

10. Failure Behavior (Fail-Safe)

On any of the following:
	•	ACM error
	•	Missing logs
	•	Unexpected input
	•	Invalid output
	•	Manual override

The system must:
	•	Revert to V1 conservative limits
	•	Continue operation under Guardian enforcement
	•	Log the event

⸻

11. Training Relationship

The Planner is NOT trained with ACM enabled.

Reasons:
	•	Prevents reward hacking
	•	Avoids “appearing safe” optimization
	•	Preserves structural safety guarantees

The Planner is trained as if limits are fixed.
Any later expansion is an environmental fact, not a learned incentive.

⸻

12. Implementation Status

Component	Status
Guardian	Implemented & Frozen (V1)
Planner	Learned (LoRA fine-tuning)
ACM Logic	❌ Not implemented
ACM Interface	❌ Not implemented
This Document	✅ Design intent only


⸻

13. Versioning & Activation Policy
	•	ACM must not be enabled in Guardian-01 V1.x
	•	Any future activation requires:
	•	New major version
	•	Independent review
	•	Updated safety tests
	•	Explicit documentation

⸻

14. Summary

The ACM is a future capability-scaling mechanism, not a safety mechanism.

Safety is guaranteed by:
	•	Immutable Guardian rules
	•	Hard ceilings
	•	Deterministic veto authority

The ACM exists to allow:
	•	Skill acquisition
	•	Dexterity growth
	•	Earned autonomy

Without ever compromising safety.

⸻

End of Document
