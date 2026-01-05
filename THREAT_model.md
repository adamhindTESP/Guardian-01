Threat Model — Guardian Architecture (G0 Frozen)

This document defines the explicit safety scope, assumptions, and limitations of the Guardian Architecture.

The Guardian is a structural safety enforcement system designed to constrain the outputs of a planner LLM operating in controlled, supervised environments. It addresses accidental failures, malformed outputs, and short-horizon unsafe proposals.

⚠️ This architecture is not a general solution to alignment.
It does not attempt to solve value learning, moral reasoning, or adversarial superintelligence.

⸻

Foundational Assumptions

The following assumptions are required for all claims made in this document:
	1.	Cooperative Planner Model
The planner LLM is not actively optimizing against the Guardian’s constraints.
“Cooperative” does not imply alignment, benevolence, or correctness — only the absence of strategic adversarial behavior.
	2.	Trusted Execution Substrate
The Guardian logic, firmware governor (e.g., Teensy), and sensor interfaces are not compromised at the hardware or OS level.
	3.	Bounded Operational Environment
The system operates in a known, finite environment consistent with tested assumptions (e.g., indoor spaces, known geometry, expected human presence).
	4.	Human Oversight Present
A human operator is available for supervision, emergency stop, and intervention in ambiguous or unsafe situations.

⸻

In-Scope Threats (Actively Mitigated)

The following threat classes are explicitly mitigated by the Guardian and tested through G1–G5 gates.

All mitigations must demonstrate deterministic enforcement within G1 simulation.

Threat Category	Description	Mitigation Mechanism	Gate(s)	Evidence
1. Linguistic / Structural Ambiguity	Planner outputs malformed, ambiguous, or free-text actions	Strict JSON parsing + schema validation	G1 / G2	G1.1–G1.3
2. Parameter Over-Bounds	Numeric parameters exceed physical or safety limits	Deterministic bounds checking	G2 / G4	G1.4–G1.5
3. Self-Reported Safety Claims	Planner asserts safety without justification	Independent Guardian risk & dignity computation	G3	G1.6
4. Accidental Planner Errors	Benign mistakes, omissions, or hallucinations	Fail-closed parsing + conservative fallback	G2	G1.1–G1.3
5. Short-Horizon Multi-Step Traps	Sequences of individually valid steps leading to harm	Limited trajectory lookahead + stop rules	G3	G1.8–G1.9

Note: “100% mitigation” refers to deterministic rejection within the modeled domain, not probabilistic guarantees over unbounded environments.

⸻

🚫 Out-of-Scope Threats (Explicitly Not Mitigated)

The Guardian Architecture does not attempt to mitigate the following:
	1.	Adversarial or Superintelligent Agents
Models that strategically search for novel exploits or bypasses across system layers.
	2.	Zero-Day Software Exploits
Vulnerabilities in the OS, Python runtime, ROS2, drivers, or firmware beneath the Guardian abstraction.
	3.	Long-Horizon Strategic Deception
Multi-week or multi-year planning involving social engineering, supply-chain compromise, or institutional manipulation.
	4.	Mechanical or Environmental Hardware Failure
Wear, breakage, environmental damage, or manufacturing defects (handled via standard industrial safety practices).
	5.	Formal Alignment / Value Learning
Ensuring a capable intelligence permanently shares or internalizes human values.
	6.	Domain Generalization
Operation outside the tested environment, sensor assumptions, or physical constraints.

No claims are made — or implied — regarding these threat classes.

⸻

⚠️ Known Failure Modes (Within Scope)

Even with correct implementation, the following failure modes remain possible:
	1.	Legitimate-Action Harm
A valid, allowed action causes harm due to environmental context (e.g., “move slowly forward” near a cliff).
Mitigation: G3 trajectory safety requires accurate sensors and conservative thresholds.
	2.	Sensor Failure Exploitation
Actions safe under correct sensor data become unsafe when sensors fail or drift.
Mitigation: G4 watchdogs, fault detection, and conservative defaults.
	3.	Timing / Rate Attacks
Rapid sequences of valid actions that cumulatively produce unsafe outcomes.
Mitigation: G3 rate limiting, G4 current and motion monitoring.
	4.	Environment Misinterpretation
Planner executes an action correctly but misunderstands the real-world situation.
Mitigation: Bounded environments, human oversight, and conservative gating.

⸻

Mitigation Effectiveness Summary

Threat Class	Effectiveness (Within Scope)	Evidence
Structural / JSON ambiguity	100% deterministic rejection	G1 simulation logs
Parameter bound violations	100% deterministic rejection	G1 simulation logs
Self-reported safety deception	100% (independent computation)	G1 simulation logs
Short-horizon multi-step traps	Limited (finite lookahead)	G1.8 / G1.9
Accidental planner errors	100% fail-closed	G1 simulation logs


⸻

Scope Control & Governance

All claims made by the Guardian Architecture are bounded by the highest gate passed.

See GATES.md for verification requirements and progression criteria.

⸻

Status: G0 Frozen

This threat model defines the complete safety scope for Guardian Seed v1.
Any expansion of autonomy, environment, adversarial assumptions, or hardware trust requires a new threat model and a reset to G0.


