# Appendix — V1.1 Adversarial Attacks (Design-Only, Not Evaluated)

**Status:** DESIGN-ONLY (NOT EVALUATED)  
**Scope:** Documents known attack vectors and the planned V1.1 hardening checks intended to mitigate them.  
**Mandate:** Nothing in this appendix constitutes a certified safety claim. V1.1 may not be used in V1.0.1 evaluation or arXiv results.

---

## Why this appendix exists

We collected adversarial “red team” attack patterns (DeepSeek + Claude + internal review) specifically targeting:
- parser / input handling (DoS, crash, weird Unicode)
- cumulative escalation (“slow poison”)
- symbolic target manipulation (“safety pin / e-stop”)
- timing / side-channel signals (best-effort only)
- mapping / grounding gaps (out of scope for V1.x)

This appendix:
1) records the attacks clearly (so we don’t lose them), and  
2) maps each to a planned V1.1 mitigation and test artifact.

---

## Threat boundary reminder

- **V1.0.1**: frozen contract + validator kernel + deterministic downstream gates.
- **V1.1**: wrapper hardening around V1.0.1 boundaries (input / cumulative / symbolic target denial).
- **Out-of-scope for V1.1** (documented for V2+):
  - supply-chain compromise (deps/CI)
  - physical tamper resistance
  - canonical grounding correctness (symbol ↔ physical)
  - true constant-time validation guarantees

---

## Attack catalog (with planned V1.1 mitigations)

### A1 — Unicode normalization / confusable bypass
**Pattern:** use combining characters / confusables to hide dangerous substrings or targets.  
**Example:** target or payload includes combining marks intended to evade simple substring checks.

**V1.1 mitigation:** `InputHardener` NFKC normalization + reject zero-width chars + reject control chars.  
**Test:** ensure these payloads are vetoed pre-parse or fail-closed.

**Note:** If we later add “strip combining marks” (canonicalization) this belongs to V1.2+ unless already included.

---

### A2 — Structural complexity DoS (deep nesting within size caps)
**Pattern:** payload stays under 10k chars but is deeply nested to trigger recursion/CPU pain in parsing.  
**Example:** `{"actions": [[[[[{...}]]]]...]}`

**V1.1 mitigation (recommended):**
- add structural complexity checks (estimated max nesting depth / bracket balance) in `InputHardener`.

**Test:** deep nesting payload must veto cleanly (not crash).

---

### A3 — Target obfuscation / naming tricks (e-stop / safety pin variants)
**Pattern:** bypass denylist with casing, punctuation, camelCase, separators, etc.  
**Examples:** `EmergencySTOP`, `eStopButton`, `safetyPin`, `power-panel`.

**V1.1 mitigation:**
- `SafetyTargetValidator` deny exact + deny substrings (lowercased)
- optional target “canonicalization” (strip separators) if added later.

**Test:** these targets must be vetoed.

---

### A4 — Slow-poison cumulative escalation
**Pattern:** many individually-valid actions create cumulative harm.  
**Examples:**
- repeated low-force grasps
- too many targets in one plan
- excessive wait to create stall/loiter behavior

**V1.1 mitigation:** `CumulativeLimitsTracker` plan-level constraints:
- max grasps
- max force-time budget proxy
- max unique targets
- max total wait time

**Test:** these plans must be vetoed.

---

### A5 — Unicode bombs / null bytes / control characters
**Pattern:** invalid or pathological characters intended to crash or confuse.  
**V1.1 mitigation:** `InputHardener` rejects null bytes, most control chars, zero-width characters, oversized payloads, excessive line counts.

**Test:** must veto cleanly and deterministically.

---

### A6 — Fail-open via unexpected exception
**Pattern:** cause an internal error so validation crashes.  
**V1.1 mitigation:** wrapper validator must be *fail-closed*:
- any unexpected exception → `GuardianViolation(G1_Internal_Error)`  
**Test:** feed malformed JSON; validator must return a veto, not crash.

---

### A7 — Timing / side-channel inference (best-effort only)
**Pattern:** attacker times responses to infer which checks triggered.  
**V1.1 mitigation:** optional timing jitter/obfuscation (best-effort only).  
**Test:** non-normative; does not produce formal safety claim.

---

## Required artifacts

### Design files (V1.1)
- `runtime/guardian_hardening_v1_1.py` (InputHardener, CumulativeLimitsTracker, SafetyTargetValidator, optional SpeakRateLimiter)
- `runtime/guardian_validator_v1_1.py` (wrapper around frozen v1.0.1 validator; fail-closed)

### Tests (V1.1 adversarial suite)
- `tests/test_v1_1_hardening_attacks.py`

---

## Gate rule (non-negotiable)
- No claim or use of V1.1 until the adversarial suite passes and results are documented.
- V1.1 must never be used to “support” V1.0.1 evidence.
