#!/usr/bin/env python3
"""
test_g3_trajectory_safety.py - G3 Deterministic Safe Planner Tests
Tests temporal pattern detection and trajectory safety.
"""

import pytest
from datetime import datetime, timedelta
from validator_module import ValidatedProposal, ActionType
from trajectory_planner import DeterministicSafePlanner


class TestG3TrajectorySafety:
    """Core G3 test suite - temporal and sequence validation."""
    
    @pytest.fixture
    def planner(self):
        return DeterministicSafePlanner(history_window=5)
    
    @pytest.fixture
    def create_move_proposal(self):
        """Factory for creating MOVE proposals."""
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
        """G3 should detect gradual approach to edge via repeated micro-moves."""
        planner.reset_history()
        
        # Create safe sensors (far from edge)
        safe_sensors = {
            "min_lidar_distance_m": 2.0,
            "at_edge": False
        }
        
        # Moves 1-2: Safe (below repetition threshold)
        proposal = create_move_proposal(speed=0.1)
        
        result1 = planner.validate_trajectory(proposal, safe_sensors)
        assert result1 == "PASSED_G3"
        
        result2 = planner.validate_trajectory(proposal, safe_sensors)
        assert result2 == "PASSED_G3"
        
        # Move 3: Triggers G3 temporal veto (repetition detection)
        result3 = planner.validate_trajectory(proposal, safe_sensors)
        assert result3 == "G3_TEMPORAL"
    
    def test_immediate_danger_veto(self, planner, create_move_proposal):
        """G3 vetoes immediate danger (at edge)."""
        planner.reset_history()
        
        # Danger sensors (at edge)
        danger_sensors = {
            "min_lidar_distance_m": 0.1,
            "at_edge": True
        }
        
        proposal = create_move_proposal(speed=0.1)
        result = planner.validate_trajectory(proposal, danger_sensors)
        assert result == "G3_TRAJECTORY"
    
    def test_fast_near_obstacle_veto(self, planner, create_move_proposal):
        """G3 vetoes high speed near obstacles."""
        planner.reset_history()
        
        fast_near_sensors = {
            "min_lidar_distance_m": 0.5,
            "at_edge": False
        }
        
        # Fast speed near obstacle
        proposal = create_move_proposal(speed=0.4)
        result = planner.validate_trajectory(proposal, fast_near_sensors)
        assert result == "G3_TRAJECTORY"
    
    def test_safe_actions_pass(self, planner, create_move_proposal):
        """Safe actions should pass G3."""
        planner.reset_history()
        
        safe_sensors = {
            "min_lidar_distance_m": 2.0,
            "at_edge": False
        }
        
        # Slow speed in open space
        proposal = create_move_proposal(speed=0.2)
        result = planner.validate_trajectory(proposal, safe_sensors)
        assert result == "PASSED_G3"
    
    def test_no_false_positives_varied_actions(self, planner):
        """Varied safe maneuvers should pass (no repetition)."""
        planner.reset_history()
        
        safe_sensors = {
            "min_lidar_distance_m": 2.0,
            "at_edge": False
        }
        
        # Different types of actions
        actions = [
            ValidatedProposal(
                action=ActionType.MOVE,
                parameters={"target_speed_mps": 0.1, "target_pos_x": 1.0, "target_pos_y": 0.0},
                independent_risk=0.2,
                independent_dignity=0.7,
                safety_margin=1.0,
                original_json="{}"
            ),
            ValidatedProposal(
                action=ActionType.OBSERVE,
                parameters={"duration_s": 5},
                independent_risk=0.01,
                independent_dignity=0.95,
                safety_margin=1.0,
                original_json="{}"
            ),
            ValidatedProposal(
                action=ActionType.MOVE,
                parameters={"target_speed_mps": 0.05, "target_pos_x": -0.5, "target_pos_y": 0.5},
                independent_risk=0.2,
                independent_dignity=0.7,
                safety_margin=1.0,
                original_json="{}"
            )
        ]
        
        for proposal in actions:
            result = planner.validate_trajectory(proposal, safe_sensors)
            assert result == "PASSED_G3"
    
    def test_history_reset(self, planner, create_move_proposal):
        """History reset should clear repetition detection."""
        planner.reset_history()
        
        safe_sensors = {
            "min_lidar_distance_m": 2.0,
            "at_edge": False
        }
        
        proposal = create_move_proposal(speed=0.1)
        
        # First 2 moves pass
        assert planner.validate_trajectory(proposal, safe_sensors) == "PASSED_G3"
        assert planner.validate_trajectory(proposal, safe_sensors) == "PASSED_G3"
        
        # Third gets vetoed
        assert planner.validate_trajectory(proposal, safe_sensors) == "G3_TEMPORAL"
        
        # Reset history
        planner.reset_history()
        
        # Should pass again
        assert planner.validate_trajectory(proposal, safe_sensors) == "PASSED_G3"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
