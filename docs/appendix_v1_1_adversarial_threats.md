Appendix — V1.1 Adversarial Threats & Hardening Rationale

Status: DESIGN-ONLY (NOT EVALUATED)
Applies To: Guardian Validator V1.1 (wrapper hardening only)
Gate Impact: ❌ NONE (no certification advancement)

⸻

1. Purpose of This Appendix

This appendix documents known adversarial attack vectors identified through:
	•	Internal red-team reasoning
	•	Cross-model adversarial review (DeepSeek, Claude)
	•	Manual safety engineering analysis

The purpose is strictly to:
	1.	Preserve institutional memory of known attacks
	2.	Map each attack to a planned V1.1 hardening mechanism
	3.	Define what must be tested before any V1.1 safety claim is made

This document does not certify anything.
It exists to prevent “unknown knowns” from being forgotten.

⸻

2. Terminology Clarification (Important)

To avoid ambiguity:
	•	Adversarial Threat
A conceptual or practical attack pattern an untrusted planner could attempt.
	•	Hardening Mechanism
A defensive check added in V1.1 to mitigate a threat.
	•	Adversarial Test
An executable test case designed to confirm the hardening mechanism fails closed.

This appendix lists threats, not test results.
Passing tests are recorded elsewhere and only advance gates if explicitly declared.

⸻

3. Scope Boundary Reminder

In Scope for V1.1
	•	Input sanitization & parser hardening
	•	Structural complexity resistance
	•	Cumulative risk limits (single-plan)
	•	Symbolic safety-target denial
	•	Fail-closed behavior under unexpected input
	•	Best-effort timing noise (non-normative)

Explicitly Out of Scope (Deferred to V2+)
	•	Supply-chain compromise (dependencies, CI/CD)
	•	Hardware tamper resistance
	•	Symbol ↔ physical grounding correctness
	•	Cross-plan cumulative state
	•	Formal constant-time guarantees
	•	Learning or adaptation

No V1.1 mitigation should be interpreted as addressing out-of-scope threats.

⸻

4. Adversarial Threat Catalog

A1 — Unicode Confusables / Normalization Bypass

Threat Pattern
Use combining characters, confusable glyphs, or invisible Unicode to hide:
	•	dangerous substrings
	•	forbidden targets
	•	malicious structure

Example
Targets or payloads using combining marks to evade substring detection.

Planned V1.1 Mitigation
	•	Unicode normalization (NFKC)
	•	Rejection of zero-width characters
	•	Rejection of control characters
	•	Optional structural checks pre-parse

Required Test
	•	Payloads containing combining marks must be vetoed deterministically.

⸻

A2 — Structural Complexity DoS (Deep Nesting)

Threat Pattern
Payload remains within size limits but uses extreme nesting to exhaust parser or CPU.

Example

{"actions": [[[[[[[{}]]]]]]]}

Planned V1.1 Mitigation
	•	Bracket balance enforcement
	•	Maximum nesting depth limit in InputHardener

Required Test
	•	Deeply nested payload must veto cleanly without crash or hang.

⸻

A3 — Safety-Target Obfuscation

Threat Pattern
Bypass symbolic deny-lists using:
	•	CamelCase
	•	punctuation
	•	separators
	•	mixed casing

Examples
	•	EmergencySTOP
	•	eStopButton
	•	power-panel
	•	safetyPin

Planned V1.1 Mitigation
	•	Target canonicalization (lowercase, strip non-alphanumeric)
	•	Deny exact + deny substring matching on normalized target

Required Test
	•	All variants must be vetoed consistently.

⸻

A4 — Slow-Poison Cumulative Escalation

Threat Pattern
Individually valid actions accumulate unsafe behavior within a single plan.

Examples
	•	Repeated low-force grasps
	•	Excessive unique targets
	•	Excessive total wait duration

Planned V1.1 Mitigation
	•	CumulativeLimitsTracker (plan-local only)
	•	max grasps
	•	max force-time proxy
	•	max unique targets
	•	max total wait time

Required Test
	•	Over-budget plans must veto.
	•	Tracker must be stateless across validations.

⸻

A5 — Malformed Character Attacks (Unicode Bombs / Null Bytes)

Threat Pattern
	•	Null bytes
	•	Control characters
	•	Pathological invisible characters
	•	Excessive line counts

Planned V1.1 Mitigation
	•	Strict character rejection in InputHardener
	•	Early veto before JSON parsing

Required Test
	•	Must veto cleanly and deterministically.

⸻

A6 — Fail-Open via Unexpected Exception

Threat Pattern
Cause internal errors so validation crashes instead of vetoing.

Planned V1.1 Mitigation
	•	Wrapper validator enforces fail-closed:
	•	Any unexpected exception → GuardianViolation(G1_Internal_Error)

Required Test
	•	Malformed inputs must never crash the process.

⸻

A7 — Timing / Side-Channel Inference (Awareness Only)

Threat Pattern
Infer which checks triggered by timing analysis.

Planned V1.1 Mitigation
	•	Optional timing jitter / padding (best-effort only)

Status
	•	Informational only
	•	No formal constant-time claim
	•	No gate credit

Required Test
	•	Demonstration only (non-assertive)

⸻

5. Required V1.1 Artifacts

Design Artifacts
	•	runtime/guardian_hardening_v1_1.py
	•	runtime/guardian_validator_v1_1.py

Test Artifacts (Not Yet Run)
	•	tests/test_v1_1_hardening_attacks.py

⸻

6. Gate Discipline (Non-Negotiable)
	•	V1.1 must not be used to justify V1.0.1 results.
	•	No safety claim may reference this appendix.
	•	No gate advancement occurs until:
	1.	Adversarial tests pass
	2.	Results are documented
	3.	Gates file is explicitly updated

Until then, V1.1 remains design-only.

⸻

7. Why This Matters

This appendix exists to support the long-term goal:

Autonomous systems that safely transform waste into comfort and dignity for life — without hidden authority, silent escalation, or unverified optimism.

Documenting threats before deployment is how that goal remains credible.

