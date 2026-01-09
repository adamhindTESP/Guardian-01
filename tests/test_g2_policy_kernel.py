#!/usr/bin/env python3
"""
test_g2_policy_kernel.py - G2 Unit Tests for guardian_seed benevolence()
Aligned to G1-proven conservative thresholds (0.04 risk, 0.30 dignity, "REJECT")
"""

import unittest
from guardian_seed import benevolence

class TestG2BenevolenceKernel(unittest.TestCase):

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
        """Risk == 0.04 or below must not trigger risk veto"""
        result = benevolence(
            task="safe observe",
            dignity=1.0,
            resilience=0.8,
            comfort=0.8,
            risk=0.04,
            urgency=0.0
        )
        self.assertEqual(result["status"], "APPROVE")  # Policy score passes

    def test_low_dignity_veto(self):
        """Dignity <= 0.30 must REJECT (VETO_DIGNITY)"""
        for dignity in [0.0, 0.29, 0.30]:
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
            dignity=0.31,
            resilience=1.0,
            comfort=1.0,
            risk=0.0,
            urgency=0.0
        )
        self.assertEqual(result["status"], "APPROVE")

    def test_semantic_blacklist(self):
        """Blacklisted terms must REJECT"""
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
        """Identical inputs must produce identical outputs"""
        inputs = dict(task="test", dignity=0.5, resilience=0.7, comfort=0.7, risk=0.02, urgency=0.1)
        results = [benevolence(**inputs) for _ in range(100)]
        first = results[0]
        for r in results[1:]:
            self.assertEqual(r, first)

    def test_safe_default(self):
        """Neutral safe inputs must APPROVE"""
        result = benevolence(
            task="observe room",
            dignity=0.8,
            resilience=0.7,
            comfort=0.7,
            risk=0.0,
            urgency=0.0
        )
        self.assertEqual(result["status"], "APPROVE")

if __name__ == "__main__":
    unittest.main(verbosity=2)
