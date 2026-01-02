# 🔒 GATES.md — Guardian Architecture Compliance & Go/No-Go Contract

**Purpose:**  
This document defines the explicit gates, evidence requirements, and claim limitations for systems built using the Guardian Architecture.

It exists to:
- prevent overclaiming
- enforce architectural discipline
- provide clear GO / NO-GO decision points
- make safety properties auditable

If a gate is not passed, **claims beyond that gate are forbidden**.

---

## Core Law: The Dual-Veto Rule

Any system claiming Guardian compliance **must** enforce **two independent veto authorities**:

| Tier | Authority | Role | Nature |
|-----:|----------|------|--------|
| Tier 1 | Semantic Policy Gate | Deterministic approval/veto of proposed intent | Small, frozen code |
| Tier 2 | Physical / External Governor | Enforces real-world limits (physics, power, rate, API bounds) | Independent & non-bypassable |

**No single component may both reason and execute.**

---

## Threat Model (Explicit)

**In scope**
- Current-generation LLMs (2024–2026)
- Cooperative or non-malicious models
- Narrow physical or software domains
- Hallucination, mis-specification, accidental misuse

**Out of scope**
- Adversarial superintelligence
- Long-horizon strategic deception guarantees
- Zero-day parser exploits
- Formal proofs of alignment

These gates certify **architectural restraint**, not global safety.

---

## Gate Definitions

### G0 — Architecture Freeze (FOUNDATION)

**Goal:**  
Lock the separation of concerns and veto boundaries.

**Requirements**
- Semantic Policy Gate exists as a standalone module
- Planner cannot directly control actuators
- Physical / external governor cannot be bypassed in software
- Interfaces between layers are explicit and minimal

**Evidence**
- Repository structure reflects separation
- Policy gate code is frozen and auditable

**NO-GO**
- Policy gate issuing commands
- LLM interacting directly with motors, APIs, or hardware
- Safety logic embedded inside the planner

**Allowed Claim**
> “This system implements the Dual-Veto architectural pattern.”

---

### G1 — Simulation Safety (ROBUSTNESS)

**Goal:**  
Prove the system fails safely under malformed, deceptive, or missing inputs.

**Requirements**
- System defaults to conservative fallback on:
  - invalid JSON
  - missing parameters
  - validator failure
  - planner failure
- No unsafe action is executed in simulation

**Evidence**
- ≥ 1,000 adversarial simulation cycles
- Logged outcomes showing:
  - zero unsafe executions
  - fallback dominates under failure

**NO-GO**
- Crash loops
- Replaying last valid command after failure
- Executing partially validated actions

**Allowed Claim**
> “The system defaults safely under adversarial or malformed inputs.”

---

### G2 — Semantic Policy Gate Integrity

**Goal:**  
Ensure the semantic veto is deterministic, bounded, and unbypassable.

**Requirements**
- Policy gate:
  - is deterministic
  - accepts only bounded numeric inputs
  - returns only APPROVE or VETO
- No learning, memory, or external calls inside gate
- Inputs are sanitized before use

**Evidence**
- Unit tests with fixed adversarial prompts
- Stable outputs across runs

**NO-GO**
- Policy gate rewriting actions
- Policy gate trusting LLM-reported risk/dignity
- Non-deterministic behavior

**Allowed Claim**
> “This system includes an auditable semantic veto layer.”

---

### G3 — Independent Validation & Planning

**Goal:**  
Ensure execution decisions are based on **independent computation**, not LLM wording.

**Requirements**
- LLM outputs **structured JSON only**
- Independent validator:
  - rejects self-reported safety metrics
  - enforces schemas and numeric bounds
  - computes risk from trusted data
- Deterministic planner converts validated intent to constrained execution

**Evidence**
- Adversarial tests showing:
  - linguistic rephrasing has no effect
  - parameter overruns are rejected
  - unsafe trajectories are blocked

**NO-GO**
- Free-text safety decisions
- Risk inferred from adjectives or phrasing
- LLM controlling trajectory generation

**Allowed Claim**
> “Execution constraints are computed independently of LLM reasoning.”

---

### G4 — Physical / External Governor

**Goal:**  
Prove an independent authority can halt execution regardless of software state.

**Requirements**
- Separate hardware or external controller
- Real-time enforcement of:
  - current / force
  - speed / rate
  - emergency stop
- No software override path

**Evidence**
- Demonstrated hard cut-off under fault
- Governor operates even if host crashes

**NO-GO**
- Governor firmware controlled by LLM
- Safety checks only in user-space software

**Allowed Claim**
> “This system enforces physical execution limits independently.”

---

### G5 — Integrated Autonomy (REFERENCE ONLY)

**Goal:**  
Demonstrate sustained operation under real-world conditions.

**Requirements**
- Successful completion of G0–G4
- Extended supervised operation
- No unsafe events observed

**Evidence**
- Logged real-world runs
- Operator review

**NO-GO**
- Claims of provable safety or benevolence

**Allowed Claim**
> “This system demonstrates constrained autonomy under the Dual-Veto Rule.”

---

## Claim Limitations (MANDATORY)

| Highest Gate Passed | Allowed Claim | Forbidden Claim |
|-------------------:|--------------|-----------------|
| G0 | Architectural pattern implemented | “Safe system” |
| G1 | Robust failure handling | “Prevents all harm” |
| G2 | Auditable semantic filter | “Ethically aligned” |
| G3 | Independent execution constraints | “Deception-proof” |
| G4 | Physically enforced limits | “Provably safe” |
| G5 | Demonstrated constrained autonomy | “Guaranteed benevolence” |

---

## Enforcement Philosophy

If a gate fails:
- development **stops**
- claims are **rolled back**
- fixes occur **before progression**

The gates are not aspirational.  
They are **binding**.

---

**Maximum service through restraint.**  
