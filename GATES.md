Guardian Architecture Safety Gates

Normative Certification Authority

⸻

Purpose

This document defines the only authoritative safety certification gates
for the Guardian Architecture.

A gate is a formally defined execution-safety capability that may only be
claimed when supported by executable, auditable evidence.

This file governs what safety claims are permitted — not philosophical,
ethical, or social interpretations of safety.

Design rationale and intent preservation are recorded separately in
DECISIONS.md.

This file is normative.

⸻

Scope Clarification (Normative)

Guardian gates do not implement moral reasoning
(neither deontological nor consequential).

They implement execution constraints only:
	•	contract validity
	•	bounded actions
	•	deny-lists
	•	deterministic policy checks
	•	trajectory and temporal safety

Terms such as harm, dignity, stewardship, or comfort are
labels for explicit, testable veto conditions —
not ethical judgments or value claims.

Guardian does not reason about:
	•	intent
	•	justice
	•	truthfulness
	•	downstream social consequences
	•	moral dilemmas

Any proposal outside Guardian’s strictly defined physical and symbolic domain
is out of scope and must be vetoed.

⸻

Non-Negotiable Rules
	•	No gate advancement without passing tests
	•	No safety claim beyond the highest verified gate
	•	Any veto → no execution
	•	Conservative vetoes are explicitly allowed
	•	Inputs may be strengthened without advancing gates
	•	Evaluation artifacts do not grant execution authority
	•	Design-only artifacts do not grant safety claims

⸻

Freeze Declaration (Normative)

The following artifacts are frozen and authority-bearing
for Guardian Seed v1.0.1.

Execution-Critical (Authority-Bearing)
	•	Action Contract (G1)
schema/guardian01_action_contract_v1.schema.json
	•	Guardian Validator (G1 Enforcement Kernel)
runtime/guardian_validator.py
	•	Deterministic Policy Kernel (G2)
runtime/guardian_policy_kernel.py
	•	Trajectory & Temporal Safety (G3)
runtime/trajectory_safety.py
	•	Safety Coordinator (G3.5 — Single Authority API)
runtime/safety_coordinator.py

These artifacts:
	•	MUST NOT learn or adapt
	•	MUST NOT be bypassed
	•	MUST fail closed
	•	MUST be versioned and audited

Any modification requires:
	1.	Semantic version bump
	2.	Re-running all certification tests
	3.	Updating this document with new evidence

⸻

Certification / Measurement (Non-Authoritative)
	•	Guardian Evaluator (Audit Harness)
evaluation/guardian_evaluator.py

The evaluator:
	•	Produces measurement evidence only
	•	Has no execution authority
	•	Is not a safety gate

⸻

Explicitly Non-Normative Artifacts (Design-Only)

The repository may include forward-looking designs.
The following are explicitly excluded from certification:
	•	runtime/guardian_validator_v1_1.py
	•	runtime/guardian_hardening_v1_1.py
	•	Any file marked DESIGN-ONLY / NOT EVALUATED

These artifacts:
	•	❌ Do not participate in any gate
	•	❌ Do not grant execution authority
	•	❌ Do not modify frozen G1–G3.5 behavior
	•	❌ Do not constitute evidence

⸻

Current Certification Status

Highest Passed Gate: G3.5 — Unified Software Safety Stack Complete

Verified Evidence
	•	All certification tests passing
	•	Zero unsafe executions passing all gates under test conditions
	•	Deterministic behavior for identical inputs
	•	Complete audit record for every proposal

The system is software-complete and hardware-ready,
but not hardware-certified.

⸻

Gate Status Summary

Gate	Scope	Status	Evidence Type
G0	Architecture freeze	✅ PASS	Structural review
G1	Action contract enforcement	✅ PASS	Schema + validator tests
G2	Deterministic policy kernel	✅ PASS	Unit tests
G3	Trajectory & temporal safety	✅ PASS	Motion tests
G3.5	Unified software authority	✅ PASS	Integration tests
G4	Hardware governor	⏳ NEXT	Physical tests
G5	Field-integrated autonomy	⏳ FUTURE	Real-world trials

No claim is valid beyond G3.5.

⸻

Maximum Verified Claim (Strict)

“Guardian implements a complete, verifiable software execution-safety stack
(G1–G3.5) that deterministically produces a single FINAL_PASS or VETO
decision, with full audit trails and zero unsafe executions passing all gates
under test conditions. The system is ready for hardware enforcement (G4).”

No stronger claim is permitted.

⸻

Architecture Overview (Invariant)

LLM (Untrusted Reasoning)
        ↓
G1 — Action Contract Enforcement
        ↓
G2 — Deterministic Policy Kernel
        ↓
G3 — Trajectory & Temporal Safety
        ↓
G3.5 — Safety Coordinator (Single Authority)
        ↓
      [ FINAL_PASS | VETO ]
        ↓
G4 — Hardware Governor (future)

Invariant:
If ANY gate vetoes → NO EXECUTION
There are no exceptions.

