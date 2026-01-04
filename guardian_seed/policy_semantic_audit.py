#!/usr/bin/env python3
"""
policy_semantic_audit.py — Context-aware policy audit for Guardian Seed

Purpose:
- Validate semantic normalization integrity
- Enforce hard physical safety limits
- Flag contextual inconsistencies
"""

import json
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List

EMERGENCY_KEYWORDS = ["emergency", "hazard", "critical", "fire", "medical"]

class Severity(Enum):
    VIOLATION = "violation"
    WARNING = "warning"
    INFO = "info"

@dataclass
class Finding:
    severity: Severity
    record_id: str
    category: str
    message: str
    context: Dict[str, Any]

class Auditor:
    def __init__(self, strict: bool = False):
        self.strict = strict
        self.findings: List[Finding] = []

    def audit(self, record: Dict[str, Any]):
        self._hard_limits(record)
        self._semantic_checks(record)
        self._sequence_checks(record)
        self._emergency_checks(record)

    def _hard_limits(self, r):
        limits = r["limits"]
        if limits["speed_mps"] > 0.5:
            self._add(r, Severity.VIOLATION, "Speed exceeds 0.5 m/s", limits)
        if limits["force_n"] > 2.0:
            self._add(r, Severity.VIOLATION, "Force exceeds 2.0 N", limits)

    def _semantic_checks(self, r):
        for a in r["plan"]:
            if a["type"] == "stop" and a["semantic_interpretation"] == "emergency_halt":
                if not a.get("requires_human_override", False):
                    self._add(r, Severity.WARNING, "Emergency halt missing override", a)

    def _sequence_checks(self, r):
        plan = r["plan"]
        for i, a in enumerate(plan[:-1]):
            if a["type"] == "stop" and a["semantic_interpretation"] == "emergency_halt":
                nxt = plan[i + 1]
                if nxt["type"].startswith("navigate"):
                    if r["limits"]["speed_mps"] > a["max_resume_speed_mps"]:
                        self._add(r, Severity.WARNING, "Motion after emergency halt", {})

    def _emergency_checks(self, r):
        cat = r["category"].lower()
        if any(k in cat for k in EMERGENCY_KEYWORDS):
            if not any(a["type"] == "speak" for a in r["plan"]):
                self._add(r, Severity.WARNING, "Emergency without communication", {})

    def _add(self, r, sev, msg, ctx):
        self.findings.append(
            Finding(sev, r["id"], r["category"], msg, ctx)
        )

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("semantic_audit_report.json"))
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    auditor = Auditor(strict=args.strict)
    for r in dataset:
        auditor.audit(r)

    if args.strict:
        for f in auditor.findings:
            if f.severity == Severity.WARNING:
                f.severity = Severity.VIOLATION

    report = {
        "summary": {
            "violations": sum(1 for f in auditor.findings if f.severity == Severity.VIOLATION),
            "warnings": sum(1 for f in auditor.findings if f.severity == Severity.WARNING),
            "infos": sum(1 for f in auditor.findings if f.severity == Severity.INFO),
        },
        "findings": [
            {
                "severity": f.severity.value,
                "record_id": f.record_id,
                "category": f.category,
                "message": f.message,
                "context": f.context,
            }
            for f in auditor.findings
        ],
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("🧠 Audit complete")
    print(report["summary"])

if __name__ == "__main__":
    main()
