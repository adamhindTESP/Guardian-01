This is the revised GATES.md. It incorporates the critical security fix by introducing the Independent Assessor and explicitly forbids the LLM from reporting its own safety metrics. This hardens the compliance contract against the threat of deception.
GATES.md — Guardian Pattern Compliance Contract
Purpose This document defines the explicit criteria for declaring a system "Guardian-Compliant." It protects the integrity of the Guardian Pattern by limiting claims to what has been validated. No system may claim higher compliance than the last successfully passed gate.
Applicability Applies to:
 * guardian-seed library (semantic veto)
 * Guardian-01 robot reference (full dual-veto)
 * Any derivative or implementation
🛡️ Core Architectural Law: The Dual-Veto Rule (Hardened)
All compliant systems must separate intelligence from execution with two independent veto authorities and one independent input layer.
| Layer | Authority | Role | Minimum Requirement |
|---|---|---|---|
| Input Validation (G3) | Independent Assessor | Calculates trusted metrics (Risk, Dignity) from sensor/context data. | Must operate outside the LLM/Planner's control. |
| Tier 1 Veto (G2) | Policy Gate (benevolence()) | Semantic veto (truth, harm, service) using trusted inputs only. | Deterministic, pre-execution check. |
| Tier 2 Veto (G4) | External Governor | Physical/API veto (limits, sensors, power cut). | Independent of all software layers. |
Non-negotiable: The LLM/Planner proposes action only. Execution requires approval from both vetoes, operating on independently verified metrics.
🔍 Gate Specifications
Gates are sequential. Pass means documented evidence (tests, logs, hardware).
| Gate | Focus | Pass Criteria | NO-GO Condition |
|---|---|---|---|
| G0 | Architecture Defined | Code/structure reflects Dual-Veto Rule. benevolence() separate from planner/executor. | Single process controls proposal + execution. |
| G1 | Simulation Robustness | \ge 1,000 adversarial cycles (including random inputs): No unsafe actions. Failures \rightarrow conservative fallback (observe/stop). | Crash, repeat last command, or escalate on failure. |
| G2 | Policy Gate Integrity | benevolence() is deterministic (unit tests pass fixed adversarial set). Inputs are clamped and normalized. | Policy Gate logic is non-deterministic (e.g., uses external LLM/API calls). |
| G3 | Input Validation & Trust Mitigation | Independent Assessor is active. The Policy Gate receives zero LLM-reported risk/dignity metrics. Deceptive LLM inputs are caught and rejected. | The Policy Gate accepts or trusts any semantic input (risk, dignity, safety score) directly supplied by the LLM/Planner. |
| G4 | External Governor | Independent veto (Teensy, API limiter, sandbox) is functional. Physical/API constraints enforced outside the main compute stack. | Governor in same process or bypassable by software. |
| G5 | Full Dual-Veto Autonomy | All prior gates + real-world cycles: No veto bypass. Documented failure modes handled. System performs a service mission safely. | Single point of failure in veto chain. |
📜 Compliance Levels & Allowed Claims
| Gates Passed | Compliance Level | Allowed Claim | Forbidden Claim |
|---|---|---|---|
| G0 | Pattern Defined | "Implements Guardian Pattern architecture." | Any safety or benevolence guarantee. |
| G0-G1 | Simulation Validated | "Robust in simulation under adversarial conditions (non-deceptive)." | "Safe in real world." |
| G0-G2 | Semantic Veto Compliant | "G2-Compliant: Deterministic semantic policy veto." (guardian-seed library) | "Safe autonomous system." |
| G0-G3 | Trust Mitigation Compliant | "Constrained reasoning with independent input validation." | "Guaranteed safe execution." |
| G0-G4 | Dual-Veto Present | "Dual-veto constraint architecture with external governor." | "Provably safe" or "benevolent AGI." |
| G0-G5 | Full Pattern Compliant | "Guardian Pattern fully implemented with validated dual-veto." (Guardian-01) | Absolute safety claims. |
⚠️ Important Notes
 * This is a structural pattern, not a product or guarantee.
 * Compliance is self-certified—provide evidence (tests, logs) for claims.
 * The pattern helps mitigate risks in cooperative LLM systems; it is not designed to contain hypothetical, adversarial superintelligence.
 * Use responsibly. Focus on service, not superiority.
MIT License – Adapt freely, but respect the gates.
Built with restraint, for service to life.
