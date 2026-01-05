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
- This script only trains a text model to *propose* plans.
- Your runtime Guardian / Safety Coordinator still validates + vetoes.

Dataset
-------
Expects JSONL where each line is:
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "{...json...}"}
  ]
}

Key Fix
-------
We FORCE padding + truncation to avoid tensor shape errors when batching.
"""

from __future__ import annotations

import os
import random
from typing import Any, Dict, List

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

# Keep this modest. Bigger => more disk + more RAM/VRAM.
MAX_SEQ_LEN = 256

BATCH_SIZE = 2
GRAD_ACCUM = 2
EPOCHS = 3
LR = 2e-4
SEED = 42

# If you want to reduce disk usage, set HF cache to a big drive in your CMD:
#   set HF_HOME=G:\hf_cache
#   set TRANSFORMERS_CACHE=G:\hf_cache
#   set HF_DATASETS_CACHE=G:\hf_cache


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
    Builds the supervised training string. We train causal-LM style:
    model learns to continue the prompt with the assistant JSON.

    NOTE: If you later want to train only on the assistant portion, we can
    mask labels for prompt tokens. Keeping it simple for now.
    """
    prompt = (
        f"{SYSTEM_PROMPT}\n"
        f"USER:\n{user_text}\n\n"
        f"ASSISTANT:\n"
    )
    return prompt + assistant_json


# =============================================================================
# DATA
# =============================================================================

def load_training_data(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    ds = load_dataset("json", data_files=path, split="train")
    return ds


# =============================================================================
# TOKENIZATION
# =============================================================================

def format_and_tokenize(example: Dict[str, Any], tokenizer: AutoTokenizer) -> Dict[str, Any]:
    msgs = example.get("messages", None)
    if not isinstance(msgs, list) or len(msgs) < 2:
        raise ValueError("Each example must contain messages=[user, assistant].")

    user = msgs[0].get("content", "")
    assistant = msgs[1].get("content", "")

    full_text = build_training_text(user, assistant)

    tok = tokenizer(
        full_text,
        padding="max_length",     # <<< critical fix
        truncation=True,          # <<< critical fix
        max_length=MAX_SEQ_LEN,
        return_attention_mask=True,
    )

    # causal LM labels = input_ids (standard)
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

    # Phi-2 often has no pad token by default. Use EOS as PAD.
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
        # Phi-2 module names can vary by implementation.
        # These targets tend to work; if you get a warning about missing modules,
        # we can adjust to the exact names in your model.
        target_modules=["q_proj", "k_proj", "v_proj", "dense"],
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    print("📚 Loading dataset...")
    dataset = load_training_data(DATASET_PATH)

    # Optional: split train/eval (helps catch overfit / broken training)
    # For tiny datasets, eval is mostly for sanity.
    split = dataset.train_test_split(test_size=0.2, seed=SEED)
    train_ds = split["train"]
    eval_ds = split["test"]

    print("🔤 Tokenizing dataset (padding + truncation enabled)...")
    train_ds = train_ds.map(
        lambda ex: format_and_tokenize(ex, tokenizer),
        remove_columns=train_ds.column_names,
    )
    eval_ds = eval_ds.map(
        lambda ex: format_and_tokenize(ex, tokenizer),
        remove_columns=eval_ds.column_names,
    )

    print("⚙️ Training configuration...")
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        num_train_epochs=EPOCHS,
        learning_rate=LR,
        fp16=torch.cuda.is_available(),
        logging_steps=5,
        evaluation_strategy="steps",
        eval_steps=20,
        save_strategy="epoch",
        save_total_limit=2,
        report_to="none",
        remove_unused_columns=False,
        seed=SEED,
    )

    # Because we already padded to max_length in tokenization,
    # the collator is straightforward.
    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
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
