***Guardian Architecture***

A verifiable, gate-based architecture for constraining execution while permitting unconstrained reasoning in LLM-driven systems.

⸻

Overview

Modern AI systems increasingly rely on large language models (LLMs) to reason, plan, and generate actions.
The central safety problem is not reasoning quality, but authority over execution.

How do we allow LLMs to reason freely without allowing them to act unsafely?

The Guardian Architecture answers this by enforcing safety structurally, not behaviorally.

Instead of attempting to “align” intelligence itself, Guardian:
	•	treats LLMs as untrusted reasoning engines
	•	enforces execution through deterministic, auditable veto gates
	•	guarantees that no action executes unless all safety authorities approve

This repository provides a fully tested, software-complete safety stack (G1–G3.5) suitable for integration with physical or external systems.

⸻

Core Principle: Structural Separation of Authority

Reasoning is not authority.
Execution is never delegated to the LLM.

Guardian enforces a dual-veto (multi-gate) rule:

Any veto → no execution.
All gates pass → execution permitted.

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

Schema-Locked Execution Interface
	•	All LLM outputs must conform to a fixed, versioned action schema
	•	Only whitelisted actions with bounded parameters are permitted
	•	Invalid structure, missing fields, or sequencing violations are vetoed before policy evaluation
	•	Safety reduces to: “Does this JSON pass the validator?”
⸻

What This Repository Provides

✅ What It Does
	•	A complete, tested software safety stack (G1–G3.5)
	•	Deterministic semantic policy enforcement
	•	Deterministic trajectory & temporal safety checks
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

## Guardian Seed v1 (Frozen Safety Substrate)

This repository contains a frozen, audited safety substrate located in:

guardian_seed/guardian_semantic_normalized.json

Guardian Seed v1 is:
- semantically normalized
- policy audited
- immutable by design

All training, simulation, or agent work must treat this artifact as read-only.
Any modification requires a new version and re-audit.

Guardian Seed (Safety Substrate)

Guardian Seed v1 is the frozen, semantically audited safety substrate used by the Guardian Architecture to ground deterministic policy enforcement.

It is not a model and not a controller.

Guardian Seed provides:
	•	Explicit semantic interpretation of actions (e.g. contextual stop)
	•	Derived, context-aware physical safety limits
	•	Deterministic policy audit results
	•	A versioned, immutable dataset artifact

Guardian Seed is produced through:
	•	structural normalization
	•	semantic annotation
	•	context-aware policy audit
	•	explicit freeze and versioning

This ensures that policy authority is grounded in auditable data, not model behavior.

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

Gated Development Model

Guardian advances only through explicit safety gates:

Gate	Scope	Status
G0	Architecture freeze	✅ PASS
G1	Simulation safety	✅ PASS
G2	Policy kernel	✅ PASS
G3	Trajectory & temporal safety	✅ PASS
G3.5	Full software integration	✅ PASS
G4	Hardware governor	⏳ NEXT
G5	Field-integrated autonomy	⏳ FUTURE

No system may claim safety beyond its highest verified gate.

Full criteria and evidence live in GATES.md￼.

⸻

Repository Structure (Authoritative)

guardian_seed/
├── README.md                     # This document
├── GATES.md                      # Certification authority
├── THREAT_model.md               # Explicit threat boundaries
├── validator_module.py           # G1 — structured intent validation
├── guardian_seed.py              # G2 — deterministic policy kernel
├── trajectory_planner.py         # G3 — trajectory & temporal safety
├── safety_coordinator.py         # G3.5 — unified decision authority
├── test_g3_trajectory_safety.py  # G3 certification tests (11)
├── test_safety_coordinator.py    # G3.5 certification tests (10)
└── tests_optional/               # Exploratory / non-certifying tests

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
	•	training-time refusals
	•	output filtering
	•	post-hoc monitoring

These fail once an LLM is allowed to act.

Guardian instead constrains where authority lives:
	•	LLMs reason
	•	gates decide
	•	execution obeys structure, not persuasion

This repository exists to demonstrate that pattern, honestly and reproducibly.

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

Maximum capability through minimum authority.

“The Tao never acts,
yet nothing is left undone.”
— Tao Te Ching
