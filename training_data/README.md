Guardian-01 — Training Data (v1.0)

Status: FROZEN (training batches only)
Scope: Planner primitive obedience
Safety Level: Tier-1 (deterministic, auditable)

⸻

Purpose

This directory contains the frozen training dataset used to train the
Guardian-01 Planner (v1.0).

The goal of this dataset is not intelligence, reasoning, or generalization.

It exists solely to train deterministic, schema-correct, safety-bounded
action reflexes for a constrained action planner operating under the
Guardian safety kernel.

The Planner is designed to be a strict subordinate to the Guardian
execution gates — never an autonomous decision-maker.

⸻

What This Dataset Trains

The model is trained to reliably map single user intents to
Guardian-approved action primitives, including:
	•	navigate (bounded speed)
	•	observe
	•	wait
	•	grasp (bounded force)
	•	release
	•	speak
	•	stop (safe no-op / refusal)

Every training record enforces:
	•	Strict JSON-only output
	•	guardian01_action_set_v1 schema
	•	Hard safety limits (speed, force, duration)
	•	No free-text reasoning or narration

This dataset trains obedience and correctness, not autonomy.

⸻

Dataset Contents (Frozen Training Batches)

File	Records	Notes
batch_003.jsonl	3	Early sanity checks
batch_004.jsonl	50	Initial functional coverage
batch_005.jsonl	500	Primary v1.0 training corpus

Frozen training records: 553
Duplicates: None within frozen set
Validation status: PASS (0 errors)

Earlier experimental batches were removed prior to freeze.

⸻

Legacy Intent Plans (Not Training Data)

golden_plans.jsonl

This file contains legacy intent-level plans produced prior to the
Action Contract v1 freeze.

These records are not used for training and are not required to pass
Guardian validation.

Record count: 5
Role: Evaluation and regression reference only

Purpose:
	•	Intent coverage reference
	•	Regression detection
	•	Safety gate stress testing
	•	Architectural validation (normalization → gate rejection)

🚫 Do NOT edit, normalize, or retrain on this file.

⸻

Determinism & Auditability
	•	Dataset generation is fully deterministic
	•	No randomness, shuffling, or stochastic variation
	•	Re-running generation without code changes produces identical output

This is intentional for v1.0 and ensures:
	•	Byte-level reproducibility
	•	Clear failure attribution
	•	Simple rollback and comparison
	•	Zero hidden data drift

⸻

✅ Validation

All frozen training batches passed the validation tool:

validate_batch.py

Validation checks include:
	•	One JSON object per line
	•	No empty lines
	•	Valid JSON syntax
	•	Required fields present
	•	No free-text leakage
	•	Action Contract v1 schema compliance

golden_plans.jsonl is intentionally excluded from contract validation.

Dataset state at freeze:

DATASET VALID — SAFE TO FREEZE

⸻

Integrity Verification

SHA-256 hashes for each frozen training file are recorded in:

training_data/HASHES.txt

These hashes must match exactly for any downstream training,
distribution, or archival use.

⸻

🚫 Explicit Non-Goals

This dataset does NOT train:
	•	Multi-step planning
	•	Memory or historical context
	•	World modeling
	•	Intent inference
	•	Moral reasoning
	•	Task decomposition
	•	Autonomy beyond primitive execution

All higher-order behavior is deferred to later versions.

⸻

Versioning Policy
	•	v1.0 — Deterministic primitive obedience (this dataset)
	•	v1.1+ — Additive hardening (temporal, cumulative, rate-based gates)
	•	v2.0+ — Multi-step planning and contextual reasoning (future)

No changes may be made to frozen training batches without a
major version bump.

⸻

Training Architecture Summary

User Intent
    ↓
Planner (trained on this dataset)
    ↓
Normalized Action Contract
    ↓
Frozen Guardian Gates (v1.0)
    ↓
EXECUTE or VETO

The Planner proposes.
The Guardian decides.
Safety always wins.

⸻

🧱 Design Philosophy

“Foundation before intelligence.
Safety before capability.”

This dataset prioritizes obedience, correctness, and limits
over creativity or generalization.

It is a foundation layer, not a final system.

⸻

End of document.

