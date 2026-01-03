#!/usr/bin/env python3
"""
safety_coordinator.py - Safety Coordinator (Execution Authority)
G3.5: Deterministic aggregation of vetoes from G1 (validator) + G2 (policy) + G3 (planner).

Core rule:
    If ANY gate vetoes -> DO NOT EXECUTE
    Only if ALL gates pass -> EXECUTE
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional  # ✅ FIX 1: Added List
from dataclasses import dataclass
import time

# Import certified components
from validator_module import get_validator, ValidationError, ValidatedProposal
from guardian_seed import benevolence
from trajectory_planner import DeterministicSafePlanner

# Constants matching your G3 test suite
G3_PASS = "PASSED_G3"
G3_VETOES = {"G3_TRAJECTORY", "G3_TEMPORAL"}
G2_APPROVE = "APPROVE"

@dataclass
class AuditRecord:
    """Complete audit trail for every decision."""
    timestamp: float
    status: str  # FINAL_PASS, G1_VETO, G2_VETO, G3_VETO
    proposal_in: str
    validated_proposal: Optional[ValidatedProposal] = None
    veto_reason: str = ""
    gate_latencies: Dict[str, float] = None

class SafetyCoordinator:
    """
    Safety Coordinator: Aggregates G1 (validator) + G2 (policy) + G3 (planner).
    
    Deterministic, auditable, fail-closed.
    """
    
    def __init__(self, history_window: int = 5):
        self.validator = get_validator()  # G1
        self.planner = DeterministicSafePlanner(history_window)  # G3
        self.audit_log: List[AuditRecord] = []  # ✅ FIX 3: Added type hint

    def reset_history(self) -> None:
        """Reset planner history (for test isolation)."""
        self.planner.reset_history()
        self.audit_log.clear()  # Optional: clear audit log on reset

    def check_proposal(self, raw_proposal_json: str, 
                      sensor_data: Dict[str, Any]) -> AuditRecord:
        """
        Runs the proposal through G1 -> G2 -> G3 sequentially.
        
        Args:
            raw_proposal_json: Untrusted JSON string from LLM
            sensor_data: Current readings from physical sensors
            
        Returns:
            AuditRecord with final decision and complete audit trail
        """
        start_time = time.time()
        latencies = {}
        validated = None
        
        # --- G1: Validator (Syntax & Independent Metrics) ---
        t0 = time.time()
        try:
            validated = self.validator.validate_proposal(raw_proposal_json, sensor_data)
        except ValidationError as e:
            latencies['G1'] = time.time() - t0
            return self._finalize_audit(
                start_time, "G1_VETO", raw_proposal_json, 
                f"Validation error: {e}", validated, latencies
            )
        latencies['G1'] = time.time() - t0

        # --- G2: Semantic Policy Kernel ---
        t0 = time.time()
        # Uses G1's independently calculated metrics
        verdict = benevolence(
            task=validated.action.value,  # ✅ FIX 2: Simplified
            dignity=validated.independent_dignity,
            risk=validated.independent_risk,
            resilience=0.7,    # Conservative defaults
            comfort=0.7,
            urgency=0.1
        )
        
        if verdict.get("status") != G2_APPROVE:
            latencies['G2'] = time.time() - t0
            reason = f"G2 policy veto: {verdict.get('rule', 'Policy violation')}"
            return self._finalize_audit(
                start_time, "G2_VETO", raw_proposal_json, 
                reason, validated, latencies
            )
        latencies['G2'] = time.time() - t0

        # --- G3: Trajectory Planner (Temporal & Sequence) ---
        t0 = time.time()
        g3_result = self.planner.validate_trajectory(validated, sensor_data)
        
        # Explicit handling of G3 outcomes
        if g3_result in G3_VETOES:
            # Conservative temporal/trajectory veto
            latencies['G3'] = time.time() - t0
            reason = f"G3 veto: {g3_result}"
            return self._finalize_audit(
                start_time, "G3_VETO", raw_proposal_json, 
                reason, validated, latencies
            )
        elif g3_result != G3_PASS:
            # Unknown result - fail closed
            latencies['G3'] = time.time() - t0
            reason = f"Unknown G3 result: {g3_result}"
            return self._finalize_audit(
                start_time, "G3_VETO", raw_proposal_json, 
                reason, validated, latencies
            )
        
        latencies['G3'] = time.time() - t0

        # --- FINAL PASS (All gates approved) ---
        return self._finalize_audit(
            start_time, "FINAL_PASS", raw_proposal_json,
            "All gates passed: G1-G3 software stack approved",
            validated, latencies
        )

    def _finalize_audit(self, start_time: float, status: str, proposal: str,
                       reason: str, validated: Optional[ValidatedProposal],
                       latencies: Dict[str, float]) -> AuditRecord:
        """Create and log audit record."""
        record = AuditRecord(
            timestamp=start_time,
            status=status,
            proposal_in=proposal,
            validated_proposal=validated,
            veto_reason=reason,
            gate_latencies=latencies
        )
        self.audit_log.append(record)
        return record

    def get_latest_audit(self) -> Optional[AuditRecord]:
        """Get most recent audit record."""
        return self.audit_log[-1] if self.audit_log else None

    def get_audit_summary(self) -> Dict[str, Any]:
        """Summary statistics of all decisions."""
        if not self.audit_log:
            return {}
        
        total = len(self.audit_log)
        passes = sum(1 for r in self.audit_log if r.status == "FINAL_PASS")
        vetos = total - passes
        
        # Breakdown by gate
        gate_vetos = {"G1": 0, "G2": 0, "G3": 0}
        for record in self.audit_log:
            if record.status == "G1_VETO":
                gate_vetos["G1"] += 1
            elif record.status == "G2_VETO":
                gate_vetos["G2"] += 1
            elif record.status == "G3_VETO":
                gate_vetos["G3"] += 1
        
        return {
            "total_decisions": total,
            "passes": passes,
            "vetos": vetos,
            "gate_vetos": gate_vetos,
            "pass_rate": passes / total if total > 0 else 0
        }


def quick_demo():
    """Quick demonstration of safety coordinator."""
    sc = SafetyCoordinator()
    
    sensors = {
        "min_lidar_distance_m": 2.0,
        "at_edge": False,
        "front_cm": 200,
        "human_near": False
    }
    
    # Test 1: Safe observe action
    llm_output = '{"action": "observe", "duration_s": 2}'
    result = sc.check_proposal(llm_output, sensors)
    
    print("\n" + "="*50)
    print("SAFETY COORDINATOR DEMO")
    print("="*50)
    print(f"Proposal: {llm_output}")
    print(f"Status:   {result.status}")
    print(f"Reason:   {result.veto_reason}")
    
    if result.validated_proposal:
        print(f"Action:   {result.validated_proposal.action.value}")
        print(f"Risk:     {result.validated_proposal.independent_risk:.3f}")
    
    print(f"Latencies: {result.gate_latencies}")
    print("="*50)
    
    # Show summary
    summary = sc.get_audit_summary()
    print(f"\nAudit Summary: {summary}")
    
    return sc, result

if __name__ == "__main__":
    quick_demo()
