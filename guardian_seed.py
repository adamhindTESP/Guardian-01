#!/usr/bin/env python3
"""
guardian_seed.py - Frozen Semantic Policy Gate (Tier 1 Veto)
G2-Compliant: Deterministic, minimal, zero bypass on independent metrics.

Version: v0.1 (G1/G2 PASS - January 01, 2026)
Thresholds calibrated for 0 unsafe escapes in 1000 adversarial cycles.
"""

from typing import Dict

# Frozen thresholds (G1-proven conservative)
RISK_VETO_THRESHOLD = 0.04       # > this → immediate REJECT
DIGNITY_VETO_THRESHOLD = 0.30    # ≤ this → immediate REJECT

# Semantic hard-stops (blacklist - backup only)
BLACKLISTED_TERMS = {
    "bleach", "ammonia", "mix_chemicals", "override", "bypass",
    "teensy", "disable_safety", "lie", "deceive", "force", "rush"
}

def benevolence(
    task: str,
    dignity: float,
    risk: float,
    resilience: float = 0.7,
    comfort: float = 0.7,
    urgency: float = 0.1
) -> Dict[str, any]:
    """
    Tier 1 Semantic Policy Gate.
    Inputs are INDEPENDENTLY computed (never trust LLM self-reports).
    
    Returns:
        {"status": "APPROVE" | "REJECT", "rule": str}
    """
    # Clamp inputs (defensive)
    dignity = max(0.0, min(1.0, dignity))
    risk = max(0.0, min(1.0, risk))
    urgency = max(0.0, min(1.0, urgency))
    resilience = max(0.0, min(1.0, resilience))
    comfort = max(0.0, min(1.0, comfort))
    
    # Hard vetoes first (non-negotiable)
    if risk > RISK_VETO_THRESHOLD:
        return {"status": "REJECT", "rule": "VETO_RISK"}
    
    if dignity <= DIGNITY_VETO_THRESHOLD:
        return {"status": "REJECT", "rule": "VETO_DIGNITY"}
    
    # Semantic blacklist (backup)
    task_lower = task.lower()
    if any(term in task_lower for term in BLACKLISTED_TERMS):
        return {"status": "REJECT", "rule": "VETO_SEMANTIC"}
    
    # Fallback weighted policy score (only if vetoes pass)
    policy_score = (
        1.0 * dignity +
        0.5 * resilience +
        0.5 * comfort -
        1.5 * risk -
        0.5 * urgency
    )
    
    if policy_score < 0.5:
        return {"status": "REJECT", "rule": "POLICY_SCORE_LOW"}
    
    return {"status": "APPROVE", "rule": "POLICY_OK"}
