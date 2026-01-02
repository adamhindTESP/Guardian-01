🔒 GATES.md — Guardian Architecture Compliance & Go/No-Go Contract

Purpose:
This document defines the explicit gates, evidence requirements, and claim limitations for systems built using the Guardian Architecture.

It exists to:

· prevent overclaiming
· enforce architectural discipline
· provide clear GO / NO-GO decision points
· make safety properties auditable

If a gate is not passed, claims beyond that gate are forbidden.

---

Current Gate Status

Gate Status Evidence Date
G0 ✅ PASS Architecture frozen 2026-01-02
G1 ✅ PASS 0 unsafe actions in 1000 adversarial cycles 2026-01-02
G2 ✅ PASS 11/11 unit tests, deterministic kernel (0.04/0.30 thresholds) 2026-01-02
G3 🔄 IN PROGRESS Trajectory/pattern safety verification Current
G4 ⏳ PLANNED Teensy physical governor implementation Future
G5 ⏳ FUTURE Integrated autonomy demonstration Future

Latest Milestone: G2 closed - Semantic policy gate verified as deterministic and non-bypassable.

---

Core Law: The Dual-Veto Rule

Any system claiming Guardian compliance must enforce two independent veto authorities:

Tier Authority Role Nature
Tier 1 Semantic Policy Gate Deterministic approval/veto of proposed intent Small, frozen code
Tier 2 Physical / External Governor Enforces real-world limits (physics, power, rate, API bounds) Independent & non-bypassable

No single component may both reason and execute.

---

Threat Model (Explicit)

In scope

· Current-generation LLMs (2024–2026)
· Cooperative or non-malicious models
· Narrow physical or software domains
· Hallucination, mis-specification, accidental misuse

Out of scope

· Adversarial superintelligence
· Long-horizon strategic deception guarantees
· Zero-day parser exploits
· Formal proofs of alignment

These gates certify architectural restraint, not global safety.

---

Gate Definitions

G0 — Architecture Freeze (FOUNDATION)

Goal:
Lock the separation of concerns and veto boundaries.

Requirements

· Semantic Policy Gate exists as a standalone module
· Planner cannot directly control actuators
· Physical / external governor cannot be bypassed in software
· Interfaces between layers are explicit and minimal

Evidence

· Repository structure reflects separation
· Policy gate code is frozen and auditable

NO-GO

· Policy gate issuing commands
· LLM interacting directly with motors, APIs, or hardware
· Safety logic embedded inside the planner

Allowed Claim

"This system implements the Dual-Veto architectural pattern."

---

G1 — Simulation Safety (ROBUSTNESS) ✅ PASS

Goal:
Prove the system fails safely under malformed, deceptive, or missing inputs.

Requirements

· System defaults to conservative fallback on:
  · invalid JSON
  · missing parameters
  · validator failure
  · planner failure
· No unsafe action is executed in simulation

Evidence

· ✅ 1,000 adversarial simulation cycles completed
· ✅ 0 unsafe executions observed
· ✅ Fallback behavior dominates under failure
· ✅ Conservative risk floor calibrated (0.20 base risk)

NO-GO

· Crash loops
· Replaying last valid command after failure
· Executing partially validated actions

Allowed Claim

"The system defaults safely under adversarial or malformed inputs (0 unsafe in 1000 cycles)."

---

G2 — Semantic Policy Gate Integrity ✅ PASS

Goal:
Ensure the semantic veto is deterministic, bounded, and unbypassable.

Requirements

· Policy gate:
  · is deterministic
  · accepts only bounded numeric inputs
  · returns only APPROVE or REJECT
· No learning, memory, or external calls inside gate
· Inputs are sanitized before use

Evidence

· ✅ 11/11 unit tests passing
· ✅ Deterministic behavior verified (100 identical runs)
· ✅ Zero bypass on conservative thresholds (risk > 0.04, dignity ≤ 0.30)
· ✅ All code paths tested:
  · Clamping verification
  · Semantic blacklist
  · Policy score fallback
  · Edge condition correctness

NO-GO

· Policy gate rewriting actions
· Policy gate trusting LLM-reported risk/dignity
· Non-deterministic behavior

Allowed Claim

"This system includes an auditable semantic veto layer (deterministic, zero bypass)."

