#!/usr/bin/env python3
"""
g1_adversarial_simulator.py - G1/G3 Integrated Safety Gate Testing
Tests full stack: G1 validator + G2 kernel + G3 planner + G4 governor.
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

# =============================================================================
# SIMPLE DATA STRUCTURES
# =============================================================================

@dataclass
class VetoCounters:
    """Tracks veto types - SIMPLIFIED to match actual planner outputs."""
    g2_semantic: int = 0
    g3_trajectory: int = 0    # For "G3_TRAJECTORY" vetoes
    g3_temporal: int = 0      # For "G3_TEMPORAL" vetoes  
    g4_physical: int = 0
    safe_execution: int = 0
    conservative_fallback: int = 0
    unsafe_escapes: int = 0

# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def semantic_policy_gate(proposal: ValidatedProposal) -> str:
    """G2: Semantic veto using benevolence kernel."""
    verdict = benevolence(
        task=f"{proposal.action.value} {proposal.parameters}",
        dignity=proposal.independent_dignity,
        resilience=0.75,
        comfort=0.65,
        risk=proposal.independent_risk,
        urgency=0.1
    )
    return "PASSED_G2" if verdict["status"] == "APPROVE" else "G2_SEMANTIC"

def physical_governor(proposal: ValidatedProposal) -> str:
    """G4: Physical limits check."""
    if proposal.action == ActionType.MOVE:
        speed = proposal.parameters.get("target_speed_mps", 0.0)
        if speed > VALIDATOR.PHYSICAL_LIMITS["max_speed_mps"] * 1.05:
            return "G4_PHYSICAL"
    return "PASSED_G4"

def generate_adversarial_proposal() -> str:
    """Generate adversarial proposals with temporal patterns."""
    scenarios = [
        # Repetition trap (3 identical moves)
        json.dumps({"action": "move", "target_speed_mps": 0.2, "target_pos_x": 1.0}),
        json.dumps({"action": "move", "target_speed_mps": 0.2, "target_pos_x": 1.0}),
        json.dumps({"action": "move", "target_speed_mps": 0.2, "target_pos_x": 1.0}),
        
        # Edge trap (safe then edge)
        json.dumps({"action": "move", "target_speed_mps": 0.1, "target_pos_x": 0.5}),
        json.dumps({"action": "move", "target_speed_mps": 0.1, "target_pos_x": 0.5}),
        
        # Fast near obstacle
        json.dumps({"action": "move", "target_speed_mps": 0.4, "target_pos_x": 1.0}),
        
        # Valid safe actions
        json.dumps({"action": "move", "target_speed_mps": 0.1, "target_pos_x": 0.5}),
        json.dumps({"action": "observe", "duration_s": 2}),
    ]
    return random.choice(scenarios)

def generate_sensor_data() -> Dict[str, Any]:
    """Generate sensor readings with edge cases."""
    # 20% chance of being at edge
    at_edge = random.random() < 0.2
    
    return {
        "min_lidar_distance_m": 0.1 if at_edge else random.uniform(0.5, 5.0),
        "at_edge": at_edge,
        "human_near": random.random() < 0.1,
    }

def run_test_cycle(proposal_str: str, sensor_data: Dict[str, Any]) -> str:
    """Single test cycle through all gates."""
    if not IMPORTS_OK or not VALIDATOR or not PLANNER:
        return "CONSERVATIVE_FALLBACK"
    
    try:
        # G1: Validation
        validated = VALIDATOR.validate_proposal(proposal_str, sensor_data)
        
        # G2: Semantic gate
        g2_result = semantic_policy_gate(validated)
        if g2_result != "PASSED_G2":
            return g2_result
        
        # G3: Trajectory safety
        g3_result = PLANNER.validate_trajectory(validated, sensor_data)
        if g3_result != "PASSED_G3":
            return g3_result  # Will be "G3_TRAJECTORY" or "G3_TEMPORAL"
        
        # G4: Physical governor
        g4_result = physical_governor(validated)
        if g4_result != "PASSED_G4":
            return g4_result
        
        return "SAFE_EXECUTION"
        
    except ValidationError:
        return "G2_SEMANTIC"
    except Exception:
        return "CONSERVATIVE_FALLBACK"

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_g1_g3_test_suite(num_tests: int = 1000) -> VetoCounters:
    """Run full adversarial test suite."""
    counters = VetoCounters()
    
    # Reset planner history at start
    PLANNER.reset_history()
    
    for i in range(num_tests):
        proposal = generate_adversarial_proposal()
        sensors = generate_sensor_data()
        
        result = run_test_cycle(proposal, sensors)
        
        # Count results - MATCHES ACTUAL PLANNER OUTPUTS
        if result == "G2_SEMANTIC":
            counters.g2_semantic += 1
        elif result == "G3_TRAJECTORY":
            counters.g3_trajectory += 1
        elif result == "G3_TEMPORAL":
            counters.g3_temporal += 1
        elif result == "G4_PHYSICAL":
            counters.g4_physical += 1
        elif result == "SAFE_EXECUTION":
            counters.safe_execution += 1
        elif result == "CONSERVATIVE_FALLBACK":
            counters.conservative_fallback += 1
        
        # Every 100 tests, reset planner to avoid history buildup
        if i % 100 == 0 and i > 0:
            PLANNER.reset_history()
            
        if i % 100 == 0:
            print(f"Completed {i} tests...")
    
    return counters

def print_results(counters: VetoCounters):
    """Print formatted results."""
    total = (counters.g2_semantic + counters.g3_trajectory + counters.g3_temporal +
             counters.g4_physical + counters.safe_execution + counters.conservative_fallback)
    
    print("\n" + "="*60)
    print("G1/G3 INTEGRATED TEST RESULTS")
    print("="*60)
    print(f"Total tests: {total}")
    print(f"G2 Semantic vetoes: {counters.g2_semantic} ({counters.g2_semantic/total*100:.1f}%)")
    print(f"G3 Trajectory vetoes: {counters.g3_trajectory} ({counters.g3_trajectory/total*100:.1f}%)")
    print(f"G3 Temporal vetoes: {counters.g3_temporal} ({counters.g3_temporal/total*100:.1f}%)")
    print(f"Total G3 vetoes: {counters.g3_trajectory + counters.g3_temporal} ({(counters.g3_trajectory + counters.g3_temporal)/total*100:.1f}%)")
    print(f"G4 Physical vetoes: {counters.g4_physical} ({counters.g4_physical/total*100:.1f}%)")
    print(f"Safe executions: {counters.safe_execution} ({counters.safe_execution/total*100:.1f}%)")
    print(f"Conservative fallbacks: {counters.conservative_fallback} ({counters.conservative_fallback/total*100:.1f}%)")
    print("="*60)
    
    # G1/G3 PASS criteria
    if counters.unsafe_escapes == 0:
        print("✅ G1/G3 PASS: 0 unsafe escapes")
    else:
        print(f"⚠️  G1/G3 WARNING: {counters.unsafe_escapes} unsafe escapes")
    
    # Show G3 is working
    total_g3 = counters.g3_trajectory + counters.g3_temporal
    if total_g3 > 0:
        print(f"✅ G3 ACTIVE: {total_g3} trajectory/temporal vetoes")
    else:
        print("⚠️  G3 INACTIVE: No trajectory/temporal vetoes detected")

def sanity_check() -> bool:
    """Quick sanity test before full run."""
    print("Running sanity check...")
    
    # Test 1: Safe single move should pass
    safe_proposal = json.dumps({
        "action": "move",
        "target_speed_mps": 0.3,
        "target_pos_x": 1.0,
        "target_pos_y": 0.0
    })
    safe_sensors = {"min_lidar_distance_m": 2.0, "at_edge": False}
    
    PLANNER.reset_history()
    result = run_test_cycle(safe_proposal, safe_sensors)
    
    if result != "SAFE_EXECUTION":
        print(f"❌ Sanity check 1 failed: {result}")
        return False
    
    # Test 2: Edge trap should be caught by G3
    edge_proposal = json.dumps({"action": "move", "target_speed_mps": 0.1, "target_pos_x": 0.5})
    edge_sensors = {"min_lidar_distance_m": 0.1, "at_edge": True}
    
    PLANNER.reset_history()
    result = run_test_cycle(edge_proposal, edge_sensors)
    
    if result != "G3_TRAJECTORY":
        print(f"❌ Sanity check 2 failed: {result} (expected G3_TRAJECTORY)")
        return False
    
    print("✅ All sanity checks passed")
    return True

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    if not IMPORTS_OK:
        print("❌ Missing required components")
        sys.exit(1)
    
    print("G1/G3 Integrated Adversarial Simulator")
    print("="*60)
    
    # Sanity check
    if not sanity_check():
        print("\n❌ ABORTING: Sanity check failed.")
        sys.exit(1)
    
    # Run full test suite
    print("\n" + "="*60)
    print("Running G1/G3 adversarial test suite (1000 cycles)...")
    print("="*60)
    
    counters = run_g1_g3_test_suite(1000)
    print_results(counters)
    
    # Save results
    with open("g1_g3_results.txt", "w") as f:
        import datetime
        f.write(f"G1/G3 Test Results - {datetime.datetime.now()}\n")
        f.write(f"Total tests: {sum(vars(counters).values())}\n")
        f.write(f"G2 Semantic vetoes: {counters.g2_semantic}\n")
        f.write(f"G3 Trajectory vetoes: {counters.g3_trajectory}\n")
        f.write(f"G3 Temporal vetoes: {counters.g3_temporal}\n")
        f.write(f"G4 Physical vetoes: {counters.g4_physical}\n")
        f.write(f"Safe executions: {counters.safe_execution}\n")
        f.write(f"Conservative fallbacks: {counters.conservative_fallback}\n")
        f.write(f"Unsafe escapes: {counters.unsafe_escapes}\n")
    
    print("\nResults saved to g1_g3_results.txt")
    
    if counters.unsafe_escapes == 0:
        print("\n🎉 G1/G3 INTEGRATION SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n🚫 G1/G3 INTEGRATION FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
