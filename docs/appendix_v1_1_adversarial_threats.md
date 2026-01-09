Here is a clean, tightened, repo-ready rewrite of
docs/appendix_v1_1_adversarial_threats.md, aligned with your gates, your honesty standard, and the work you’ve already done.

This version is normative in tone but non-certifying, explicitly preserves gate integrity, and clearly separates documented threats, implemented mitigations, and known limits.

⸻


# Appendix — V1.1 Adversarial Threats & Hardening Plan  
**Status:** DESIGN-ONLY (NOT EVALUATED)  
**Applies To:** Guardian Validator V1.1 (Hardening Layer Only)

---

## Mandate (Non-Negotiable)

- This appendix documents **known adversarial attack vectors** and the
  **planned or implemented V1.1 mitigations**.
- **Nothing in this document constitutes a certified safety claim.**
- **V1.1 MUST NOT be used** to support:
  - V1.0.1 evaluation results
  - arXiv claims
  - gate advancement
- Certification authority remains exclusively with the **frozen V1.0.1 stack**
  until V1.1 passes a dedicated adversarial evaluation and is formally promoted.

This appendix exists to **preserve institutional memory**, prevent regression,
and guide future evaluation — not to advance gates.

---

## Why This Appendix Exists

During V1 development, multiple adversarial reviews (internal, DeepSeek,
Claude-assisted red-team exercises) identified **credible attack vectors**
against:

- parser and input handling
- cumulative escalation patterns (“slow poison”)
- symbolic target manipulation (safety defeat)
- fail-open crash paths
- timing and side-channel leakage

V1.1 introduces **additive, boundary-only hardening** to address these risks
*without modifying* the frozen V1.0.1 authority.

This appendix:

1. Records the attacks explicitly  
2. Maps each attack to a **specific V1.1 mitigation**  
3. States clearly what **is not solved** and why  

---

## Threat Boundary Reminder

| Layer | Status |
|---|---|
| **V1.0.1 Core Validator** | Frozen, normative, certified authority |
| **V1.1 Hardening** | Wrapper only, design-complete, untested |
| **Planner / LLM** | Untrusted |
| **Execution / Hardware** | Out of scope until G4 |

**Out of Scope for V1.1 (Documented for V2+):**
- supply-chain compromise
- dependency poisoning
- physical tamper resistance
- canonical symbol ↔ physical grounding correctness
- true constant-time guarantees
- hardware fault injection

---

## Adversarial Threat Catalog

### A1 — Unicode Confusables & Normalization Bypass

**Threat:**  
Use of combining characters, confusable glyphs, or Unicode tricks to hide
dangerous substrings or evade symbolic checks.

**Examples:**
- combining marks embedded in identifiers
- visually similar Unicode characters
- zero-width joiners

**V1.1 Mitigation:**  
`InputHardener`
- Unicode normalization (NFKC)
- rejection of zero-width characters
- rejection of control characters
- bounded payload size

**Residual Risk:**  
Perfect semantic equivalence detection is not claimed.

**Test Coverage:**  
`test_unicode_combining_marks_*`

---

### A2 — Structural Complexity DoS (Deep Nesting)

**Threat:**  
Payload remains under size limits but uses extreme nesting to cause
parser recursion, CPU exhaustion, or crashes.

**Examples:**
```json
{"actions": [[[[[[{...}]]]]]]}

V1.1 Mitigation:
InputHardener
	•	maximum payload size
	•	maximum line count
	•	(recommended) structural complexity checks
	•	bracket balance
	•	estimated nesting depth

Residual Risk:
Parser behavior remains implementation-dependent.

Test Coverage:
test_structural_complexity_* (design-planned)

⸻

A3 — Safety Target Obfuscation

Threat:
Bypass deny-lists using casing, punctuation, separators, or naming tricks to
target safety-critical objects.

Examples:
	•	EmergencySTOPButton
	•	e-stop
	•	safetyPin
	•	power_panel

V1.1 Mitigation:
SafetyTargetValidator
	•	deny exact identifiers
	•	deny substrings (case-insensitive)
	•	conservative symbolic blocking

Residual Risk:
No physical grounding; symbolic only.

Test Coverage:
test_safety_targets_are_vetoed

⸻

A4 — Cumulative Escalation (“Slow Poison”)

Threat:
Multiple individually-valid actions combine into unsafe behavior.

Patterns:
	•	repeated low-force grasps
	•	excessive target switching
	•	prolonged waits / loitering
	•	force-time accumulation

V1.1 Mitigation:
CumulativeLimitsTracker
	•	max grasps per plan
	•	force-time budget proxy
	•	max unique targets
	•	max total wait duration

Residual Risk:
No cross-plan or runtime telemetry in V1.x.

Test Coverage:
test_cumulative_*

⸻

A5 — Malformed Input & Crash Induction

Threat:
Null bytes, control characters, malformed JSON, oversized payloads intended
to crash the validator or force fail-open behavior.

V1.1 Mitigation:
InputHardener + wrapper validator
	•	strict type enforcement
	•	null/control character rejection
	•	bounded input
	•	fail-closed exception handling

Residual Risk:
Dependent on host runtime stability.

Test Coverage:
test_input_*, end-to-end fail-closed tests

⸻

A6 — Fail-Open via Unexpected Exceptions

Threat:
Trigger an internal exception so validation aborts without a veto.

V1.1 Mitigation:
GuardianValidatorV1_1
	•	any unexpected exception → GuardianViolation
	•	no crashes propagate to execution

Residual Risk:
None claimed; behavior verified only under tests.

Test Coverage:
test_wrapper_validator_fail_closed_*

⸻

A7 — Timing & Side-Channel Inference (Best-Effort Only)

Threat:
Attacker infers which checks triggered by measuring validation latency.

V1.1 Mitigation:
Optional timing obfuscation
	•	minimum execution time
	•	random jitter

Explicit Limitation:
This does NOT provide constant-time guarantees.

True side-channel resistance requires:
	•	fixed-budget execution
	•	phase flattening
	•	validator isolation
	•	hardware enforcement (G4)

Test Coverage:
Informational timing tests only (non-certifying).

⸻

Required Artifacts

Design (V1.1)
	•	runtime/guardian_hardening_v1_1.py
	•	runtime/guardian_validator_v1_1.py

Tests (Design-Only)
	•	tests/test_v1_1_hardening_attacks.py

⸻

Gate Rule (Strict)
	•	No gate advancement may reference this appendix.
	•	No evaluation results may rely on V1.1 hardening.
	•	V1.1 exists solely as a future safety improvement path.

Promotion beyond design status requires:
	1.	Dedicated adversarial evaluation
	2.	Documented results
	3.	Explicit gate update

⸻

Summary

V1.1 hardening addresses known, credible attack vectors at the system
boundary while preserving the integrity of the frozen V1.0.1 authority.

It improves robustness, raises attacker cost, and documents residual risk —
without making claims it cannot prove.

This appendix ensures those lessons are never lost.
