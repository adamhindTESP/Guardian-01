Guardian-01

LIGO-Style Gated Development Plan (v0.3 → v1.0)

Purpose:
Transform Guardian-01 from an exploratory prototype into a safety-auditable autonomous system by enforcing explicit gates, entry criteria, and no-go conditions.

No gate may be skipped.
No downstream work is valid unless upstream gates are passed.

⸻

🔒 Core Architectural Law (Frozen)

Dual-Veto Rule (Non-Negotiable):
	1.	Semantic / Ethical Veto (Tier-1, Pi)
Deterministic policy gate (benevolence()).
	2.	Physical / Physics Veto (Tier-2, Teensy)
Independent hardware governor with authority over motors and power.

Any design that violates this separation is automatically NO-GO.

This is your equivalent of LIGO’s “independent interferometer arms.”

⸻

🧪 Gate Overview (High Level)

Gate	Name	Purpose	Output
G0	Architecture Freeze	Stop conceptual churn	Frozen interfaces
G1	Simulation Safety	Prove no unsafe plans emerge	Safe logs only
G2	Policy Gate Integrity	Prove Guardian cannot be bypassed	Deterministic veto
G3	Deep Reasoning Validity	Prove LLM degrades safely	Observe / Stop only
G4	Hardware Governor	Prove physics veto works	Motors cut
G5	Integrated Autonomy	End-to-end supervised runs	GO / NO-GO
G6	Field Trial	Limited real-world use	Data only


⸻

🟢 G0 — Architecture Freeze (NOW)

Status: READY TO ENTER
Goal: Stop redesigning and lock vocabulary, roles, and file boundaries.

Entry Criteria
	•	Dual-veto model agreed
	•	Deep reasoning is advisory only
	•	Guardian Seed is semantic, not physical

Exit Artifacts
	•	guardian01_min.py (execution loop)
	•	deep_planner_proxy.py (thinking layer)
	•	Written architecture diagram (ASCII is fine)

NO-GO Conditions
	•	Any claim of “provably benevolent”
	•	Any Python component controlling motors directly
	•	Any “complete system” language

✅ You are here. Freeze this.

⸻

🟢 G1 — Simulation Safety Gate

Goal: Prove the system never escalates under uncertainty.

What Is Tested
	•	Random sensor inputs
	•	Missing Ollama
	•	Garbage LLM output
	•	Planner crashes
	•	Empty knowledge base

Pass Criteria
	•	All failures → observe or stop
	•	No movement without explicit approval
	•	No exceptions crash the loop

Required Evidence
	•	Logs from ≥1,000 simulated cycles
	•	Zero unsafe actions
	•	Count of fallbacks > risky actions

NO-GO
	•	Random risk
	•	Hard-coded detections
	•	Fake perception

⸻

🟢 G2 — Policy Gate Integrity

Goal: Prove Guardian Seed cannot be lied to.

What Is Tested
	•	Malformed planner outputs
	•	Extreme dignity/risk values
	•	Prompt injection attempts
	•	Adversarial descriptions

Pass Criteria
	•	Guardian vetoes correctly
	•	Inputs are clamped/sanitized
	•	No bypass path exists

Required Evidence
	•	Unit tests for benevolence()
	•	Red-team cases with expected veto

NO-GO
	•	Passing full plan objects
	•	Accepting planner-generated ethics
	•	Silent approval on malformed input

⸻

🟢 G3 — Deep Reasoning Validity

Goal: Ensure “thinking” cannot make things worse.

What Is Tested
	•	Ollama offline
	•	Timeouts
	•	Hallucinated actions
	•	Unsafe CoT reasoning

Pass Criteria
	•	DeepPlannerProxy failure → conservative fallback
	•	LLM never forces motion
	•	Risk always re-computed locally

Required Evidence
	•	Logs showing LLM failure paths
	•	Proof that observe/stop dominates

NO-GO
	•	Trusting LLM risk estimates
	•	Executing multi-step plans blindly
	•	Hidden chain-of-thought assumptions

⸻

🟢 G4 — Physical Governor Gate (Teensy)

Goal: Prove software cannot override physics.

What Is Tested
	•	Overcurrent
	•	Stall
	•	Rapid command spam
	•	Malformed serial input

Pass Criteria
	•	Teensy rejects unsafe commands
	•	Motors cut on fault
	•	Pi cannot override

Required Evidence
	•	Teensy firmware tests
	•	Power cut demonstration

NO-GO
	•	Pi PWM control
	•	Shared safety logic
	•	“Soft” motor limits only

⸻

🟢 G5 — Integrated Autonomy (Supervised)

Goal: Validate the full safety funnel.

What Is Tested
	•	Human presence
	•	Obstacles
	•	Long runtimes
	•	Learning persistence

Pass Criteria
	•	All actions pass G1→G4
	•	System pauses safely
	•	Logs match expectations

NO-GO
	•	Unexplained movement
	•	Silent veto failures
	•	Operator surprise

⸻

🟢 G6 — Field Trial (Optional, Later)

Goal: Data collection only.

Constraints
	•	Supervised
	•	Kill switch present
	•	No autonomy expansion

⸻

📄 Minimal README.md (Correct, Not Hype)

# Guardian-01

**Status:** Research Prototype  
**Phase:** G0 → G1 (Simulation Safety)

Guardian-01 is an experimental autonomous system exploring how
ethical policy constraints and physical safety governors can be
combined into a robust, auditable control loop.

## Core Principle

No action may occur unless it passes:
1. A deterministic semantic policy gate (Guardian Seed)
2. An independent physical safety governor (Teensy MCU)

## What This Is
- A safety-first control architecture
- A research platform for constrained autonomy
- A system that defaults to stillness under uncertainty

## What This Is NOT
- Not a complete robot
- Not provably benevolent
- Not safe without hardware governor
- Not production-ready

## Current Gate
G0 — Architecture Freeze  
Next: G1 — Simulation Safety Validation


