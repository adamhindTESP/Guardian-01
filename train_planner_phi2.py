#!/usr/bin/env python3
"""
train_planner_phi2.py — Phase 3 Planner Learning (Guardian-safe)

Trains a planner to emit Guardian-compliant JSON.
Guardian authority remains external, frozen, and absolute.

This script:
- Fine-tunes Phi-2 with LoRA
- Learns STRICT_JSON_MODE + action contract
- NEVER modifies Guardian logic
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Any

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType

# =============================================================================
# CONFIG
# =============================================================================

BASE_MODEL = "microsoft/phi-2"
DATASET_PATH = "training_data/golden_plans.jsonl"
OUTPUT_DIR = "./guardian-planner-phi2-lora"

MAX_SEQ_LEN = 512
BATCH_SIZE = 2
GRAD_ACCUM = 2
EPOCHS = 3
LR = 2e-4
SEED = 42

torch.manual_seed(SEED)

# =============================================================================
# LOAD DATA
# =============================================================================

def load_training_data(path: str):
    """
    Expects JSONL with:
    {
      "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "{JSON}"}
      ]
    }
    """
    return load_dataset("json", data_files=path)["train"]

# =============================================================================
# TOKENIZATION
# =============================================================================

def format_example(example: Dict[str, Any], tokenizer):
    user = example["messages"][0]["content"]
    assistant = example["messages"][1]["content"]

    prompt = (
        "You are an autonomous planner.\n"
        "You MUST output ONLY valid JSON matching the Guardian contract.\n\n"
        f"USER:\n{user}\n\nASSISTANT:\n"
    )

    full_text = prompt + assistant

    tokens = tokenizer(
        full_text,
        truncation=True,
        max_length=MAX_SEQ_LEN,
        padding=False,
    )

    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("🧠 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token

    print("🧠 Loading base model...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
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
    dataset = dataset.map(
        lambda ex: format_example(ex, tokenizer),
        remove_columns=dataset.column_names,
    )

    print("⚙️ Training configuration...")
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        num_train_epochs=EPOCHS,
        learning_rate=LR,
        fp16=True,
        logging_steps=5,
        save_strategy="epoch",
        save_total_limit=2,
        report_to="none",
        remove_unused_columns=False,
        seed=SEED,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset,
        tokenizer=tokenizer,
        data_collator=DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        ),
    )

    print("🚀 Starting training...")
    trainer.train()

    print("💾 Saving LoRA adapter...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("\n✅ TRAINING COMPLETE")
    print(f"📁 Adapter saved to: {OUTPUT_DIR}")
    print("🛡️ Guardian authority unchanged.")

# =============================================================================

if __name__ == "__main__":
    main()
