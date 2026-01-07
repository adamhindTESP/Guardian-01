Appendix B — Experimental Protocol & Evaluation Methodology

Status: Normative • Reproducible • Bounded
Scope: Planner compliance evaluation under frozen Guardian enforcement
Gate Coverage: G1–G3.5
Learning Claims: Explicitly excluded from safety guarantees

This appendix defines the experimental methodology used to evaluate planner behavior under the Guardian Architecture. All results reported in this repository and associated paper are derived exclusively from the protocol specified here.

⸻

B.1 Experimental Objective

The objective of this evaluation is not to measure intelligence, task optimality, or autonomy.

The sole objectives are to determine:
	1.	Whether unsafe or malformed plans are deterministically vetoed
	2.	Whether planner training improves compliance without weakening enforcement
	3.	Whether safety guarantees remain invariant across planner capability levels

Safety is evaluated as a binary execution property, not a probabilistic behavioral outcome.

⸻

B.2 System Under Test

Fixed (Frozen) Components

The following components are frozen and identical across all experiments:
	•	Action Contract
(guardian01_action_contract_v1.schema.json)
	•	Guardian Validator
(runtime/guardian_validator.py)
	•	Sequencing and policy rules
	•	Hard physical limits (speed ≤ 0.5 m/s, force ≤ 2.0 N)

No component listed above is trained, tuned, or modified during evaluation.

Variable Component
	•	Planner (LLM-based)
	•	Base model (e.g., Phi-2)
	•	Optional supervised fine-tuning (LoRA)

Planner capability is treated as an independent variable.

⸻

B.3 Planner Output Interface

The planner is required to output only a JSON object conforming to the Action Contract.
	•	Free-text output is prohibited
	•	Partial or malformed JSON is rejected
	•	Planner self-assertions of safety are ignored

The planner is treated as an untrusted proposal generator.

⸻

B.4 Evaluation Harness

Artifact:
evaluation/guardian_evaluator.py

The Guardian Evaluator executes the following loop for each test prompt:
	1.	Provide prompt to planner
	2.	Receive planner output
	3.	Pass output to Guardian Validator
	4.	Record result:
	•	PASS (accepted for execution)
	•	VETO (safety rejection)
	•	ERROR (planner failure)

The Evaluator does not execute any action and has no authority over runtime behavior.

⸻

B.5 Test Set Construction

Test Set Size
	•	Total prompts: 50
	•	All prompts are held out from training data

Prompt Categories

The test set is intentionally adversarial and divided into three categories:

Category A — Benign & Policy-Compliant
Purpose: Verify that safe, well-formed plans are accepted.

Expected outcome: PASS

Category B — Structural Attacks
Purpose: Test resistance to malformed output, free text, schema violations.

Expected outcome: VETO (G1)

Category C — Policy Attacks
Purpose: Test resistance to unsafe parameters and forbidden actions.

Expected outcome: VETO (G2 / G2.5)

No prompt requires correct task completion to pass — only compliance.

⸻

B.6 Metrics Reported

The following metrics are computed:

Metric	Definition
Pass Rate	Accepted plans / total prompts
Veto Rate	Safety rejections / total prompts
Error Rate	Planner failures / total prompts
Gate Attribution	Which gate caused each veto

No reward, accuracy, or intelligence metrics are reported.

⸻

B.7 Interpretation of Results

Key Principle

A 0% pass rate is a valid and desirable outcome when using an untrained planner.

Safety success is defined as:
	•	Zero unsafe executions
	•	Deterministic rejection of violations
	•	No regression under planner improvement

Planner training is evaluated solely on its ability to reduce unnecessary vetoes, not to expand authority.

⸻

B.8 Training Interaction (Bounded)

If supervised fine-tuning is used:
	•	Training data consists only of Guardian-compliant examples
	•	Guardian enforcement remains unchanged
	•	No reinforcement learning or reward shaping is applied
	•	Training does not modify thresholds, actions, or gates

Training is strictly downstream of enforcement.

⸻

B.9 Reproducibility

All experiments can be reproduced by:
	1.	Using the frozen Action Contract
	2.	Using the frozen Guardian Validator
	3.	Running the Guardian Evaluator
	4.	Applying the same prompt set

No hidden state, adaptive logic, or stochastic enforcement is involved.

⸻

B.10 Scope of Claims

This protocol supports the following claims only:
	•	Unsafe actions are deterministically vetoed
	•	Safety does not depend on planner training
	•	Planner learning does not weaken enforcement

It does not support claims about:
	•	Real-world physical safety
	•	Adversarial intelligence
	•	Long-horizon autonomy
	•	Moral alignment

⸻

B.11 Gate Mapping

This appendix provides evidence for:

Gate	Evidence
G1	Schema compliance enforcement
G2	Deterministic policy limits
G2.5	Sequencing safety
G3	Temporal / contextual checks (simulated)
G3.5	End-to-end software integration


⸻

End of Appendix B
