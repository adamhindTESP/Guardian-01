GATES.md — Guardian Architecture Safety Gates

Verifiable Safety Certification for LLM-Driven Physical Systems

⸻

Purpose

This document defines explicit, test-verifiable safety gates for the Guardian architecture.
A gate is considered PASSED only with executable test evidence.

No gate advancement without passing tests.
No claims beyond the highest verified gate.

⸻

Current Certification Status

Highest Passed Gate: G3.5 — Software Safety Stack Complete

Evidence:
	•	21 / 21 tests passing
	•	0 unsafe escapes
	•	Full audit trail for every decision

⸻

Gate Status Summary

Gate	Status	Evidence	Date	Tests
G0	✅ PASS	Architecture frozen	2026-01-02	N/A
G1	✅ PASS	Simulation safety verified	2026-01-02	Adversarial sim
G2	✅ PASS	Deterministic policy kernel	2026-01-02	Unit tests
G3	✅ PASS	Trajectory & temporal safety	2026-01-02	11 / 11
G3.5	✅ PASS	Full software integration	2026-01-02	10 / 10
G4	⏳ NEXT	Hardware governor	Planned	Hardware
G5	⏳ FUTURE	Robot field integration	Future	Field tests


⸻

Maximum Verified Claim (Strict)

“Guardian implements a complete, verifiable software safety stack (G1–G3.5) that deterministically produces a single FINAL_PASS or VETO decision, with full audit trails and zero unsafe escapes across 21 tests. The system is ready for hardware enforcement (G4).”

⸻

Architecture Overview (Dual-Veto Model)

LLM (Untrusted)
   ↓
G1 — Validator
   ↓
G2 — Policy Kernel
   ↓
G3 — Trajectory Planner
   ↓
G3.5 — Safety Coordinator
   ↓
[ FINAL_PASS | VETO ]
   ↓
G4 — Hardware Governor (future)

Invariant:

If ANY gate vetoes → NO EXECUTION.

⸻

Gate Definitions & Evidence

G0 — Architecture Freeze ✅

Purpose: Enforce strict separation of reasoning, planning, and execution.
Evidence: Repository structure and frozen interfaces.
Claim: Architecture is fixed and auditable.

⸻

G1 — Simulation Safety ✅

Purpose: Demonstrate zero unsafe actions under adversarial simulation.
Evidence: Stress simulations with conservative fallback behavior.
Claim: Unsafe behaviors are reliably detected in simulation.

⸻

G2 — Policy Kernel ✅

Purpose: Deterministic semantic safety evaluation.
Rules:
	•	Risk > threshold → VETO
	•	Dignity below threshold → VETO

Code: guardian_seed.py
Evidence: Unit tests passing.
Claim: No probabilistic or learned behavior at policy level.

⸻

G3 — Trajectory & Temporal Safety ✅

Purpose: Prevent unsafe motion and unsafe repetition patterns.

Code: trajectory_planner.py
Tests: test_g3_trajectory_safety.py

Verified Properties:
	•	Danger → NEVER PASSED
	•	Temporal repetition detection active
	•	Conservative vetoes explicitly allowed
	•	0 unsafe escapes in 1000-cycle endurance test

Result: 11 / 11 tests passed

Command:

python -m pytest test_g3_trajectory_safety.py -v


⸻

G3.5 — Safety Coordinator Integration ✅

Purpose: Single authoritative decision pipeline.

Code: safety_coordinator.py
Tests: test_safety_coordinator.py

Verified Properties:
	•	G1 → G2 → G3 enforced in order
	•	Single check_proposal() API
	•	Complete audit trail (AuditRecord) per decision
	•	Reset behavior verified
	•	Conservative vetoes preserved
	•	Endurance test passed (100 decisions)

Result: 10 / 10 tests passed

Command:

python -m pytest test_safety_coordinator.py -v


⸻

Verification Commands

# Run full certification (21 tests)
python -m pytest -v

# Individual gates
python -m pytest test_g3_trajectory_safety.py -v
python -m pytest test_safety_coordinator.py -v

# Demo (non-certification)
python safety_coordinator.py


⸻

Claim Limitations (Non-Negotiable)

Allowed	Forbidden
“Software safety stack verified”	“Physically safe”
“Zero unsafe escapes in tests”	“Safe in real world”
“Ready for G4 hardware”	“Tamper-proof”
“Auditable execution control”	“General intelligence safety”


⸻

Core File Map

guardian_seed/
├── GATES.md                     # Certification authority
├── validator_module.py          # G1
├── guardian_seed.py             # G2
├── trajectory_planner.py        # G3
├── safety_coordinator.py        # G3.5
├── test_g3_trajectory_safety.py # G3 tests (11)
├── test_safety_coordinator.py   # G3.5 tests (10)


⸻

Next Gate: G4 — Hardware Governor

Objective: Make software vetoes physically unavoidable.

Requirements (Preview):
	•	Independent MCU (Teensy 4.x)
	•	Current / force sensing
	•	Watchdog-enforced safety loop
	•	Ignores disable / override commands
	•	<50 ms hard cutoff latency

⸻

Status:
🟢 Software stack complete
🟡 Hardware enforcement next

Last Updated: 2026-01-02

