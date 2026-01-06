# Guardian-01 Training Dataset — v1.0 (FROZEN)

Status: **FROZEN**
Date: 2026-01-06

This directory contains the **frozen Guardian-01 v1.0 training dataset**.
These files are immutable and MUST NOT be modified, regenerated, reordered,
or augmented.

## Included Batches

| File | Records | Validator Status |
|-----|--------|------------------|
| batch_003.jsonl | 5 | OK |
| batch_004.jsonl | 50 | OK |
| batch_005.jsonl | 500 | OK |
| batch_006.jsonl | 500 | OK |

**Total Records:** 1,055  
**Validator:** `validate_batch.py`  
**Result:** DATASET VALID — SAFE TO FREEZE

## Dataset Properties

- Deterministic generation
- Strict JSON-only outputs
- Guardian action schema v1 enforced
- Speed ≤ 0.5 m/s
- Force ≤ 2.0 N
- No free-text leakage
- No multi-step reasoning
- No memory or chaining

This dataset trains **Guardian Planner v1**:
> A safe, obedient, schema-locked action generator.

## Modification Policy

❌ Do NOT edit these files  
❌ Do NOT re-run generation scripts for v1  
❌ Do NOT mix with future datasets  

All future work MUST occur in **v1.1+ datasets**.

## Integrity

SHA256 checksums are recorded in `HASHES.txt`.

— Guardian-01 Maintainer
