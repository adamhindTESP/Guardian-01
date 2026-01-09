Absolutely. Below is a clean, repo-ready rewrite of GATES.md that:
	•	Preserves all existing claims and gates
	•	Explicitly excludes V1.1 and other design-only artifacts
	•	Aligns with DECISIONS.md governance
	•	Does NOT advance any gate
	•	Tightens language for arXiv / audit / fork safety

You can replace your current GATES.md with this verbatim.

⸻


# Guardian Architecture Safety Gates  
**Normative Certification Authority**

---

## Purpose

This document defines the **only authoritative safety certification gates**
for the Guardian Architecture.

A **gate** is a formally defined safety capability that may only be claimed
when supported by **executable, auditable evidence**.

This file is the **sole source of truth** for all safety claims made by this
repository.

Design rationale for architectural and safety constraints is recorded
separately in **DECISIONS.md**.

---

## Non-Negotiable Rules

- **No gate advancement without passing tests**
- **No safety claim beyond the highest verified gate**
- **Conservative vetoes are explicitly allowed**
- **Inputs may be strengthened without advancing gates**
- **Evaluation artifacts do not grant execution authority**
- **Design-only artifacts do not grant safety claims**

---

## Freeze Declaration (Normative)

The following artifacts are **frozen and normative** for the current
Guardian Seed release.

### Execution-Critical (Authority-Bearing)

- **Action Contract (G1)**  
  `schema/guardian01_action_contract_v1.schema.json`

- **Guardian Validator (G1 Enforcement Kernel)**  
  `runtime/guardian_validator.py`

### Certification / Measurement (Non-Authoritative)

- **Guardian Evaluator (Audit Harness)**  
  `evaluation/guardian_evaluator.py`

---

### Freeze Rules

- These artifacts **MUST NOT learn, adapt, or self-modify**
- These artifacts **MUST NOT be bypassed by any execution path**
- Any modification requires:
  1. Semantic version bump
  2. Re-running all certification tests
  3. Updating this document with new evidence

**Important:**  
The evaluator produces **measurement evidence only**.  
It has **no execution authority** and is **not a safety gate**.

---

## Explicitly Non-Normative Artifacts (Design-Only)

The repository MAY contain forward-looking or experimental designs.
The following files are **explicitly excluded** from certification authority,
gate advancement, and safety claims:

- `runtime/guardian_validator_v1_1.py`
- `runtime/guardian_hardening_v1_1.py`
- Any file marked **“DESIGN-ONLY / NOT EVALUATED”**

These artifacts:

- ❌ Do NOT participate in any gate
- ❌ Do NOT grant execution authority
- ❌ Do NOT modify frozen G1–G3.5 behavior
- ❌ Do NOT constitute evidence

Their presence **does not advance certification status**.

---

## Current Certification Status

**Highest Passed Gate:** **G3.5 — Unified Software Safety Stack Complete**

### Verified Evidence

- All certification tests passing
- Zero unsafe executions passing all gates under test conditions
- Deterministic behavior across identical inputs
- Complete audit record for every proposal

The system is **software-complete and hardware-ready**, but **not hardware-certified**.

---

## Gate Status Summary

| Gate | Scope | Status | Evidence Type |
|---|---|---|---|
| G0 | Architecture freeze | ✅ PASS | Structural review |
| G1 | Action contract enforcement | ✅ PASS | Validator + schema |
| G2 | Deterministic policy kernel | ✅ PASS | Unit tests |
| G3 | Trajectory & temporal safety | ✅ PASS | Motion tests |
| G3.5 | Unified software authority | ✅ PASS | Integration tests |
| G4 | Hardware governor | ⏳ NEXT | Physical tests |
| G5 | Field-integrated autonomy | ⏳ FUTURE | Real-world trials |

**No claim is valid beyond G3.5.**

---

## Maximum Verified Claim (Strict)

> “Guardian implements a complete, verifiable **software safety stack
> (G1–G3.5)** that deterministically produces a single **FINAL_PASS or VETO**
> decision, with full audit trails and zero unsafe executions passing all gates
> under test conditions. The system is ready for hardware enforcement (G4).”

**No stronger claim is permitted.**

---

## Architecture Overview (Invariant)

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

### Invariant

If **ANY gate vetoes → NO EXECUTION**  
**No exceptions.**

---

## Gate Definitions & Evidence

---

### G0 — Architecture Freeze ✅

**Purpose**  
Enforce strict separation between reasoning, evaluation, and execution authority.

**Verified Properties**

- LLMs never control actuators or external APIs directly
- All execution passes through explicit gates
- No gate may be bypassed
- Interfaces between gates are fixed and auditable

**Claim**  
The architecture is fixed, non-emergent, and authority-separated.

---

### G1 — Action Contract Enforcement ✅

**Purpose**  
Reject malformed, unsafe, or out-of-bounds proposals before semantic policy evaluation.

**Normative Artifacts**

