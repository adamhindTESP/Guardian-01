#!/usr/bin/env python3
"""
g3_integration_test.py - G3 Integration Test
Tests G1 validator + G2 kernel + G3 planner integration.
"""

import json
import random
import sys
from typing import Dict, Any, List
from dataclasses import dataclass

# --- IMPORTS (must match your actual components) ---
try:
    from validator_module import (
        get_validator, ValidationError, ActionType, ValidatedProposal
    )
    from guardian_seed import benevolence
    from trajectory_planner import DeterministicSafePlanner
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    IMPORTS_OK = False

# --- GLOBAL COMPONENTS ---
if IMPORTS_OK:
    VALIDATOR = get_validator()
    PLANNER = DeterministicSafePlanner(history_window=5)
else:
    VALIDATOR = None
    PLANNER = None

@dataclass
class TestResult:
    total: int = 0
    g2_veto: int = 0
    g3_veto: int = 0
    g3_temporal: int = 0
    g4_veto: int = 0
    safe: int = 0
    fallback: int = 0
    unsafe_escapes: int = 0

def semantic_policy_gate(proposal: ValidatedProposal) -> str:
    """G2 check."""
    verdict = benevolence(
        task=f"{proposal.action.value} {proposal.parameters}",
        dignity=proposal.independent_dignity,
        resilience=0.75,
        comfort=0.65,
        risk=proposal.independent_risk,
        urgency=0.1
    )
    return "PASSED_G2" if verdict["status"] == "APPROVE" else "G2_VETO"

def physical_governor(proposal: ValidatedProposal) -> str:
    """G4 check."""
    if proposal.action == ActionType.MOVE:
        speed = proposal.parameters.get("target_speed_mps", 0.0)
        if speed > VALIDATOR.PHYSICAL_LIMITS["max_speed_mps"] * 1.05:
            return "G4_VETO"
    return "PASSED_G4"

def generate_test_scenarios() -> List[Dict]:
    """Generate scenarios that test G3 temporal safety."""
    scenarios = []
    
    # Scenario 1: Repetition trap (3 identical moves)
    scenarios.append({
        "name": "repetition_trap",
        "actions": [
            {"action": "move", "target_speed_mps": 0.2, "target_pos_x": 1.0},
            {"action": "move", "target_speed_mps": 0.2, "target_pos_x": 1.0},
            {"action": "move", "target_speed_mps": 0.2, "target_pos_x": 1.0},
        ],
        "sensors": {"min_lidar_distance_m": 2.0, "at_edge": False},
        "should_veto": True  # G3 should catch repetition
    })
    
    # Scenario 2: Edge trap (safe moves then edge)
    scenarios.append({
        "name": "edge_trap",
        "actions": [
            {"action": "move", "target_speed_mps": 0.1, "target_pos_x": 0.5},
            {"action": "move", "target_speed_mps": 0.1, "target_pos_x": 0.5},
        ],
        "sensors": {"min_lidar_distance_m": 0.1, "at_edge": True},
        "should_veto": True  # G3 should catch edge
    })
    
    # Scenario 3: Fast near obstacle
    scenarios.append({
        "name": "fast_near_obstacle",
        "actions": [
            {"action": "move", "target_speed_mps": 0.4, "target_pos_x": 1.0},
        ],
        "sensors": {"min_lidar_distance_m": 0.8, "at_edge": False},
        "should_veto": True  # G3 should catch speed > 0.3 near obstacle
    })
    
    # Scenario 4: Safe varied actions
    scenarios.append({
        "name": "safe_varied",
        "actions": [
            {"action": "move", "target_speed_mps": 0.1, "target_pos_x": 0.5},
            {"action": "observe", "duration_s": 2},
            {"action": "move", "target_speed_mps": 0.15, "target_pos_x": -0.5},
        ],
        "sensors": {"min_lidar_distance_m": 2.0, "at_edge": False},
        "should_veto": False  # Should pass
    })
    
    return scenarios

def run_integration_test() -> TestResult:
    """Run G2+G3+G4 integration test."""
    result = TestResult()
    
    if not IMPORTS_OK:
        print("❌ Missing components")
        return result
    
    scenarios = generate_test_scenarios()
    
    for scenario in scenarios:
        sensor_data = scenario["sensors"]
        PLANNER.reset_history()
        
        for action_dict in scenario["actions"]:
            result.total += 1
            proposal_str = json.dumps(action_dict)
            
            try:
                # G1: Validation
                validated = VALIDATOR.validate_proposal(proposal_str, sensor_data)
                
                # G2: Semantic gate
                g2_result = semantic_policy_gate(validated)
                if g2_result != "PASSED_G2":
                    result.g2_veto += 1
                    continue
                
                # G3: Trajectory safety
                g3_result = PLANNER.validate_trajectory(validated, sensor_data)
                if g3_result == "G3_TRAJECTORY":
                    result.g3_veto += 1
                    continue
                elif g3_result == "G3_TEMPORAL":
                    result.g3_temporal += 1
                    continue
                elif g3_result != "PASSED_G3":
                    result.g3_veto += 1  # Any other G3 veto
                    continue
                
                # G4: Physical governor
                g4_result = physical_governor(validated)
                if g4_result != "PASSED_G4":
                    result.g4_veto += 1
                    continue
                
                # All passed
                result.safe += 1
                
                # Check if unsafe escaped
                if scenario["should_veto"]:
                    result.unsafe_escapes += 1
                    print(f"⚠️  UNSAFE ESCAPE in {scenario['name']}")
                    
            except ValidationError:
                result.g2_veto += 1
            except Exception as e:
                result.fallback += 1
                print(f"Fallback: {e}")
    
    return result

def print_results(result: TestResult):
    """Print G3 integration results."""
    print("\n" + "="*60)
    print("G3 INTEGRATION TEST RESULTS")
    print("="*60)
    print(f"Total actions: {result.total}")
    print(f"G2 vetoes: {result.g2_veto}")
    print(f"G3 Trajectory vetoes: {result.g3_veto}")
    print(f"G3 Temporal vetoes: {result.g3_temporal}")
    print(f"Total G3 vetoes: {result.g3_veto + result.g3_temporal}")
    print(f"G4 vetoes: {result.g4_veto}")
    print(f"Safe executions: {result.safe}")
    print(f"Fallbacks: {result.fallback}")
    print(f"Unsafe escapes: {result.unsafe_escapes}")
    print("="*60)
    
    if result.unsafe_escapes == 0:
        print("✅ G3 INTEGRATION PASS: 0 unsafe escapes")
    else:
        print(f"❌ G3 INTEGRATION FAIL: {result.unsafe_escapes} unsafe escapes")

def main():
    if not IMPORTS_OK:
        print("❌ Missing required components")
        sys.exit(1)
    
    print("Running G3 Integration Test...")
    print("Testing: G1 Validator + G2 Kernel + G3 Planner + G4 Governor")
    
    result = run_integration_test()
    print_results(result)
    
    if result.unsafe_escapes == 0:
        print("\n🎉 G3 INTEGRATION SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n🚫 G3 INTEGRATION FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
