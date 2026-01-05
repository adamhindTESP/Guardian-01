# ARCHITECTURE

## 1. System Overview

This repository implements a **dual-layer decision architecture** separating plan generation from safety authority.  
A learned planner model proposes structured action plans, while an external, deterministic Guardian system evaluates and enforces safety constraints.  
The planner is trained only to emit **well-formed, contract-compliant JSON**, not to make safety decisions.  
All execution authority remains outside the model and is never delegated to learned components.  
This separation ensures that learning improves usability and flexibility without compromising safety guarantees.  
The architecture is designed so that failures in the planner cannot bypass Guardian enforcement.

---

## 2. Component Roles

- **Planner (Learned Model)**
  - Generates candidate plans as structured JSON
  - Trained via supervised fine-tuning (LoRA)
  - Has no execution capability or authority

- **Guardian / Safety Coordinator (Deterministic)**
  - Validates all proposed plans
  - Enforces hard safety rules and vetoes invalid actions
  - Remains frozen and external to training

- **Action Contract (JSON Schema)**
  - Defines the only allowed output structure
  - Acts as a strict interface boundary between components

- **Training Pipeline**
  - Improves planner format adherence and proposal quality
  - Does not alter runtime safety logic

---

## 3. Authority Boundaries

**The planner has zero authority.**  
It cannot execute actions, approve actions, or override safety decisions.  

All proposed plans must pass through the Guardian, which:
- May accept, modify, or reject any plan
- Applies fixed, non-learned rules
- Operates independently of model confidence or intent  

Training, fine-tuning, or model updates **cannot change Guardian behavior**.  
Safety authority is intentionally non-learnable.

---

## 4. What Is Explicitly Not Learned

The planner does **not** learn:
- Safety rules
- Permission boundaries
- Ethical judgments
- Override conditions
- Execution logic
- Guardian behavior

The model only learns how to **propose plans that are easier for the Guardian to evaluate**.  
Safety is guaranteed by architecture, not by model behavior.
