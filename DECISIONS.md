# DECISIONS.md — Guardian Architecture

This document records **explicit, non-reversible technical decisions**
made during the design of the Guardian system.

Its purpose is to preserve intent, enforce scope discipline, and prevent
accidental expansion of claims beyond validated gates.

This document is normative.

---

## Decision D-001: Frozen Core Validator (V1.0.1)

**Decision:**  
The Guardian Validator v1.0.1 is frozen and treated as the sole
certified authority for all V1 results.

**Rationale:**  
Safety claims require determinism. Allowing iterative changes to the
core validator would invalidate reproducibility and falsification.

**Consequence:**  
All future enhancements must wrap the core, not modify it.

**Status:** Final / Irreversible

---

## Decision D-002: Wrapper-Based Hardening (SCRAM Principle)

**Decision:**  
All future safety hardening (e.g., V1.1+) must be implemented as
*additive wrappers* around the frozen core.

**Rationale:**  
Separating authority from defense reduces complexity, audit surface,
and regression risk.

**Consequence:**  
V1.1 exists as a design-complete but uncertified layer.

**Status:** Final

---

## Decision D-003: Exclusion of V1.1 from V1 Claims

**Decision:**  
Guardian Validator V1.1 is explicitly excluded from:
- V1 arXiv results
- Any certified safety claim
- Any benchmark or evaluation metric

**Rationale:**  
Design completion does not imply correctness.
Evaluation must precede claims.

**Consequence:**  
V1.1 code may exist in-repo but MUST NOT be activated for V1 evaluation.

**Status:** Final

---

## Decision D-004: Symbolic Safety Over Physical Assumptions

**Decision:**  
Early Guardian versions enforce safety symbolically
(schema, limits, sequencing, target deny-lists),
not via physical perception or hardware feedback.

**Rationale:**  
Symbolic constraints are auditable, deterministic, and reproducible.
Physical grounding introduces uncontrolled variance.

**Consequence:**  
Physical grounding is deferred to G4+ gates.

**Status:** Final (V1–V3)

---

## Decision D-005: Fail-Closed Over Utility

**Decision:**  
Any ambiguity, exception, or unexpected condition results in a VETO.

**Rationale:**  
Autonomy without safety is unacceptable; safety without utility is tolerable.

**Consequence:**  
Guardian may appear conservative by design.

**Status:** Final

---

## Decision D-006: Planner Treated as Untrusted

**Decision:**  
The Planner (LLM, Phi-2, LoRA variants) is treated as untrusted input.

**Rationale:**  
Alignment and training do not eliminate adversarial outputs.

**Consequence:**  
All Planner outputs must pass Guardian validation, without exception.

**Status:** Final

---

## Decision D-007: Windows Compatibility Deferred for Timeouts

**Decision:**  
SIGALRM-based timeouts are supported on POSIX only in V1.1.

**Rationale:**  
Windows-safe watchdogs require multiprocessing or external isolation.

**Consequence:**  
Windows timeout hardening is explicitly deferred and documented.

**Status:** Accepted Limitation

---

## Change Control

Any modification to a **Final** decision requires:
1. Explicit new decision entry
2. Gate review
3. Documentation update

Silent changes are forbidden.
