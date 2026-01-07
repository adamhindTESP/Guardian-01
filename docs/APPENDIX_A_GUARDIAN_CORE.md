Appendix A — Guardian Core (Normative Specification)

Status: Normative • Frozen for Guardian Seed v1.0
Scope: Software-only safety enforcement (G1–G3.5)
Learning: Explicitly prohibited in all components described here

This appendix defines the minimal, frozen core of the Guardian Architecture.
All safety guarantees claimed in this repository and associated paper are grounded exclusively in the artifacts specified below.

No component in this appendix learns, adapts, or updates at runtime.

⸻

A.1 Action Contract (Formal Interface)

Artifact:
schema/guardian01_action_contract_v1.schema.json

The Action Contract defines the only permissible interface between an untrusted planner and the Guardian safety stack.

Properties
	•	Closed action vocabulary (explicit enumeration)
	•	Hard numeric bounds on all physical parameters
	•	Strict prohibition of free-text execution directives
	•	No additional properties permitted
	•	JSON-only, schema-valid output required

Authority

The Action Contract is authoritative.
Any planner output that does not conform exactly to this schema is rejected prior to policy evaluation.

Safety Role

This contract ensures that:
	•	All planner outputs are machine-verifiable
	•	All unsafe or ambiguous proposals fail closed
	•	Safety reduces to a binary question:
“Does this JSON satisfy the contract?”

The Action Contract is versioned and immutable for Guardian Seed v1.
Any modification requires a schema version bump and full re-evaluation.

⸻

A.2 Guardian Validator (Veto Kernel)

Artifact:
runtime/guardian_validator.py

The Guardian Validator is the deterministic veto authority that enforces the Action Contract and associated safety rules.

Responsibilities

The Validator implements three classes of checks:

G1 — Structural Validation
	•	Valid JSON parsing
	•	Exact schema compliance
	•	Required fields present
	•	No additional fields allowed

G2 — Deterministic Policy Enforcement
	•	Closed action set enforcement
	•	Hard bounds on speed, force, duration
	•	Prohibition of invalid parameter combinations

G2.5 — Sequencing Constraints
	•	Required prior actions (e.g., observe → grasp)
	•	Forbidden transitions (e.g., navigate immediately after grasp)
	•	Order-sensitive safety rules

Non-Properties (Explicit)

The Guardian Validator:
	•	❌ does not learn
	•	❌ does not adapt thresholds
	•	❌ does not infer intent
	•	❌ does not repair planner output
	•	❌ does not negotiate with the planner

Any violation results in an immediate VETO.

Freeze Declaration

The Guardian Validator is frozen for v1.
Behavioral changes require:
	1.	Version bump
	2.	Updated evidence
	3.	Re-certification

⸻

A.3 Guardian Evaluator (Measurement Harness)

Artifact:
evaluation/guardian_evaluator.py

The Guardian Evaluator is an offline audit and measurement tool.
It does not participate in execution.

Purpose

The Evaluator exists to:
	•	Measure planner compliance
	•	Produce reproducible PASS / VETO / ERROR statistics
	•	Generate auditable artifacts for documentation and review

Operation

For each prompt:
	1.	Invoke planner (untrusted)
	2.	Pass output to Guardian Validator
	3.	Record outcome:
	•	PASS (accepted)
	•	VETO (safety rejection)
	•	ERROR (planner failure)

All outcomes are logged with:
	•	Prompt ID
	•	Raw reason string
	•	Gate responsible (if applicable)

Safety Role

The Evaluator:
	•	does not affect runtime behavior
	•	does not grant execution authority
	•	exists solely to support verification and reporting

⸻

A.4 Separation of Roles (Normative)

The Guardian Core enforces strict separation:

Component	Role	Learning
Action Contract	Defines allowed structure	❌
Guardian Validator	Enforces safety	❌
Guardian Evaluator	Measures outcomes	❌
Planner	Proposes actions	✅ (optional)

This separation is intentional and mandatory.

Safety authority is never delegated to learned components.

⸻

A.5 Freeze & Versioning Policy

For Guardian Seed v1:
	•	Action Contract: Frozen
	•	Guardian Validator: Frozen
	•	Guardian Evaluator: Frozen
	•	Safety claims: Bounded to these artifacts

Any future extension requires:
	•	New version identifier
	•	Explicit change log
	•	New evaluation evidence
	•	Updated gate status

Silent drift is prohibited.

⸻

A.6 Scope of Guarantees

The guarantees established by this appendix are limited to:
	•	Deterministic rejection of unsafe or malformed plans
	•	Invariant enforcement of declared safety bounds
	•	Independence from planner capability or alignment

This appendix does not claim:
	•	Long-horizon intent alignment
	•	Adversarial robustness
	•	Physical-world safety beyond verified gates

⸻

A.7 Normative Status

This appendix is normative for Guardian Seed v1.
All claims in the paper and README that reference “Guardian enforcement” or “safety guarantees” rely solely on the mechanisms specified here.

⸻

End of Appendix A
