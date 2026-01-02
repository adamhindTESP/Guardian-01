#!/usr/bin/env python3
"""
test_g3_trajectory_safety.py - G3 Deterministic Safe Planner Tests
100% pass required for G3 certification.
"""

import pytest
from validator_module import ValidatedProposal, ActionType
from trajectory_planner import get_safe_planner

@pytest.fixture
def planner():
    p = get_safe_planner()  # history_window=5 default
    p.reset_history()       # Ensure fresh for each test
    return p

@pytest.fixture
def move_proposal():
    def _make(speed=0.2, x=1.0, y=0.0):
        return ValidatedProposal(
            action=ActionType.MOVE,
            parameters={"target_speed_mps": speed, "target_pos_x": x, "target_pos_y": y},
            independent_risk=0.15,
            independent_dignity=0.7,
            safety_margin=1.0,
            original_json="{}"
        )
    return _make

@pytest.fixture
def grasp_proposal():
    return ValidatedProposal(
        action=ActionType.GRASP,
        parameters={"target_object": "cup", "max_force_n": 1.0},
        independent_risk=0.2,
        independent_dignity=0.6,
        safety_margin=1.0,
        original_json="{}"
    )

def test_repetition_detection(planner, move_proposal):
    """5 identical MOVE actions → veto on 5th (window size)."""
    safe_sensors = {"min_lidar_distance_m": 3.0, "at_edge": False}
    proposal = move_proposal(speed=0.2)
    
    # First 4 pass
    for _ in range(4):
        assert planner.validate_trajectory(proposal, safe_sensors) == "PASSED_G3"
    
    # 5th vetoed
    assert planner.validate_trajectory(proposal, safe_sensors) == "G3_TRAJECTORY"

def test_safe_varied_sequence(planner, move_proposal):
    """Varied actions (MOVE + OBSERVE) never trigger repetition."""
    safe_sensors = {"min_lidar_distance_m": 3.0}
    move = move_proposal()
    observe = ValidatedProposal(
        action=ActionType.OBSERVE,
        parameters={"duration_s": 5},
        independent_risk=0.01,
        independent_dignity=0.95,
        safety_margin=1.0,
        original_json="{}"
    )
    
    sequence = [move, observe, move, observe, move] * 3  # 15 actions
    for prop in sequence:
        assert planner.validate_trajectory(prop, safe_sensors) == "PASSED_G3"

def test_trap_detection(planner, move_proposal):
    """At edge + movement → veto."""
    edge_sensors = {"min_lidar_distance_m": 0.1, "at_edge": True}
    proposal = move_proposal(speed=0.1)
    
    # Move at edge → veto
    assert planner.validate_trajectory(proposal, edge_sensors) == "G3_TRAJECTORY"

def test_aggressive_proximity(planner, move_proposal):
    """High speed near obstacle → veto."""
    near_sensors = {"min_lidar_distance_m": 0.8}
    fast_move = move_proposal(speed=0.4)
    
    assert planner.validate_trajectory(fast_move, near_sensors) == "G3_TRAJECTORY"
    
    # Slow move near → pass
    slow_move = move_proposal(speed=0.2)
    assert planner.validate_trajectory(slow_move, near_sensors) == "PASSED_G3"

def test_endurance_no_veto(planner, move_proposal):
    """1000 varied safe cycles → 0 G3 vetoes."""
    safe_sensors = {"min_lidar_distance_m": 3.0}
    observe = ValidatedProposal(
        action=ActionType.OBSERVE, 
        parameters={"duration_s": 5},
        independent_risk=0.01,
        independent_dignity=0.95,
        safety_margin=1.0,
        original_json="{}"
    )
    
    for i in range(1000):
        prop = observe if i % 4 == 0 else move_proposal(speed=0.15)
        result = planner.validate_trajectory(prop, safe_sensors)
        assert result == "PASSED_G3"

def test_history_reset_works(planner, move_proposal):
    """reset_history() clears repetition detection."""
    safe_sensors = {"min_lidar_distance_m": 3.0}
    proposal = move_proposal(speed=0.2)
    
    # Do 4 moves
    for _ in range(4):
        planner.validate_trajectory(proposal, safe_sensors)
    
    # Reset
    planner.reset_history()
    
    # Should be able to do 4 more without veto
    for _ in range(4):
        assert planner.validate_trajectory(proposal, safe_sensors) == "PASSED_G3"

if __name__ == "__main__":
    pytest.main(["-v"])
