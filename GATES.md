# GATES.md — Guardian Pattern Compliance Contract

**Purpose**  
This document defines the explicit criteria for declaring a system "Guardian-Compliant." It protects the integrity of the Guardian Pattern by limiting claims to what has been validated. No system may claim higher compliance than the last successfully passed gate.

**Applicability**  
Applies to:
- `guardian-seed` library (semantic veto)
- Guardian-01 robot reference (full dual-veto)
- Any derivative or implementation

## 🛡️ Core Architectural Law: The Dual-Veto Rule

All compliant systems **must** separate intelligence from execution with **two independent veto authorities**:

| Layer          | Authority                  | Role                          | Minimum Requirement                  |
|----------------|----------------------------|-------------------------------|--------------------------------------|
| Tier 1         | Policy Gate (`benevolence()`) | Semantic veto (truth, harm, service) | Deterministic, pre-execution check   |
| Tier 2         | External Governor          | Physical/API veto (limits, sensors)  | Independent of intelligence layer    |

**Non-negotiable**: Intelligence proposes only. Execution requires approval from **both** vetoes.

## 🔍 Gate Specifications

Gates are sequential. Pass means documented evidence (tests, logs, hardware).

| Gate | Focus                              | Pass Criteria                                                                 | NO-GO Condition                                      |
|------|------------------------------------|-------------------------------------------------------------------------------|------------------------------------------------------|
| G0   | Architecture Defined               | Code/structure reflects Dual-Veto Rule. `benevolence()` separate from planner/executor. | Single process controls proposal + execution         |
| G1   | Simulation Robustness              | ≥1,000 adversarial cycles: No unsafe actions. Failures → conservative fallback (observe/stop). | Crash, repeat last command, or escalate on failure    |
| G2   | Policy Gate Integrity              | `benevolence()` deterministic (unit tests pass fixed adversarial set). Inputs clamped. | Trusts raw LLM risk estimates or non-deterministic   |
| G3   | Reasoning Validity                 | Planner treats LLM output as proposal only. Risk recalculated independently. Veto learning loop present. | LLM output directly executes or bypasses veto        |
| G4   | External Governor                  | Independent veto (Teensy, API limiter, sandbox). Physics/API constraints enforced outside Python. | Governor in same process or bypassable by software    |
| G5   | Full Dual-Veto Autonomy            | All prior gates + real-world cycles: No veto bypass. Documented failure modes handled. | Single point of failure in veto chain                |

## 📜 Compliance Levels & Allowed Claims

| Gates Passed | Compliance Level              | Allowed Claim                                                                 | Forbidden Claim                              |
|--------------|-------------------------------|-------------------------------------------------------------------------------|----------------------------------------------|
| G0           | Pattern Defined               | "Implements Guardian Pattern architecture."                                   | Any safety or benevolence guarantee          |
| G0-G1        | Simulation Validated          | "Robust in simulation under adversarial conditions."                          | "Safe in real world"                         |
| G0-G2        | Semantic Veto Compliant       | "G2-Compliant: Deterministic semantic policy veto." (`guardian-seed` library) | "Safe autonomous system"                     |
| G0-G3        | Reasoning Constrained         | "Constrained deep reasoning with ethical veto."                               | "Guaranteed safe execution"                  |
| G0-G4        | Dual-Veto Present             | "Dual-veto constraint architecture with external governor."                   | "Provably safe" or "benevolent AGI"          |
| G0-G5        | Full Pattern Compliant        | "Guardian Pattern fully implemented with validated dual-veto." (Guardian-01)  | Absolute safety claims                       |

## ⚠️ Important Notes

- This is a **pattern**, not a product or guarantee.
- Compliance is self-certified—provide evidence (tests, logs) for claims.
- The pattern enables constrained autonomy—it does not eliminate all risks.
- Use responsibly. Focus on service, not superiority.

**MIT License** – Adapt freely, but respect the gates.
