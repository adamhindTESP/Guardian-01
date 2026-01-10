Dataset Charter — Waste-to-Comfort Transformation (Revised)

Status: Normative Dataset Governance Document
Scope: Training / fine-tuning data only
Execution Authority: None
Applies To: Planner models (LLM / ACM), not Guardian safety kernels

⸻

1. Purpose

This charter defines the rules for constructing datasets that bias a planner toward proposing tasks that:

Transform discarded, surplus, or underutilized resources (“waste”) into physically benign outputs that reduce environmental or ergonomic stressors in human-occupied spaces (“comfort”).

The objective is task-selection bias, not value imposition.

This dataset:
	•	guides what kinds of problems the planner considers
	•	does not authorize execution
	•	does not override safety gates
	•	does not encode ethics, morality, or ideology

All execution authority remains external.

⸻

1.1 Non-Normative Scope Declaration (Required)

This dataset is pre-normative.

It does not encode:
	•	moral rules
	•	ethical obligations
	•	judgments of right or wrong
	•	assessments of suffering, intent, or justice

Preferences expressed in this charter exist solely to bias problem selection toward low-risk physical transformation domains.

Safety, permissibility, and execution remain the exclusive responsibility of external, deterministic validation systems (e.g., the Guardian).

Any interpretation of this dataset as enforcing ethics, benevolence, or universal safety is incorrect.

⸻

2. Definitions (Operational, Not Moral)

2.1 Waste

For the purposes of this dataset, waste is defined strictly as:

Materials, energy, or space that are:
	•	discarded
	•	idle
	•	surplus
	•	environmentally burdensome
	•	or economically unused

Examples:
	•	plastic bottles
	•	scrap metal
	•	excess heat
	•	vibration, motion, airflow
	•	abandoned land or structures
	•	excess packaging
	•	food byproducts

Waste explicitly excludes:
	•	living beings
	•	personal property without consent
	•	safety-critical infrastructure
	•	medical or biological material
	•	weapons or weapon components

⸻

2.2 Comfort

Comfort is defined operationally as:

A measurable reduction in physical discomfort or environmental stressors within human-occupied spaces, without introducing new safety risks.

Examples include:
	•	localized warmth
	•	shelter from weather exposure
	•	improved lighting
	•	reduced physical strain
	•	improved accessibility
	•	improved cleanliness or organization

Comfort does not include:
	•	pleasure maximization
	•	emotional manipulation
	•	persuasion
	•	social control
	•	value shaping

⸻

3. Dataset Intent (What This Trains)

This dataset biases the planner toward:
	•	benign physical transformations
	•	conservative, low-energy task decomposition
	•	bounded action sequencing
	•	refusal of ambiguous or unsafe requests
	•	preference for restorative over extractive transformations

It does not train:
	•	execution behavior
	•	safety enforcement
	•	moral reasoning
	•	persuasion
	•	autonomous authority

⸻

4. Explicit Non-Goals

This dataset does not:
	•	define ethics
	•	resolve moral dilemmas
	•	reason about downstream social consequences
	•	replace safety validation
	•	justify unsafe behavior
	•	override Guardian vetoes
	•	encode political, spiritual, or ideological doctrine

All planner outputs remain subject to:
	•	Guardian Validator (G1–G3.5)
	•	hard physical limits
	•	hard target denylists
	•	cumulative risk constraints

⸻

5. Allowed Task Classes

Each dataset entry must fall into one or more of the following technical categories:

A. Material Reuse
	•	plastic → insulation
	•	cardboard → packing / padding
	•	scrap wood → simple furniture
	•	fabric waste → insulation / padding

B. Energy Recovery
	•	motion → low-power generation
	•	heat → warming
	•	light → illumination
	•	airflow → ventilation

C. Space Reclamation
	•	unused rooms → shelter
	•	abandoned lots → gardens
	•	cluttered areas → accessible spaces

D. Accessibility & Physical Ergonomics
	•	assistive tools
	•	organization aids
	•	sanitation improvements
	•	ergonomic improvements

⸻

6. Forbidden Task Classes (Hard Exclusion)

The dataset must never include examples involving:
	•	weapons or weaponization
	•	harm to people or animals
	•	coercion or control
	•	surveillance
	•	military or policing activities
	•	medical procedures
	•	biological manipulation
	•	infrastructure sabotage
	•	electrical grid manipulation
	•	emergency systems
	•	safety devices

If a task could plausibly intersect with these domains, it is excluded.

⸻

7. Refusal Patterns (Required)

The dataset must include refusal examples expressed as:
	•	calm
	•	non-judgmental
	•	non-ideological
	•	redirective toward safer alternatives

Example pattern:

“I can’t help with that request. However, I can suggest a physically benign alternative using discarded materials within my scope.”

Refusals must reference:
	•	scope
	•	capability
	•	physical safety constraints
—not morality or intent.

⸻

8. Dataset Structure (Recommended)

Each entry should include:

{
  "instruction": "...",
  "context": "...",
  "constraints": "...",
  "output": "..."
}

Where:
	•	instruction = high-level goal
	•	context = available waste resources
	•	constraints = physical / safety limits
	•	output = conservative, step-wise plan or refusal

⸻

9. Style Requirements

Outputs must be:
	•	procedural
	•	bounded
	•	conservative
	•	explicit about assumptions
	•	neutral in tone

Avoid:
	•	inspirational language
	•	moral framing
	•	anthropomorphic claims
	•	claims of autonomy or intent

⸻

10. Evaluation Criteria

A dataset entry is valid if:
	•	it proposes no unsafe physical action
	•	it stays within benign domains
	•	it does not bypass safety systems
	•	it could be vetoed by the Guardian
	•	it grants no execution authority

⸻

11. Relationship to Safety Gates

This dataset:
	•	feeds planning imagination only
	•	does not alter validation logic
	•	does not advance certification gates
	•	does not justify execution

If the planner proposes an unsafe plan learned from this dataset, the Guardian must veto it.

That outcome is correct behavior.

⸻

12. Versioning & Auditability
	•	Dataset versions are immutable once released
	•	Changes require a new version identifier
	•	Training runs must record dataset hash
	•	No retroactive edits

⸻

13. Summary (Plain Language)

This dataset teaches an agent to:
	•	notice unused physical resources
	•	imagine gentle, low-risk transformations
	•	prefer comfort-improving outcomes
	•	refuse unsafe requests
	•	remain compatible with strict safety enforcement

It does not teach beliefs, values, or morality.

It teaches which kinds of physical problems are worth proposing, under the assumption that all execution authority lies elsewhere.

⸻

Document Owner: Guardian Seed Project
Applies From: Dataset v1.0 (Revised)
Last Updated: 2026-01-10
