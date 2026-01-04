Guardian Seed v1

Guardian Seed v1 is a frozen, semantically audited safety substrate for AI agents operating in the physical world.

It is not a model.
It is not a controller.
It is not an alignment claim.

It is a minimal, testable, and auditable foundation for enforcing safety constraints outside of model reasoning.

⸻

Purpose

Modern AI systems are increasingly capable of planning, persuasion, and tool use.
What they lack is structural authority separation — a layer that decides what may execute, independent of how well the model reasons.

Guardian Seed v1 exists to provide that layer.

Core goals
	•	Separate reasoning from authority
	•	Encode safety as structure, not persuasion
	•	Make limits explicit, testable, and reviewable
	•	Enable downstream systems to inherit safety without trusting an LLM

⸻

What This Repository Contains

Guardian Seed v1 includes:
	•	A validated raw action dataset (83 records, 11 chunks)
	•	A semantic normalization pipeline
	•	A context-aware policy audit
	•	A frozen, versioned dataset artifact

Key Files

guardian_seed/
├── normalize_with_semantics.py        # Structural + semantic normalization
├── policy_semantic_audit.py           # Context-aware policy audit
├── guardian_semantic_normalized.json  # Frozen Guardian Seed v1 dataset
└── README.md                          # This document


⸻

Design Principles

1. Authority Is Not Learned

No model is trusted to decide safety-critical actions.

All execution must pass through explicit, external constraints.

⸻

2. Semantics Matter

Actions like stop are contextual, not primitive.

Guardian Seed v1 distinguishes between:
	•	emergency halts
	•	prudent pauses
	•	navigational waypoints
	•	safety-boundary enforcement

This prevents both overreaction and silent failure.

⸻

3. Conservative by Default

If intent is ambiguous, Guardian prefers inaction.

This is a feature, not a limitation.

⸻

4. Bounded Claims

Guardian Seed v1 makes no claims about:
	•	general alignment
	•	AGI safety
	•	optimal behavior

It claims only this:

Given these constraints, unsafe actions are vetoed before execution.

⸻

Dataset Overview
	•	Total records: 83
	•	Chunks: 11 (A1–A11)
	•	Domains covered:
	•	household safety
	•	medical hazards
	•	environmental risk
	•	mobility constraints
	•	public and vehicle contexts

Each record includes:
	•	an action sequence (plan)
	•	semantic annotations
	•	derived safety limits
	•	contextual tags
	•	a full audit trail to the original data

⸻

Semantic Normalization

Raw action data is converted using:

python normalize_with_semantics.py raw_dataset.json

This process:
	•	preserves original intent
	•	annotates stop semantics
	•	derives contextual safety limits
	•	assigns semantic tags
	•	produces deterministic record IDs

Output:

guardian_semantic_normalized.json


⸻

Policy Semantic Audit

Normalized data is audited using:

python policy_semantic_audit.py guardian_semantic_normalized.json

The audit checks:
	•	hard physical limits (speed, force)
	•	semantic consistency
	•	action sequencing safety
	•	emergency protocol coverage
	•	context-aware warnings vs. violations

Training or execution must not proceed if violations exist.

⸻

Freeze Status

Guardian Seed v1 is frozen.
	•	The dataset is immutable
	•	Any changes require a new version
	•	Downstream systems must reference this version explicitly

Tag:

guardian-seed-v1.0


⸻

Intended Use

Guardian Seed v1 is intended to be used as:
	•	a safety substrate for embodied agents
	•	an external veto layer for planners or LLMs
	•	a research artifact for reproducible safety evaluation
	•	a foundation for simulation or hardware gating

It is not intended to:
	•	replace human judgment
	•	grant autonomy
	•	justify deployment without additional safeguards

⸻

Philosophy

The best way to keep a system safe
is to never give it the power to argue about safety.

Guardian Seed v1 follows a falsification-first, humility-driven approach:
	•	define limits
	•	test them
	•	freeze what passes
	•	refuse what does not

⸻

License

MIT License.

Use freely.
Modify responsibly.
Do not remove the audit trail.

⸻

Status

Guardian Seed v1
Semantically normalized • Policy audited • Frozen

This is a beginning, not a conclusion.

To serve others is to serve the whole.
