#!/usr/bin/env python3
"""
train_planner_phi2.py — Phase 3 Planner Learning (Guardian-safe)

Goal
----
Fine-tune a planner (Phi-2 + LoRA) to emit STRICT JSON plans that match the
Guardian action contract.

Safety / Authority
------------------
- Guardian authority remains EXTERNAL and FROZEN.
- This script ONLY trains a text model to propose plans.
- Runtime Guardian / Safety Coordinator still validates + vetoes.

Dataset
-------
JSONL, one example per line:
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "{...json...}"}
  ]
}

Critical Fix
------------
We FORCE padding + truncation so batches have uniform tensor sizes.
"""

from __future__ import annotations

import os
import random
from typing import Any, Dict

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    set_seed,
)
from peft import LoraConfig, get_peft_model, TaskType


# =============================================================================
# CONFIG
# =============================================================================

BASE_MODEL = "microsoft/phi-2"
DATASET_PATH = "training_data/golden_plans.jsonl"
OUTPUT_DIR = "./guardian-planner-phi2-lora"

MAX_SEQ_LEN = 256          # Keep small to save RAM / disk
BATCH_SIZE = 2
GRAD_ACCUM = 2
EPOCHS = 3
LR = 2e-4
SEED = 42


# =============================================================================
# PROMPT TEMPLATE
# =============================================================================

SYSTEM_PROMPT = (
    "You are an autonomous planner.\n"
    "You MUST output ONLY valid JSON matching the Guardian action contract.\n"
    "STRICT_JSON_MODE: No prose. No markdown. No backticks. JSON only.\n"
)


def build_training_text(user_text: str, assistant_json: str) -> str:
    """
    Causal LM format: model learns to continue with assistant JSON.
    """
    return (
        f"{SYSTEM_PROMPT}\n"
        f"USER:\n{user_text}\n\n"
        f"ASSISTANT:\n{assistant_json}"
    )


# =============================================================================
# DATA
# =============================================================================

def load_training_data(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")
    return load_dataset("json", data_files=path, split="train")


# =============================================================================
# TOKENIZATION
# =============================================================================

def format_and_tokenize(example: Dict[str, Any], tokenizer: AutoTokenizer) -> Dict[str, Any]:
    msgs = example.get("messages")
    if not isinstance(msgs, list) or len(msgs) < 2:
        raise ValueError("Each example must contain messages=[user, assistant].")

    user = msgs[0].get("content", "")
    assistant = msgs[1].get("content", "")

    full_text = build_training_text(user, assistant)

    tok = tokenizer(
        full_text,
        padding="max_length",     # CRITICAL
        truncation=True,          # CRITICAL
        max_length=MAX_SEQ_LEN,
        return_attention_mask=True,
    )

    # Causal LM labels = input_ids
    tok["labels"] = tok["input_ids"].copy()
    return tok


# =============================================================================
# MAIN
# =============================================================================

def main():
    # Determinism (best effort)
    set_seed(SEED)
    random.seed(SEED)
    torch.manual_seed(SEED)

    print("🧠 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)

    # Phi-2 has no PAD token by default
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("🧠 Loading base model...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
        trust_remote_code=True,
    )

    print("🔧 Attaching LoRA adapter...")
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "dense"],
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    print("📚 Loading dataset...")
    dataset = load_training_data(DATASET_PATH)

    print("🔤 Tokenizing dataset (padding + truncation enabled)...")
    dataset = dataset.map(
        lambda ex: format_and_tokenize(ex, tokenizer),
        remove_columns=dataset.column_names,
    )

    print("⚙️ Training configuration...")
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        num_train_epochs=EPOCHS,
        learning_rate=LR,
        fp16=torch.cuda.is_available(),
        logging_steps=5,
        save_strategy="epoch",
        save_total_limit=2,
        report_to="none",
        remove_unused_columns=False,
        seed=SEED,
    )

    collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset,
        tokenizer=tokenizer,
        data_collator=collator,
    )

    print("🚀 Starting training...")
    trainer.train()

    print("💾 Saving LoRA adapter + tokenizer...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("\n✅ TRAINING COMPLETE")
    print(f"📁 Adapter saved to: {OUTPUT_DIR}")
    print("🛡️ Guardian authority unchanged.")


if __name__ == "__main__":
    main()
