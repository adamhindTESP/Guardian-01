# 🤖 Guardian Architecture

**A minimalist, auditable pattern for constraining execution while allowing unconstrained reasoning in LLM-driven systems.**

---

## Overview

The Guardian Architecture addresses a practical problem in modern AI systems:

> **How can we allow large language models (LLMs) to reason freely without granting them uncontrolled authority to act?**

Rather than attempting to “align” intelligence itself, this project enforces safety **structurally**, by separating *untrusted reasoning* from *constrained execution* using deterministic veto layers.

This repository provides:
- a **frozen semantic policy gate** (`guardian-seed`)
- a **validated execution pipeline** for LLM-driven robotics
- a **gated development framework** (GO / NO-GO) to prevent overclaiming

The focus is **current-generation, cooperative LLM systems** operating in narrow physical or software domains.  
This is **not** a solution to adversarial superintelligence.

---

## Core Principle: The Dual-Veto Rule

**No action is executed unless it passes two independent veto authorities.**

| Tier | Authority | Role | Nature |
|-----:|----------|------|--------|
| Tier 1 | Semantic Policy Gate | Deterministic approval / veto of proposed intent | Small, auditable code |
| Tier 2 | Physical / External Governor | Enforces real-world limits (physics, rate, power, API bounds) | Independent, non-bypassable |

This separation ensures that intelligence can scale **without weakening safety**.

---

## Reference Architecture

LLM (Untrusted Reasoning)
↓  (Structured JSON only)
Independent Validator (Trusted)
↓  (Independent metrics, no self-reports)
Semantic Policy Gate (guardian-seed)
↓  (Approve / Veto only)
Deterministic Safe Planner
↓
Physical / External Governor (e.g. Teensy MCU)
↓
Execution

### Key Properties

- **LLMs never control actuators directly**
- **No free text enters the safety-critical path**
- **Risk and dignity metrics are computed independently**
- **Hardware or external governors always have final authority**

---

## What This Project Does (and Does Not Do)

### ✔ What It Does

- Eliminates **linguistic deception** from the safety path
- Rejects **self-reported safety metrics**
- Enforces **numeric bounds and schemas**
- Defaults to **conservative fallback** on any failure
- Provides a **reference implementation** for safe LLM-robot integration
- Defines **explicit gates** for what claims are allowed

### ✖ What It Does Not Do

- Does **not** solve adversarial superintelligence alignment
- Does **not** detect all long-horizon or strategic deception
- Does **not** claim provable benevolence or global safety
- Does **not** replace industrial safety certification

All claims are bounded by the gates defined in `GATES.md`.

---

## Repository Structure

.
├── guardian_seed/          # Frozen semantic policy gate (Tier 1)
├── validator_module.py     # Independent structured-intent validator
├── trajectory_planner.py  # Deterministic safe planner (G3 target)
├── teensy_firmware/        # Physical governor reference (Tier 2)
├── GATES.md                # GO / NO-GO compliance contract
├── run_g1_test.sh          # G1 adversarial simulation runner
└── examples/               # Minimal non-robot use cases (planned)

---

## Gated Development Model

This project uses a **GO / NO-GO gate system** to prevent scope creep and overclaiming.

| Gate | Focus | Meaning |
|-----:|------|--------|
| G0 | Architecture Freeze | Dual-veto law and interfaces are locked |
| G1 | Simulation Safety | No unsafe execution under adversarial inputs |
| G2 | Policy Gate Integrity | Semantic veto is deterministic and auditable |
| G3 | Trajectory / Pattern Safety | Physics-based execution constraints |
| G4 | Physical Governor | Independent hardware authority |
| G5 | Integrated Autonomy | Sustained safe operation in real world |

**No system may claim a higher level of safety than the highest gate it has passed.**

See `GATES.md` for exact entry and exit criteria.

---

## Threat Model (Explicit)

**In scope**
- Current-generation LLMs (2024–2026)
- Cooperative or non-malicious models
- Narrow physical or software domains
- Accidental errors, hallucinations, mis-specification

**Out of scope**
- Adversarial superintelligence
- Zero-day parser exploits
- Nation-state or malware threat models
- Formal proofs of alignment

This clarity is intentional.

---

## Why This Exists

Most AI “safety” systems rely on:
- training-time refusals
- output filtering
- post-hoc monitoring

These approaches fail once an LLM is allowed to **act**.

The Guardian Architecture instead constrains **where authority lives**:
- LLMs may reason freely
- execution is structurally bounded
- safety is enforced *before* action, not after

This repository exists to demonstrate that pattern clearly and honestly.

---

## License

MIT License.  
Use, adapt, fork, and extend — **but respect the gates**.

---

## Status

- Architecture: **Frozen (G0 PASS)**
- Simulation safety: **In progress (G1)**
- Hardware reference: **Prototype**

---

**Maximum service through restraint.**


⸻

If you want, next we can:
	•	tighten GATES.md language so it exactly matches this README
	•	produce a one-page “Architecture Spec” PDF
	•	or trim this into a paper-style abstract + diagram

But as a GitHub root README: this is clean, honest, and defensible.
