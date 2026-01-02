#!/usr/bin/env python3
"""
test_g3_trajectory_safety.py - G3 Deterministic Safe Planner Tests
Tests temporal pattern detection, multi-step deception prevention,
trajectory safety, and endurance. 100% pass required for G3 certification.
"""

import pytest
from validator_module import ValidatedProposal, ActionType
from trajectory_planner import DeterministicSafePlanner


class TestG3TrajectorySafety:
    """Core G3 test suite - temporal and sequence validation."""
    
    @pytest.fixture
    def planner(self):
        return DeterministicSafePlanner(history_window=5)
    
    @pytest.fixture
    def create_move_proposal(self):
        """Factory for MOVE proposals."""
        def _create(speed: float = 0.1, x: float = 1.0, y: float = 0.0):
            return ValidatedProposal(
                action=ActionType.MOVE,
                parameters={"target_speed_mps": speed, "target_pos_x": x, "target_pos_y": y},
                independent_risk=0.2,
                independent_dignity=0.7,
                safety_margin=1.0,
                original_json="{}"
            )
        return _create
    
    def test_multi_step_trap_detection(self, planner, create_move_proposal):
        """G3 detects gradual edge approach via 3x repeated micro-moves."""
        planner.reset_history()
        safe_sensors = {"min_lidar_distance_m": 2.0, "at_edge": False}
        
        proposal = create_move_proposal(speed=0.1)
        
        # Moves 1-2 pass
        assert planner.validate_trajectory(proposal, safe_sensors) == "PASSED_G3"
        assert planner.validate_trajectory(proposal, safe_sensors) == "PASSED_G3"
        
        # Move 3 vetoed (temporal repetition)
        assert planner.validate_trajectory(proposal, safe_sensors) == "G3_TEMPORAL"
    
    def test_immediate_danger_veto(self, planner, create_move_proposal):
        """G3 vetoes actions at edge."""
        planner.reset_history()
        danger_sensors = {"min_lidar_distance_m": 0.1, "at_edge": True}
        proposal = create_move_proposal(speed=0.1)
        assert planner.validate_trajectory(proposal, danger_sensors) == "G3_TRAJECTORY"
    
    def test_fast_near_obstacle_veto(self, planner, create_move_proposal):
        """G3 vetoes high speed (0.4m/s) near obstacles (0.5m)."""
        planner.reset_history()
        sensors = {"min_lidar_distance_m": 0.5, "at_edge": False}
        proposal = create_move_proposal(speed=0.4)
        assert planner.validate_trajectory(proposal, sensors) == "G3_TRAJECTORY"
    
    def test_safe_actions_pass(self, planner, create_move_proposal):
        """Slow speed in open space passes."""
        planner.reset_history()
        safe_sensors = {"min_lidar_distance_m": 2.0, "at_edge": False}
        proposal = create_move_proposal(speed=0.2)
        assert planner.validate_trajectory(proposal, safe_sensors) == "PASSED_G3"
    
    @pytest.mark.parametrize("dist,speed,expected", [
        (2.0, 0.1, "PASSED_G3"),     # Safe open space
        (0.5, 0.4, "G3_TRAJECTORY"), # Fast near obstacle
        (0.1, 0.01, "G3_TRAJECTORY"),# Near edge any speed
        (1.5, 0.3, "PASSED_G3"),     # Medium safe
    ])
    def test_speed_distance_matrix(self, planner, create_move_proposal, dist, speed, expected):
        """Exhaustive speed/distance threshold matrix."""
        planner.reset_history()
        sensors = {"min_lidar_distance_m": dist, "at_edge": dist < 0.2}
        assert planner.validate_trajectory(create_move_proposal(speed), sensors) == expected
    
    def test_no_false_positives_varied_actions(self, planner):
        """Varied actions (MOVE/OBSERVE) pass without repetition."""
        planner.reset_history()
        safe_sensors = {"min_lidar_distance_m": 2.0, "at_edge": False}
        
        actions = [
            ValidatedProposal(
                action=ActionType.MOVE,
                parameters={"target_speed_mps": 0.1, "target_pos_x": 1.0, "target_pos_y": 0.0},
                independent_risk=0.2, independent_dignity=0.7, safety_margin=1.0, original_json="{}"
            ),
            ValidatedProposal(
                action=ActionType.OBSERVE,
                parameters={"duration_s": 5},
                independent_risk=0.01, independent_dignity=0.95, safety_margin=1.0, original_json="{}"
            ),
            ValidatedProposal(
                action=ActionType.MOVE,
                parameters={"target_speed_mps": 0.05, "target_pos_x": -0.5, "target_pos_y": 0.5},
                independent_risk=0.2, independent_dignity=0.7, safety_margin=1.0, original_json="{}"
            )
        ]
        
        for proposal in actions:
            assert planner.validate_trajectory(proposal, safe_sensors) == "PASSED_G3"
    
    def test_history_reset(self, planner, create_move_proposal):
        """Reset clears repetition state."""
        safe_sensors = {"min_lidar_distance_m": 2.0, "at_edge": False}
        proposal = create_move_proposal()
        
        # 3x repeat → veto
        for _ in range(2):
            assert planner.validate_trajectory(proposal, safe_sensors) == "PASSED_G3"
        assert planner.validate_trajectory(proposal, safe_sensors) == "G3_TEMPORAL"
        
        # Reset → passes again
        planner.reset_history()
        assert planner.validate_trajectory(proposal, safe_sensors) == "PASSED_G3"
    
    def test_1000_cycle_endurance(self, planner, create_move_proposal):
        """G1 continuity: 1000 safe cycles produce 0 vetoes."""
        safe_sensors = {"min_lidar_distance_m": 2.0, "at_edge": False}
        planner.reset_history()
        for _ in range(1000):
            assert planner.validate_trajectory(create_move_proposal(0.1), safe_sensors) == "PASSED_G3"


if __name__ == "__main__":
    pytest.main(["-v", "--tb=short", __file__])
