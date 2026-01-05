# TRAINING.md — Planner Model Training (Guardian-01)

## Purpose

This document describes how the **planner language model** is trained in the
Guardian-01 system.

The planner’s sole responsibility is to **propose structured JSON plans**.
It does **not** make safety decisions, execute actions, or modify Guardian logic.

Training exists to improve:
- JSON format fidelity
- Action schema compliance
- Deterministic plan structure

Training does **not** create, modify, or replace safety guarantees.

---

## Safety & Authority Model (Critical)

**Guardian authority is external, immutable, and absolute.**

- The planner is a text model only.
- All outputs are treated as *untrusted proposals*.
- Every plan is validated and may be vetoed by:
  - Guardian core logic
  - Safety Coordinator
  - Action schema enforcement

> Training the planner **cannot bypass** Guardian controls by design.

No Guardian logic, safety policy, or execution authority is ever learned,
fine-tuned, or modified during training.

---

## What Is Trained vs Frozen

### Trained
- LoRA adapters attached to a base language model
- Planner prompt behavior
- JSON structure consistency

### Frozen
- Base model weights (Phi-2)
- Guardian logic
- Safety Coordinator
- Action schema definitions
- Runtime veto rules

---

## Model & Method

- **Base model:** microsoft/phi-2
- **Fine-tuning method:** LoRA (Low-Rank Adaptation)
- **Training style:** Supervised causal language modeling
- **Objective:** Predict assistant JSON continuation given a user prompt

LoRA is used to:
- Minimize compute and disk requirements
- Prevent catastrophic changes to base behavior
- Enable safe, reversible adaptation

---

## Dataset Format

Training data is stored as JSONL:

```json
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "{...valid JSON...}"}
  ]
}

Constraints:
	•	Exactly one user message
	•	Exactly one assistant message
	•	Assistant content must be valid JSON
	•	No prose, markdown, or backticks in assistant output

Datasets are validated before training.

⸻

Training Configuration (Typical)

Parameter	Value (example)
Max sequence length	256
Batch size	2
Gradient accumulation	2
Epochs	3
Learning rate	2e-4
Precision	FP16 (GPU) / FP32 (CPU)

Padding and truncation are forced to avoid tensor shape errors.

⸻

Hardware Expectations

CPU (No GPU)
	•	Training is possible but very slow
	•	Expect hours per epoch
	•	Useful for:
	•	Validation
	•	Debugging
	•	Small experiments

GPU (Recommended)
	•	8–12 GB VRAM sufficient for LoRA
	•	Orders of magnitude faster
	•	Strongly recommended for real training runs

Training scripts automatically adapt to available hardware.

⸻

Outputs

Training produces:
	•	A LoRA adapter directory
	•	Tokenizer files

These outputs:
	•	Are loaded on top of the frozen base model
	•	Do not contain Guardian logic
	•	Can be safely deleted or retrained

⸻

Evaluation & Success Criteria

Training is considered successful if:
	•	Planner outputs valid JSON
	•	Schema violations decrease
	•	Guardian veto rate decreases
	•	No safety regressions occur

There is no expectation of:
	•	World knowledge improvement
	•	Autonomous safety reasoning
	•	Policy learning

⸻

Known Limitations
	•	Small datasets bias behavior toward format, not generality
	•	Planner quality is bounded by schema expressiveness
	•	Safety depends entirely on Guardian, not the model

These limitations are intentional design choices.

⸻

Reproducibility Notes

To reproduce training:
	1.	Use the same dataset
	2.	Use the same training script
	3.	Use LoRA, not full fine-tuning
	4.	Do not modify Guardian logic

Training differences affect proposal quality only.

⸻

Summary

The planner is a constrained proposal generator.

Training improves structure and reliability,
while all authority remains outside the model.

This separation is the core safety property of Guardian-01.

