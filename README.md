***Guardian Architecture***

A verifiable, gate-based architecture for constraining execution while permitting unconstrained reasoning in LLM-driven systems.

⸻

Overview

Modern AI systems increasingly rely on large language models (LLMs) to reason, plan, and generate actions.
The central safety problem is not reasoning quality, but authority over execution.

How do we allow LLMs to reason freely without allowing them to act unsafely?

The Guardian Architecture answers this by enforcing safety structurally, not behaviorally.

Instead of attempting to align intelligence itself, Guardian:
	•	Treats LLMs as untrusted reasoning engines
	•	Enforces execution through deterministic, auditable veto gates
	•	Guarantees that no action executes unless all safety authorities approve

This repository provides a software-complete safety stack (G1–G3.5) suitable for later integration with physical or external systems.

This repository does not present a complete robot and makes no deployment claims.
It demonstrates a frozen safety substrate and a measurable planner interface intended for downstream integration.

Terminology Note

Throughout this repository, the term “safety” is used in a strictly technical sense.

“Safety” refers only to enforced execution constraints:
• bounded force, speed, energy, and sequencing
• deterministic veto conditions
• auditable authority separation

It does not refer to moral harm, ethical judgment, social outcomes, or downstream consequences.

Guardian enforces what actions are physically and procedurally permitted — not what actions are morally right.

⸻

Core Principle: Structural Separation of Authority

Reasoning is not authority.
Execution is never delegated to the LLM.

Guardian enforces a strict multi-gate rule:

Any veto → no execution
All gates pass → execution permitted

There is no negotiation, repair, or persuasion within the safety path.

⸻

Reference Architecture (G3.5 Certified)

LLM (Untrusted Reasoning)
        ↓  (Structured JSON only)
G1 — Validator
        ↓
G2 — Deterministic Policy Kernel
        ↓
G3 — Deterministic Trajectory / Temporal Safety
        ↓
G3.5 — Safety Coordinator (Single Authority API)
        ↓
     [ FINAL_PASS | VETO ]
        ↓
G4 — Hardware / External Governor (future)

Key Properties
	•	LLMs never control actuators or APIs directly
	•	Free-text never enters the safety-critical path
	•	All risk metrics are independently computed
	•	All decisions produce a complete audit record
	•	Conservative vetoes are explicitly allowed
	•	Failure modes default to NO-GO

⸻

Schema-Locked Execution Interface

All planner outputs must conform to a fixed, versioned action schema.
	•	Only whitelisted actions with bounded parameters are permitted
	•	Invalid structure, missing fields, or sequencing violations are vetoed
	•	Safety reduces to a single question:

“Does this JSON pass the validator?”

⸻

Frozen Action Contract & Enforcement (Normative)

All planner outputs are treated as untrusted proposals until validated.

Guardian enforces safety using three frozen, non-learning artifacts:
	•	Action Contract (Schema)
schema/guardian01_action_contract_v1.schema.json
Defines the complete, closed set of permitted actions and hard physical bounds.
	•	Guardian Validator (Veto Kernel)
runtime/guardian_validator.py
Deterministically enforces structural validity, policy limits, and sequencing rules.
The Guardian does not learn, adapt, or update state.
	•	Guardian Evaluator (Audit Harness)
evaluation/guardian_evaluator.py
Executes planner proposals against the frozen Guardian to produce
PASS / VETO / ERROR outcomes with full auditability.

These artifacts are normative and frozen for Guardian Seed v1.
Any modification requires a version bump and full re-evaluation.

⸻

What This Repository Provides

✅ What It Does
	•	A complete, tested software safety stack (G1–G3.5)
	•	Deterministic semantic policy enforcement
	•	Deterministic trajectory and temporal safety checks
	•	A single authoritative check_proposal() interface
	•	End-to-end auditability for every decision
	•	A GO / NO-GO gate model that strictly limits claims

❌ What It Does Not Claim
	•	No solution to adversarial superintelligence
	•	No long-horizon intent inference
	•	No guarantees beyond verified gates
	•	No replacement for industrial safety certification
	•	No claims of real-world physical safety (yet)