- `schema/guardian01_action_contract_v1.schema.json`
- `runtime/guardian_validator.py`

**Verified Properties**

- Only schema-valid JSON is accepted
- Closed action set enforced
- Hard physical bounds enforced deterministically
- Missing fields, extra fields, or invalid sequencing → **VETO**
- No reliance on LLM self-reported safety

**Evidence**

- Structural validation tests
- Bounds enforcement tests
- Malformed / adversarial output rejection
- Deterministic repeatability

**Claim**  
Only proposals conforming to the frozen contract may proceed under tested conditions.

---

### G2 — Deterministic Policy Kernel ✅

**Purpose**  
Apply semantic safety rules using deterministic logic.

**Normative Artifact**

- `guardian_seed.py`

**Verified Properties**

- Rule-based (no learning, no probability)
- Deterministic outputs for identical inputs
- Policy inputs sourced from frozen, audited data
- Risk above threshold → **VETO**
- Dignity below threshold → **VETO**

**Evidence**

- Unit tests passing
- Zero nondeterminism observed

**Claim**  
Policy decisions are deterministic and auditable.

---

### G3 — Trajectory & Temporal Safety ✅

**Purpose**  
Prevent unsafe motion and unsafe repetition patterns.

**Normative Artifact**

- `trajectory_planner.py`

**Verified Properties**

- Deterministic danger states are never passed
- Temporal repetition detection enforced
- Conservative vetoes preserved
- Zero unsafe executions passing tests

**Evidence**

- 11 / 11 trajectory safety tests passing

**Claim**  
Unsafe motion patterns are deterministically rejected under test conditions.

---

### G3.5 — Safety Coordinator Integration ✅

**Purpose**  
Provide a single authoritative execution decision.

**Normative Artifact**

- `safety_coordinator.py`

**Verified Properties**

- G1 → G2 → G3 enforced in strict order
- Single `check_proposal()` authority
- Complete audit record generated per decision
- Reset and endurance behavior verified

**Evidence**

- 10 / 10 integration tests passing

**Claim**  
The software safety stack operates as a unified, authoritative system.

---

## Certified Policy Substrate (Input Artifact)

**Guardian Seed v1** is a frozen, audited semantic dataset used as an input to G2.

**Properties**

- Semantically normalized records
- Context-aware stop semantics
- Deterministic safety-limit derivation
- Immutable, versioned artifact

**Status**

- ✅ Verified input
- ❌ Not a gate
- ❌ No execution authority
- ❌ No independent safety claim

Guardian Seed strengthens determinism but **does not advance certification**.

---

## Verification Commands

```bash
# Full certification
python -m pytest -v

# Individual gates
python -m pytest test_g3_trajectory_safety.py -v
python -m pytest test_safety_coordinator.py -v

# Demonstration (non-certifying)
python safety_coordinator.py


⸻

Claim Limitations (Non-Negotiable)

Allowed Claims	Forbidden Claims
Software safety stack verified	Physically safe
Zero unsafe executions in tests	Safe in real world
Ready for hardware enforcement	Tamper-proof
Auditable execution control	General intelligence safety
Safety via gate enforcement	Model alignment guarantee


⸻

Core File Map (Certified Set)

guardian_seed/
├── GATES.md
├── schema/guardian01_action_contract_v1.schema.json
├── runtime/guardian_validator.py
├── guardian_seed.py
├── trajectory_planner.py
├── safety_coordinator.py
├── evaluation/guardian_evaluator.py
├── test_g3_trajectory_safety.py
├── test_safety_coordinator.py

Files outside this set do not participate in certification.

⸻

Next Gate — G4: Hardware Governor (Planned)

Objective
Make software vetoes physically unavoidable.

Planned Requirements
	•	Independent MCU
	•	Current / force sensing
	•	Watchdog-enforced cutoff
	•	Ignores override commands
	•	<50 ms hard stop latency

Status
No G4 claims are valid until hardware tests pass.

⸻

Status

🟢 Software safety stack complete (G3.5)
🟡 Hardware enforcement next (G4)

Last Updated: 2026-01-02

⸻

Version History

v1.0.0 — Architectural Freeze
	•	Date: January 04, 2026
	•	Scope: Software safety stack (G2–G3.5) architecture frozen
	•	Includes: Policy kernel, trajectory safety, safety coordinator
	•	Note: Pre-formalization of action contract enforcement

v1.0.1 — First Normative Freeze ✅ CURRENT
	•	Date: January 07, 2026
	•	Scope: Complete software safety stack (G1–G3.5)
	•	Adds:
	•	Action Contract Schema (G1 normative interface)
	•	Guardian Validator (G1 enforcement kernel)
	•	Guardian Evaluator (measurement harness)
	•	No gate advancement
	•	No new safety claims
	•	All freeze declarations accurate

⸻

“He who knows when he can fight and when he cannot, will be victorious.”
— Sun Tzu
