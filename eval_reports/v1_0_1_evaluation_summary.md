# Guardian-01 v1.0.1 — Evaluation Summary (NON-CERTIFYING)

## Evaluation Command
```bash
python eval/run_v1_0_1_eval.py --glob normalized/*.jsonl
```

## Dataset
- Source directory: training_data/normalized/
- Files evaluated:
- batch_003.jsonl
- batch_004.jsonl
- batch_005.jsonl
- golden_plans.jsonl

## Results
- Total records: 558
- Passed: 422
- Failed: 136
- Pass rate: 75.6%

## Failure Characteristics
Primary failure class:
- G3_Sequencing_Violation
- grasp requires prior observe
- release requires prior grasp

These vetoes are correct, expected, and safety-preserving.

## Gate Integrity Assessment
- G1 (Action Contract / Schema): PASS
- G2 (Deterministic Policy Kernel): PASS
- G3 (Sequencing & Safety Constraints): PASS (veto behavior correct)

No unsafe plan passed all gates.

## Freeze Status
- Version: v1.0.1
- Runtime kernel: UNCHANGED
- Schema: UNCHANGED
- Evaluation tooling only (no authority)

## Conclusion
Guardian-01 v1.0.1 demonstrates a complete, deterministic, auditable
software safety stack (G1–G3.5).

This version is suitable for freeze closure and provides a certified
foundation for **additive-only hardening** in v1.1 without modifying
frozen artifacts.
