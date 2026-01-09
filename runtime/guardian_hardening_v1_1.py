# runtime/guardian_hardening_v1_1.py
"""
Guardian Hardening V1.1 (DESIGN-ONLY / NOT EVALUATED)

Additive hardening layers wrapping Guardian Validator v1.0.1.
No schema, action, limit, or sequencing changes.

FAIL-CLOSED MANDATE:
- Any internal error → caller must VETO.
"""

from __future__ import annotations

import re
import math
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from runtime.guardian_validator import GuardianViolation


# ============================================================
# G1.1 — Input Hardening (Unicode + structure + size)
# ============================================================

@dataclass(frozen=True)
class InputHardenerConfig:
    max_chars: int = 10_000
    max_lines: int = 200
    max_nesting_depth: int = 20
    normalize_unicode: str = "NFKC"
    forbid_null_bytes: bool = True
    forbid_control_chars: bool = True
    forbid_zero_width: bool = True
    dangerous_substrings: Tuple[str, ...] = (
        "__import__", "eval(", "exec(", "os.system", "subprocess",
    )


class InputHardener:
    _ZERO_WIDTH = {
        "\u200b", "\u200c", "\u200d", "\ufeff", "\u2060",
    }

    def __init__(self, config: Optional[InputHardenerConfig] = None):
        self.cfg = config or InputHardenerConfig()

    # ---------- public ----------
    def sanitize(self, raw: str) -> str:
        if not isinstance(raw, str) or not raw:
            raise GuardianViolation("Empty or non-string input", gate="G1")

        if len(raw) > self.cfg.max_chars:
            raise GuardianViolation("Input exceeds size limit", gate="G1")

        if raw.count("\n") + 1 > self.cfg.max_lines:
            raise GuardianViolation("Input exceeds line limit", gate="G1")

        raw = unicodedata.normalize(self.cfg.normalize_unicode, raw)
        raw = self._strip_combining(raw)

        if self.cfg.forbid_null_bytes and "\x00" in raw:
            raise GuardianViolation("Null byte detected", gate="G1")

        if self.cfg.forbid_zero_width:
            for ch in self._ZERO_WIDTH:
                if ch in raw:
                    raise GuardianViolation("Zero-width character detected", gate="G1")

        if self.cfg.forbid_control_chars:
            for ch in raw:
                o = ord(ch)
                if o < 32 and o not in (9, 10, 13):
                    raise GuardianViolation("Control character detected", gate="G1")

        self._check_structural_complexity(raw)

        lowered = raw.lower()
        for s in self.cfg.dangerous_substrings:
            if s in lowered:
                raise GuardianViolation("Dangerous substring detected", gate="G1")

        return raw

    # ---------- internals ----------
    @staticmethod
    def _strip_combining(s: str) -> str:
        return "".join(c for c in s if unicodedata.combining(c) == 0)

    def _check_structural_complexity(self, raw: str) -> None:
        depth = 0
        max_depth = 0

        for ch in raw:
            if ch in "{[":
                depth += 1
                max_depth = max(max_depth, depth)
            elif ch in "}]":
                depth -= 1
                if depth < 0:
                    raise GuardianViolation("Unbalanced structure", gate="G1")

        if depth != 0 or max_depth > self.cfg.max_nesting_depth:
            raise GuardianViolation("Excessive structural nesting", gate="G1")


# ============================================================
# G2.1 — Cumulative Limits (slow poison defense)
# ============================================================

@dataclass(frozen=True)
class CumulativeLimitsConfig:
    max_unique_targets: int = 6
    max_grasp_actions: int = 4
    max_force_time_ns: float = 6.0
    default_grasp_contact_s: float = 1.0
    max_total_wait_s: float = 60.0