All claims are explicitly bounded by GATES.md.

⸻

## Freeze Status

**v1.0.0**: Architecture and software safety stack (G2-G3.5) frozen  
**v1.0.1**: First normative enforcement freeze (G1-G3.5 complete)

> Action contract schema, validator, and evaluator are explicitly defined and frozen starting with v1.0.1.

⸻

Guardian Seed v1 (Frozen Safety Substrate)

This repository contains a frozen, audited safety substrate located at:

guardian_seed/guardian_semantic_normalized.json

Guardian Seed v1 is:
	•	Semantically normalized
	•	Policy audited
	•	Immutable by design

All training, simulation, or agent work must treat this artifact as read-only.
Any modification requires a new version and re-audit.

Guardian Seed is not a model and not a controller.

It provides:
	•	Explicit semantic interpretation of actions (e.g., contextual stop)
	•	Derived, context-aware physical safety limits
	•	Deterministic policy audit results
	•	A versioned, immutable dataset artifact

This ensures policy authority is grounded in auditable data, not model behavior.

⸻

Certification Status (Current)

Highest Passed Gate: G3.5 — Software Safety Stack Complete

Verified Evidence:
	•	21 / 21 tests passing
	•	0 unsafe escapes
	•	Deterministic behavior
	•	Complete audit trail for every decision

The system is software-complete and hardware-ready.

⸻

Project Status

Guardian Seed v1.0 is frozen.
	•	Guardian policy (G1–G3.5) is immutable
	•	Planner behavior may improve in future phases
	•	Safety claims are bounded to verified gates only

All safety enforcement logic (schema, validator, evaluator) is frozen for v1.0.0.

⸻

Gated Development Model

Guardian advances only through explicit safety gates:

Gate	Scope	Status
G0	Architecture freeze	✅ PASS
G1	Formal interface & validation	✅ PASS
G2	Deterministic policy kernel	✅ PASS
G3	Trajectory & temporal safety	✅ PASS
G3.5	Full software integration	✅ PASS
G4	Hardware governor	⏳ NEXT
G5	Field-integrated autonomy	⏳ FUTURE

No system may claim safety beyond its highest verified gate.

⸻

Repository Structure (Authoritative)

schema/
├── guardian01_action_contract_v1.schema.json   # Frozen action contract (G1)

runtime/
├── guardian_validator.py                       # G1–G2 veto kernel (frozen)

evaluation/
├── guardian_evaluator.py                       # Audit / measurement harness

guardian_seed/
├── guardian_semantic_normalized.json           # Frozen safety substrate

docs/
├── APPENDIX_A_GUARDIAN_CORE.md                  # Normative enforcement docs
├── APPENDIX_B_EXPERIMENTAL_PROTOCOL.md          # Evaluation methodology

GATES.md                                        # Certification authority
THREAT_model.md                                 # Explicit threat boundaries

Files outside this core do not participate in certification.

⸻

Threat Model (Explicit and Conservative)

In Scope
	•	Current-generation LLMs (2024–2026)
	•	Cooperative or non-malicious models
	•	Narrow physical or software domains
	•	Hallucination, mis-specification, repetition, and error

Out of Scope
	•	Adversarial superintelligence
	•	Parser exploits / malware
	•	Nation-state threat models
	•	Formal alignment proofs

This clarity is intentional and non-negotiable.

⸻

Why This Exists

Most AI safety approaches rely on:
	•	Training-time refusals
	•	Output filtering
	•	Post-hoc monitoring

These fail once an LLM is allowed to act.

Guardian instead constrains where authority lives:
	•	LLMs reason
	•	Gates decide
	•	Execution obeys structure, not persuasion

This repository exists to demonstrate that pattern — honestly and reproducibly.

⸻

License

MIT License.

You are free to use, fork, and extend this work —
provided you respect the gates and do not overclaim.

⸻

Current Status
	•	Software safety stack: COMPLETE (G3.5)
	•	Hardware enforcement: NEXT (G4)
	•	Claims limited to verified evidence

⸻

“The Tao never acts,
yet nothing is left undone.”
— Tao Te Ching
