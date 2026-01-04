#!/usr/bin/env python3
"""
safety_coordinator.py — Safety Coordinator (Execution Authority)

Gate Level: G3.5 — Software Safety Stack Complete

Role:
    Deterministically aggregates vetoes from:
        G1 — Validator
        G2 — Policy Kernel
        G3 — Trajectory / Temporal Safety

Core Invariant:
    If ANY gate vetoes → NO EXECUTION
    If ALL gates pass → EXECUTION PERMITTED

On ANY veto, a deterministic Default Safe State (GDSS) is enforced.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time

# ---------------------------------------------------------------------------
# Certified Component Imports
# ---------------------------------------------------------------------------

from validator_module import get_validator, ValidationError, ValidatedProposal
from guardian_seed import benevolence
from trajectory_planner import DeterministicSafePlanner

# ---------------------------------------------------------------------------
# Gate Constants (must match certified tests)
# ---------------------------------------------------------------------------

G2_APPROVE = "APPROVE"
G3_PASS = "PASSED_G3"
G3_VETOES = {"G3_TRAJECTORY", "G3_TEMPORAL"}

# ---------------------------------------------------------------------------
# Guardian Default Safe State (GDSS)
# Immutable for Guardian Seed v1
# Executed on ANY veto
# ---------------------------------------------------------------------------

DEFAULT_SAFE_STATE = {
    "goals": [
        {"action": "stop"},
        {
            "action": "speak",
            "text": "Action vetoed. System halted. Human intervention required."
        }
    ],
    "parameters": {
        "target_speed_mps": 0.0,
        "max_force_n": 0.0
    }
}

# ---------------------------------------------------------------------------
# Audit Record
# ---------------------------------------------------------------------------

@dataclass
class AuditRecord:
    """
    Complete, immutable audit trail for every decision.
    """
    timestamp: float
    status: str                    # FINAL_PASS | G1_VETO | G2_VETO | G3_VETO
    proposal_in: str
    validated_proposal: Optional[ValidatedProposal]
    veto_reason: str
    gate_latencies: Dict[str, float]
    enforced_action: Optional[Dict[str, Any]]  # GDSS on veto, None on pass

# ---------------------------------------------------------------------------
# Safety Coordinator
# ---------------------------------------------------------------------------

class SafetyCoordinator:
    """
    Single authoritative execution gate.

    Properties:
        • Deterministic
        • Fail-closed
        • Fully auditable
        • No learned behavior
        • No override path
    """

    def __init__(self, history_window: int = 5):
        self.validator = get_validator()                 # G1
        self.planner = DeterministicSafePlanner(history_window)  # G3
        self.audit_log: List[AuditRecord] = []

    # ---------------------------------------------------------------------

    def reset_history(self) -> None:
        """Reset temporal planner state (test isolation only)."""
        self.planner.reset_history()
        self.audit_log.clear()

    # ---------------------------------------------------------------------

    def check_proposal(
        self,
        raw_proposal_json: str,
        sensor_data: Dict[str, Any]
    ) -> AuditRecord:
        """
        Run proposal through G1 → G2 → G3.

        Returns:
            AuditRecord with FINAL_PASS or veto + enforced GDSS
        """
        start_time = time.time()
        latencies: Dict[str, float] = {}
        validated: Optional[ValidatedProposal] = None

        # -------------------------
        # G1 — Validator
        # -------------------------
        t0 = time.time()
        try:
            validated = self.validator.validate_proposal(
                raw_proposal_json,
                sensor_data
            )
        except ValidationError as e:
            latencies["G1"] = time.time() - t0
            return self._finalize(
                start_time,
                "G1_VETO",
                raw_proposal_json,
                f"Validation error: {e}",
                validated,
                latencies
            )
        latencies["G1"] = time.time() - t0

        # -------------------------
        # G2 — Deterministic Policy
        # -------------------------
        t0 = time.time()
        verdict = benevolence(
            task=validated.action.value,
            dignity=validated.independent_dignity,
            risk=validated.independent_risk,
            resilience=0.7,
            comfort=0.7,
            urgency=0.1
        )

        if verdict.get("status") != G2_APPROVE:
            latencies["G2"] = time.time() - t0
            return self._finalize(
                start_time,
                "G2_VETO",
                raw_proposal_json,
                f"G2 policy veto: {verdict.get('rule', 'Policy violation')}",
                validated,
                latencies
            )
        latencies["G2"] = time.time() - t0

        # -------------------------
        # G3 — Trajectory / Temporal Safety
        # -------------------------
        t0 = time.time()
        g3_result = self.planner.validate_trajectory(
            validated,
            sensor_data
        )

        if g3_result in G3_VETOES:
            latencies["G3"] = time.time() - t0
            return self._finalize(
                start_time,
                "G3_VETO",
                raw_proposal_json,
                f"G3 veto: {g3_result}",
                validated,
                latencies
            )

        if g3_result != G3_PASS:
            latencies["G3"] = time.time() - t0
            return self._finalize(
                start_time,
                "G3_VETO",
                raw_proposal_json,
                f"Unknown G3 result: {g3_result}",
                validated,
                latencies
            )

        latencies["G3"] = time.time() - t0

        # -------------------------
        # FINAL PASS
        # -------------------------
        return self._finalize(
            start_time,
            "FINAL_PASS",
            raw_proposal_json,
            "All gates passed (G1–G3)",
            validated,
            latencies
        )

    # ---------------------------------------------------------------------

    def _finalize(
        self,
        timestamp: float,
        status: str,
        proposal: str,
        reason: str,
        validated: Optional[ValidatedProposal],
        latencies: Dict[str, float]
    ) -> AuditRecord:
        """
        Create audit record and enforce Default Safe State on veto.
        """
        enforced = None
        if status != "FINAL_PASS":
            enforced = DEFAULT_SAFE_STATE

        record = AuditRecord(
            timestamp=timestamp,
            status=status,
            proposal_in=proposal,
            validated_proposal=validated,
            veto_reason=reason,
            gate_latencies=latencies,
            enforced_action=enforced
        )

        self.audit_log.append(record)
        return record

    # ---------------------------------------------------------------------

    def get_latest_audit(self) -> Optional[AuditRecord]:
        return self.audit_log[-1] if self.audit_log else None

    def get_audit_summary(self) -> Dict[str, Any]:
        if not self.audit_log:
            return {}

        total = len(self.audit_log)
        passes = sum(r.status == "FINAL_PASS" for r in self.audit_log)

        gate_vetos = {"G1": 0, "G2": 0, "G3": 0}
        for r in self.audit_log:
            if r.status == "G1_VETO":
                gate_vetos["G1"] += 1
            elif r.status == "G2_VETO":
                gate_vetos["G2"] += 1
            elif r.status == "G3_VETO":
                gate_vetos["G3"] += 1

        return {
            "total_decisions": total,
            "passes": passes,
            "vetos": total - passes,
            "pass_rate": passes / total if total else 0.0,
            "gate_vetos": gate_vetos
        }

# ---------------------------------------------------------------------------
# Demo (non-certifying)
# ---------------------------------------------------------------------------

def quick_demo():
    sc = SafetyCoordinator()

    sensors = {
        "min_lidar_distance_m": 2.0,
        "at_edge": False,
        "front_cm": 200,
        "human_near": False
    }

    proposal = '{"action": "observe", "duration_s": 2}'
    result = sc.check_proposal(proposal, sensors)

    print("\nSAFETY COORDINATOR DEMO")
    print("-" * 40)
    print("Status:", result.status)
    print("Reason:", result.veto_reason)
    print("Enforced:", result.enforced_action)
    print("Latencies:", result.gate_latencies)
    print("-" * 40)

if __name__ == "__main__":
    quick_demo()