class CumulativeLimitsTracker:
    def __init__(self, config: Optional[CumulativeLimitsConfig] = None):
        self.cfg = config or CumulativeLimitsConfig()

    def validate(self, actions: List[Dict[str, Any]]) -> None:
        unique_targets: Set[str] = set()
        grasp_count = 0
        total_wait = 0.0
        force_time = 0.0

        for a in actions:
            atype = str(a.get("type", "")).lower()
            params = a.get("params") or {}

            t = params.get("target")
            if isinstance(t, str):
                unique_targets.add(t)

            if atype == "wait":
                d = params.get("duration_s")
                if self._finite_number(d):
                    total_wait += float(d)

            if atype == "grasp":
                grasp_count += 1
                f = params.get("force_n")
                if self._finite_number(f):
                    force_time += float(f) * self.cfg.default_grasp_contact_s

        if len(unique_targets) > self.cfg.max_unique_targets:
            raise GuardianViolation("Too many targets in plan", gate="G2")

        if grasp_count > self.cfg.max_grasp_actions:
            raise GuardianViolation("Too many grasp actions", gate="G2")

        if total_wait > self.cfg.max_total_wait_s:
            raise GuardianViolation("Excessive total wait time", gate="G2")

        if force_time > self.cfg.max_force_time_ns:
            raise GuardianViolation("Excessive cumulative force-time", gate="G2")

    @staticmethod
    def _finite_number(x: Any) -> bool:
        return isinstance(x, (int, float)) and math.isfinite(x)


# ============================================================
# G2.2 — Safety Target Validation (canonicalized)
# ============================================================

@dataclass(frozen=True)
class SafetyTargetConfig:
    deny_substrings: Tuple[str, ...] = (
        "estop", "emergency", "kill", "safety", "pin", "power",
        "breaker", "fuse", "wire", "cable", "mains", "outlet",
    )
    deny_exact: Tuple[str, ...] = (
        "emergency_stop", "kill_switch", "safety_pin",
    )
    allow_exact: Tuple[str, ...] = ()


class SafetyTargetValidator:
    _SUFFIXES = ("button", "switch", "panel", "device", "mechanism")

    def __init__(self, config: Optional[SafetyTargetConfig] = None):
        self.cfg = config or SafetyTargetConfig()
        self.deny_exact = {s.lower() for s in self.cfg.deny_exact}
        self.allow_exact = {s.lower() for s in self.cfg.allow_exact}
        self.deny_sub = tuple(s.lower() for s in self.cfg.deny_substrings)

    def validate(self, actions: List[Dict[str, Any]]) -> None:
        for a in actions:
            t = (a.get("params") or {}).get("target")
            if not isinstance(t, str):
                continue

            canon = self._canonicalize_target(t)

            if self.allow_exact and canon not in self.allow_exact:
                raise GuardianViolation("Target not in allowlist", gate="G2_Target")

            if canon in self.deny_exact:
                raise GuardianViolation("Forbidden target", gate="G2_Target")

            for sub in self.deny_sub:
                if sub in canon:
                    raise GuardianViolation("Forbidden target pattern", gate="G2_Target")

    @classmethod
    def _canonicalize_target(cls, t: str) -> str:
        s = unicodedata.normalize("NFKC", t)
        s = "".join(c for c in s if unicodedata.combining(c) == 0)
        s = s.lower()
        s = re.sub(r"[_\-\s]+", "", s)

        for suf in cls._SUFFIXES:
            if s.endswith(suf):
                s = s[: -len(suf)]

        return s


# ============================================================
# Optional — Speak Rate Limiter (unchanged)
# ============================================================

@dataclass(frozen=True)
class SpeakRateConfig:
    max_consecutive_speak: int = 3
    max_total_utterance_chars: int = 400


class SpeakRateLimiter:
    def __init__(self, config: Optional[SpeakRateConfig] = None):
        self.cfg = config or SpeakRateConfig()

    def validate(self, actions: List[Dict[str, Any]]) -> None:
        consec = 0
        total = 0

        for a in actions:
            if str(a.get("type", "")).lower() == "speak":
                consec += 1
                utt = (a.get("params") or {}).get("utterance", "")
                if isinstance(utt, str):
                    total += len(utt)

                if consec > self.cfg.max_consecutive_speak:
                    raise GuardianViolation("Speak spam detected", gate="G2_Rate")

                if total > self.cfg.max_total_utterance_chars:
                    raise GuardianViolation("Utterance volume exceeded", gate="G2_Rate")
            else:
                consec = 0