⸻

Gate Definitions & Evidence

⸻

G0 — Architecture Freeze ✅

Purpose
Enforce strict separation between reasoning, evaluation, and execution authority.

Verified Properties
	•	LLMs never control actuators or external APIs
	•	All execution passes through explicit gates
	•	No gate may be bypassed
	•	Interfaces are fixed and auditable

Claim
Authority separation is structural and non-emergent.

⸻

G1 — Action Contract Enforcement ✅

Purpose
Reject malformed, unsafe, or out-of-bounds proposals before semantic evaluation.

Normative Artifacts
	•	schema/guardian01_action_contract_v1.schema.json
	•	runtime/guardian_validator.py

Verified Properties
	•	Only schema-valid JSON is accepted
	•	Closed action set enforced
	•	Hard parameter bounds enforced
	•	Invalid structure or sequencing → VETO
	•	No reliance on model self-reports

Fail-Closed Robustness (G1 — Strengthened Property)
The validator MUST:
	•	Veto empty, malformed, or partial input
	•	Enforce max input size (e.g., ≤64 KB)
	•	Enforce max nesting depth and list lengths
	•	Veto Unicode floods, null bytes, pathological inputs
	•	Veto on any internal exception

At no point may the validator:
	•	crash
	•	hang
	•	fail open

Evidence
	•	tests/test_failsafe_basic.py

Claim
Only contract-conforming proposals may proceed under tested conditions.

⸻

G2 — Deterministic Policy Kernel ✅

Purpose
Apply semantic execution constraints using deterministic logic.

Normative Artifact
	•	runtime/guardian_policy_kernel.py

Verified Properties
	•	Rule-based, non-learning
	•	Deterministic outputs for identical inputs
	•	Uses frozen, audited policy data
	•	Violations of policy constraints → VETO

Claim
Policy decisions are deterministic and auditable.

⸻

G3 — Trajectory & Temporal Safety ✅

Purpose
Prevent unsafe motion patterns and unsafe repetition.

Normative Artifact
	•	runtime/trajectory_safety.py

Verified Properties
	•	Unsafe trajectories vetoed
	•	Temporal repetition limits enforced
	•	Conservative vetoes preserved

Claim
Unsafe motion patterns are rejected under test conditions.

⸻

G3.5 — Safety Coordinator Integration ✅

Purpose
Provide a single authoritative execution decision.

Normative Artifact
	•	runtime/safety_coordinator.py

Verified Properties
	•	G1 → G2 → G3 enforced in strict order
	•	Single check_proposal() authority
	•	Full audit record generated
	•	Endurance and reset behavior verified

Claim
The software safety stack operates as a unified authority.

⸻

Certified Policy Substrate (Input Artifact)

Guardian Seed v1 is a frozen, audited input dataset to G2.

Properties
	•	Semantically normalized records
	•	Context-aware stop semantics
	•	Deterministic limit derivation
	•	Immutable, versioned artifact

Status
	•	✅ Verified input
	•	❌ Not a gate
	•	❌ No veto authority
	•	❌ No independent safety claim

Policy authority resides in G2, not the dataset.

⸻

Verification Commands

# Full certification
python -m pytest -v

# Individual gates
python -m pytest tests/test_g3_trajectory_safety.py -v
python -m pytest tests/test_safety_coordinator.py -v

# Demonstration only (non-certifying)
python runtime/safety_coordinator.py


⸻

Claim Limitations (Non-Negotiable)

Allowed Claims	Forbidden Claims
Software safety stack verified	Physically safe
Zero unsafe executions in tests	Safe in real world
Auditable execution control	General intelligence safety
Ready for hardware enforcement	Moral reasoning
Deterministic veto authority	Intent understanding


⸻

Core File Map (Certified Set)

schema/
└── guardian01_action_contract_v1.schema.json

runtime/
├── guardian_validator.py
├── guardian_policy_kernel.py
├── trajectory_safety.py
└── safety_coordinator.py

evaluation/
└── guardian_evaluator.py

tests/
├── test_failsafe_basic.py
├── test_g3_trajectory_safety.py
└── test_safety_coordinator.py

Files outside this set do not participate in certification.

⸻

Next Gate — G4: Hardware Governor (Planned)

Objective
Make software vetoes physically unavoidable.

Planned Requirements
	•	Independent MCU
	•	Current / force sensing
	•	Watchdog-enforced cutoff
	•	Override-immune design
	•	<50 ms hard stop latency

Status
No G4 claims are valid until hardware tests pass.

⸻

Status

🟢 Software safety stack complete (G3.5)
🟡 Hardware enforcement next (G4)

⸻

Version History

v1.0.0 — Architectural Freeze
January 04, 2026

v1.0.1 — First Normative Freeze (CURRENT)
January 07, 2026
Complete software safety stack (G1–G3.5)

⸻

“He who knows when he can fight and when he cannot, will be victorious.”
— Sun Tzu