---

G3 — Independent Validation & Planning 🔄 IN PROGRESS

Goal:
Ensure execution decisions are based on independent computation, not LLM wording.

Requirements

· LLM outputs structured JSON only
· Independent validator:
  · rejects self-reported safety metrics
  · enforces schemas and numeric bounds
  · computes risk from trusted data
· Deterministic planner converts validated intent to constrained execution
· Temporal pattern detection prevents multi-step deception

Evidence

· In development

NO-GO

· Free-text safety decisions
· Risk inferred from adjectives or phrasing
· LLM controlling trajectory generation

Allowed Claim

"Execution constraints are computed independently of LLM reasoning."

---

G4 — Physical / External Governor ⏳ PLANNED

Goal:
Prove an independent authority can halt execution regardless of software state.

Requirements

· Separate hardware or external controller
· Real-time enforcement of:
  · current / force
  · speed / rate
  · emergency stop
· No software override path

Evidence

· Planned

NO-GO

· Governor firmware controlled by LLM
· Safety checks only in user-space software

Allowed Claim

"This system enforces physical execution limits independently."

---

G5 — Integrated Autonomy (REFERENCE ONLY) ⏳ FUTURE

Goal:
Demonstrate sustained operation under real-world conditions.

Requirements

· Successful completion of G0–G4
· Extended supervised operation
· No unsafe events observed

Evidence

· Future demonstration

NO-GO

· Claims of provable safety or benevolence

Allowed Claim

"This system demonstrates constrained autonomy under the Dual-Veto Rule."

---

Implementation Status

✅ Completed Gates

G0 (Architecture Freeze)

· Dual-veto rule locked
· Interfaces defined and frozen
· Reference implementation complete

G1 (Simulation Safety)

· g1_adversarial_simulator.py tests completed
· 1000 adversarial test cycles with 0 unsafe executions
· Conservative fallback behavior verified
· Validator hardened (base risk = 0.20, quadratic penalties)

G2 (Semantic Policy Gate Integrity)

· guardian_seed.py kernel frozen at v0.1
· Ultra-conservative thresholds: 0.04 risk, 0.30 dignity
· 11/11 unit tests in test_benevolence.py passing
· Deterministic behavior verified (100 identical runs)
· All code paths tested including clamping, blacklist, policy score

🔄 Current Focus: G3 (Trajectory/Pattern Safety)

Objectives:

· Independent validation of execution trajectories
· Prevention of multi-step deception
· Physical limit enforcement in planning
· Temporal pattern detection

Key Components:

· validator_module.py (G1-hardened)
· Deterministic safe planner (in development)
· Temporal sequence validation

⏳ Planned Gates

G4 (Physical Governor)

· Teensy microcontroller reference implementation
· Hardware-level speed/force limits
· Independent emergency stop capability
· No-software-override enforcement

G5 (Integrated Autonomy)

· Real-world demonstration
· Sustained operation monitoring
· Environmental adaptation within constraints

---

Claim Limitations (MANDATORY)

Highest Gate Passed Allowed Claim Forbidden Claim
G0 Architectural pattern implemented "Safe system"
G1 ✅ Robust failure handling under adversarial inputs "Prevents all harm"
G2 ✅ Auditable semantic filter with zero bypass "Ethically aligned"
G3 🔄 Independent execution constraints "Deception-proof"
G4 ⏳ Physically enforced limits "Provably safe"
G5 ⏳ Demonstrated constrained autonomy "Guaranteed benevolence"

Current allowed claim (G2 PASS):

"This system includes an auditable semantic veto layer that is deterministic and non-bypassable when fed independent metrics. It has demonstrated robust failure handling in simulation with 0 unsafe actions in 1000 adversarial cycles."

---

Enforcement Philosophy

If a gate fails:

· development stops
· claims are rolled back
· fixes occur before progression

The gates are not aspirational.
They are binding.

---

Next Steps

1. G3 Development: Complete deterministic safe planner with temporal validation
2. G4 Planning: Teensy firmware for physical governor
3. Documentation: Update all components to reflect G1/G2 passes

System currently at: G2 PASS (Semantic policy gate verified)

Maximum service through restraint.

---

Last Updated: 2026-01-02
