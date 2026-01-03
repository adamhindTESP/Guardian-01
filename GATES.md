GATES.md — Guardian Architecture Safety Gates

Verifiable Safety Certification for LLM-Driven Execution Systems

⸻

Purpose

This document defines explicit, test-verifiable safety gates for the Guardian architecture.

A gate is considered PASSED only with executable test evidence.
	•	No gate advancement without passing tests
	•	No claims beyond the highest verified gate
	•	Conservative vetoes are explicitly allowed

This document is the sole certification authority for safety claims in this repository.

⸻

Current Certification Status

Highest Passed Gate: G3.5 — Software Safety Stack Complete

Verified Evidence:
	•	21 / 21 certification tests passing
	•	0 unsafe executions passing all gates under test conditions
	•	Deterministic behavior across all tested paths
	•	Complete audit trail produced for every decision

⸻

Gate Status Summary

Gate	Scope	Status	Evidence	Date	Tests
G0	Architecture freeze	✅ PASS	Interfaces frozen	2026-01-02	N/A
G1	Simulation safety	✅ PASS	Adversarial simulation	2026-01-02	Sim cycles
G2	Policy kernel	✅ PASS	Deterministic rules	2026-01-02	Unit tests
G3	Trajectory & temporal safety	✅ PASS	Motion + repetition checks	2026-01-02	11 / 11
G3.5	Full software integration	✅ PASS	Unified decision authority	2026-01-02	10 / 10
G4	Hardware governor	⏳ NEXT	Physical enforcement	Planned	Hardware
G5	Field-integrated autonomy	⏳ FUTURE	Real-world testing	Future	Field


⸻

Maximum Verified Claim (Strict)

“Guardian implements a complete, verifiable software safety stack (G1–G3.5) that deterministically produces a single FINAL_PASS or VETO decision, with full audit trails and zero unsafe executions passing all gates under test conditions. The system is ready for hardware enforcement (G4).”

No stronger claim is permitted.

⸻

Architecture Overview (Dual-Veto Model)

LLM (Untrusted Reasoning)
        ↓
G1 — Validator (Schema + Bounds)
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

Invariant

If ANY gate vetoes → NO EXECUTION.

No exceptions.

⸻

Gate Definitions & Evidence

⸻

G0 — Architecture Freeze ✅

Purpose
Enforce strict separation between reasoning, evaluation, and execution authority.

Evidence
	•	Repository structure
	•	Frozen interfaces between gates
	•	No execution path bypasses gates

Claim
Architecture is fixed, auditable, and non-emergent.

⸻

G1 — Simulation Safety ✅

Purpose
Reject malformed, unsafe, or out-of-bounds proposals before policy evaluation.

Evidence
	•	Adversarial simulation cycles
	•	Schema-locked structured input
	•	Independent metric computation
	•	Conservative rejection behavior

Verified Properties
	•	Malformed or non-conforming proposals are rejected
	•	Known unsafe patterns are deterministically detected under adversarial simulation scenarios
	•	No reliance on LLM self-reported safety claims

Claim
Unsafe patterns are reliably rejected in simulation under tested conditions.

⸻

G2 — Policy Kernel ✅

Purpose
Deterministic semantic safety evaluation.

Rules
	•	Risk above threshold → VETO
	•	Dignity below threshold → VETO
	•	No learned or probabilistic behavior

Code
guardian_seed.py

Evidence
	•	Unit tests passing
	•	Deterministic outputs for identical inputs

Claim
Policy decisions are deterministic, auditable, and rule-based.

⸻

G3 — Trajectory & Temporal Safety ✅

Purpose
Prevent unsafe motion and unsafe repetition patterns.

Code
trajectory_planner.py

Tests
test_g3_trajectory_safety.py

Verified Properties
	•	Deterministically defined danger states → NEVER PASSED
	•	Temporal repetition detection enforced
	•	Conservative vetoes preserved
	•	0 unsafe executions passing gates in 1000-cycle endurance test

Result
11 / 11 tests passed

Command

python -m pytest test_g3_trajectory_safety.py -v


⸻

G3.5 — Safety Coordinator Integration ✅

Purpose
Provide a single authoritative decision pipeline.

Code
safety_coordinator.py

Tests
test_safety_coordinator.py

Verified Properties
	•	G1 → G2 → G3 enforced in strict order
	•	Single check_proposal() API
	•	Complete AuditRecord generated per decision
	•	Reset behavior verified
	•	Conservative vetoes preserved
	•	Endurance test passed (100 decisions)

Result
10 / 10 tests passed

Command

python -m pytest test_safety_coordinator.py -v


⸻

Verification Commands

# Full certification (21 tests)
python -m pytest -v

# Individual gates
python -m pytest test_g3_trajectory_safety.py -v
python -m pytest test_safety_coordinator.py -v

# Demo (non-certifying)
python safety_coordinator.py


⸻

Claim Limitations (Non-Negotiable)

Allowed Claims	Forbidden Claims
“Software safety stack verified”	“Physically safe”
“Zero unsafe executions in tests”	“Safe in the real world”
“Ready for G4 hardware enforcement”	“Tamper-proof”
“Auditable execution control”	“General intelligence safety”
“Safety depends on gate enforcement”	“Model alignment guarantee”


⸻

Core File Map

guardian_seed/
├── GATES.md                     # Certification authority
├── validator_module.py          # G1 — schema + bounds validation
├── guardian_seed.py             # G2 — deterministic policy kernel
├── trajectory_planner.py        # G3 — trajectory & temporal safety
├── safety_coordinator.py        # G3.5 — unified decision authority
├── test_g3_trajectory_safety.py # G3 tests (11)
├── test_safety_coordinator.py   # G3.5 tests (10)

Files outside this set do not participate in certification.

⸻

Next Gate: G4 — Hardware Governor

Objective
Make software vetoes physically unavoidable.

Planned Requirements
	•	Independent MCU (e.g., Teensy 4.x)
	•	Current / force sensing
	•	Watchdog-enforced safety loop
	•	Ignores disable / override commands
	•	<50 ms hard cutoff latency

No G4 claims are valid until hardware tests pass.

⸻

Status

🟢 Software safety stack complete (G3.5)
🟡 Hardware enforcement next (G4)

Last Updated: 2026-01-02

⸻

Maximum capability through minimum authority.
Maximum service through restraint.


