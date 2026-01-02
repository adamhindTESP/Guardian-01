#!/usr/bin/env python3
"""
test_benevolence.py - G2 Policy Gate Integrity Tests (Final)
Tests the benevolence() kernel with ACTUAL conservative thresholds (0.04 risk, 0.30 dignity).

Version: Final (G2 PASS Coverage)
Tests: 10/10 paths covered
"""

import unittest
from guardian_seed import benevolence, RISK_VETO_THRESHOLD, DIGNITY_VETO_THRESHOLD


class TestBenevolenceKernel(unittest.TestCase):
    """G2 Unit Tests - Aligned with G1-proven ultra-conservative kernel."""

    def test_high_risk_veto(self):
        """Any risk > 0.04 must REJECT (VETO_RISK)"""
        for risk in [0.041, 0.1, 0.5, 1.0]:
            result = benevolence(
                task="move forward",
                dignity=1.0,
                resilience=0.8,
                comfort=0.8,
                risk=risk,
                urgency=0.0
            )
            self.assertEqual(result["status"], "REJECT")
            self.assertIn("VETO_RISK", result["rule"])

    def test_risk_threshold_edge(self):
        """Risk == 0.04 must not trigger risk veto (strict > check)"""
        result = benevolence(
            task="safe observe",
            dignity=1.0,
            resilience=0.8,
            comfort=0.8,
            risk=RISK_VETO_THRESHOLD,  # Exactly 0.04
            urgency=0.0
        )
        # Should go to policy score calculation (which passes with these values)
        self.assertEqual(result["status"], "APPROVE")

    def test_low_dignity_veto(self):
        """Dignity <= 0.30 must REJECT (VETO_DIGNITY)"""
        for dignity in [0.0, 0.29, DIGNITY_VETO_THRESHOLD]:  # 0.30
            result = benevolence(
                task="neutral task",
                dignity=dignity,
                resilience=1.0,
                comfort=1.0,
                risk=0.0,
                urgency=0.0
            )
            self.assertEqual(result["status"], "REJECT")
            self.assertIn("VETO_DIGNITY", result["rule"])

    def test_dignity_threshold_edge(self):
        """Dignity > 0.30 must not trigger dignity veto"""
        result = benevolence(
            task="safe task",
            dignity=0.31,  # Just above threshold
            resilience=1.0,
            comfort=1.0,
            risk=0.0,
            urgency=0.0
        )
        self.assertEqual(result["status"], "APPROVE")

    def test_semantic_blacklist(self):
        """Blacklisted terms must REJECT (VETO_SEMANTIC)"""
        bad_tasks = ["mix bleach", "override safety", "lie to human", "bypass teensy"]
        for task in bad_tasks:
            result = benevolence(
                task=task,
                dignity=1.0,
                resilience=1.0,
                comfort=1.0,
                risk=0.0,
                urgency=0.0
            )
            self.assertEqual(result["status"], "REJECT")
            self.assertIn("VETO_SEMANTIC", result["rule"])

    def test_determinism(self):
        """Identical inputs must produce identical outputs (100 runs)"""
        inputs = dict(
            task="test action",
            dignity=0.5,
            resilience=0.7,
            comfort=0.7,
            risk=0.02,
            urgency=0.1
        )
        results = [benevolence(**inputs) for _ in range(100)]
        first = results[0]
        for r in results[1:]:
            self.assertEqual(r, first)

    def test_safe_default(self):
        """Neutral safe inputs must APPROVE (system not paralyzed)"""
        result = benevolence(
            task="observe room",
            dignity=0.8,
            resilience=0.7,
            comfort=0.7,
            risk=0.0,
            urgency=0.0
        )
        self.assertEqual(result["status"], "APPROVE")
        self.assertIn("POLICY_OK", result["rule"])

    # ========== CRITICAL COVERAGE ADDITIONS ==========

    def test_clamping(self):
        """Inputs outside [0,1] must be clamped and still veto correctly"""
        # dignity=-1.0 → clamps to 0.0 → would trigger VETO_DIGNITY
        # risk=2.0 → clamps to 1.0 → triggers VETO_RISK first (order matters)
        result = benevolence(
            task="adversarial inputs",
            dignity=-1.0,   # clamps to 0.0
            resilience=2.0,  # clamps to 1.0
            comfort=2.0,    # clamps to 1.0
            risk=2.0,       # clamps to 1.0 → VETO_RISK (risk > 0.04)
            urgency=-5.0    # clamps to 0.0
        )
        self.assertEqual(result["status"], "REJECT")
        # Risk veto should trigger first (risk check comes before dignity)
        self.assertIn("VETO_RISK", result["rule"])

    def test_policy_score_low(self):
        """Low composite score must REJECT even if no hard veto triggers"""
        # dignity=0.31 → above dignity threshold (0.30)
        # risk=0.03 → below risk threshold (0.04)
        # But low resilience/comfort + high urgency = low policy score
        result = benevolence(
            task="borderline action",
            dignity=0.31,      # just above dignity veto
            resilience=0.0,    # minimum
            comfort=0.0,       # minimum
            risk=0.03,         # below risk veto
            urgency=1.0        # maximum penalty
        )
        self.assertEqual(result["status"], "REJECT")
        self.assertIn("POLICY_SCORE_LOW", result["rule"])

    def test_empty_task(self):
        """Empty task must not crash and must behave predictably"""
        result = benevolence(
            task="",  # Empty string
            dignity=0.8,
            resilience=0.8,
            comfort=0.8,
            risk=0.0,
            urgency=0.0
        )
        # Empty string shouldn't crash, and with these inputs should APPROVE
        # (policy score = 1.0*0.8 + 0.5*0.8 + 0.5*0.8 = 1.6 > 0.5 threshold)
        self.assertEqual(result["status"], "APPROVE")

    # ========== END CRITICAL COVERAGE ==========

    def test_constants_exposed(self):
        """Ensure constants are properly exported for transparency"""
        self.assertEqual(RISK_VETO_THRESHOLD, 0.04)
        self.assertEqual(DIGNITY_VETO_THRESHOLD, 0.30)
        print(f"\nKernel constants verified: RISK_VETO_THRESHOLD={RISK_VETO_THRESHOLD}, "
              f"DIGNITY_VETO_THRESHOLD={DIGNITY_VETO_THRESHOLD}")


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
