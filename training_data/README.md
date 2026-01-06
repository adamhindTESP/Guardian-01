# Guardian-01 — Training Data (v1.0)

**Status:** FROZEN  
**Scope:** Planner primitive obedience only  
**Safety Level:** Tier-1 (deterministic, auditable)

---

## 📌 Purpose

This directory contains the **frozen training dataset** used to train the
**Guardian-01 Planner (v1.0)**.

The goal of this dataset is **not intelligence, reasoning, or generalization**.

It exists solely to train **deterministic, schema-correct, safety-bounded
action reflexes** for a constrained action planner operating under the
Guardian safety kernel.

---

## 🎯 What This Dataset Trains

The model is trained to reliably map **single user intents** to
**Guardian-approved action primitives**, such as:

- `navigate` (bounded speed)
- `observe`
- `wait`
- `grasp` (bounded force)
- `release`
- `speak`
- `stop` (safe no-op / refusal)

Every record enforces:

- **Strict JSON-only output**
- **guardian01_action_set_v1 schema**
- **Hard safety limits** (speed, force, no free-text)

This dataset teaches the Planner to be a **safe, obedient subordinate** —
not an autonomous decision-maker.

---

## 📂 Dataset Contents (Frozen)

| File | Records | Notes |
|-----|--------:|------|
| `batch_003.jsonl` | 5 | Early sanity checks |
| `batch_004.jsonl` | 50 | Initial functional coverage |
| `batch_005.jsonl` | 500 | Primary v1.0 training corpus |

**Total records:** 555  
**Duplicates:** None within frozen set  
**Validation status:** PASS (0 errors)

> Earlier experimental batches were removed prior to freeze.

---

## 🔒 Determinism & Auditability

- Dataset generation is **fully deterministic**
- No randomness, shuffling, or stochastic variation
- Re-running the generator without code changes produces identical output
- This is **intentional** for v1.0 audit clarity

This ensures:

- Byte-level reproducibility
- Clear failure attribution
- Simple rollback and comparison
- No hidden data drift

---

## ✅ Validation

All frozen files passed the validation tool:

validate_batch.py

Validation checks include:

- One JSON object per line
- No empty lines
- Valid JSON syntax
- Required fields present
- No free-text leakage
- Schema compliance

Dataset state at freeze:

DATASET VALID — SAFE TO FREEZE

---

## 🔐 Integrity Verification

SHA-256 hashes for each frozen file are recorded in:

training_data/HASHES.txt

These hashes **must match exactly** for any downstream training,
distribution, or archival use.

---

## 🚫 Explicit Non-Goals

This dataset does **NOT** train:

- Multi-step planning
- Memory or past context
- World modeling
- Intent inference
- Moral reasoning
- Task decomposition
- Autonomy beyond primitive execution

All higher-order behavior is deferred to **later versions**.

---

## 🧭 Versioning Policy

- **v1.0** — Deterministic primitive obedience (this dataset)
- **v1.1+** — Controlled variation (curriculum, phrasing, mild entropy)
- **v2.0+** — Multi-step planning and contextual reasoning (future)

No changes may be made to this dataset without a **major version bump**.

---

## 📜 License & Use

This dataset is provided under the same license as the parent repository.

It may be used for:

- Training Guardian-01 v1.0 planners
- Reproducibility studies
- Safety research
- Educational inspection

It must **not** be modified in place.

---

## 🧱 Design Philosophy

> *“Foundation before intelligence.  
> Safety before capability.”*

This dataset intentionally prioritizes **obedience, correctness, and limits**
over creativity or generalization.

It is a **foundation layer**, not a final system.

---

**End of document.**

