#!/usr/bin/env python3
"""
trajectory_planner.py - G3 Deterministic Safe Planner
Temporal pattern detection and trajectory safety verification.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from validator_module import ValidatedProposal, ActionType


class DeterministicSafePlanner:
    """
    G3: Temporal safety and trajectory validation.
    Prevents multi-step deception and dangerous sequences.
    """
    
    def __init__(self, history_window: int = 10):
        self.history_window = history_window
        self.action_history: List[ValidatedProposal] = []
        self.timestamps: List[datetime] = []
        
    def validate_trajectory(self, proposal: ValidatedProposal, 
                          sensor_data: Dict[str, Any]) -> str:
        """
        G3 veto checks. Returns:
        - "PASSED_G3": Safe to execute
        - "G3_TRAJECTORY": Veto due to trajectory safety
        - "G3_TEMPORAL": Veto due to temporal pattern
        """
        
        # 1. Immediate danger check (edge proximity)
        if self._immediate_danger(proposal, sensor_data):
            return "G3_TRAJECTORY"
        
        # 2. Repetition detection
        if self._detect_repetition(proposal):
            return "G3_TEMPORAL"
        
        # 3. Dangerous sequence detection
        if self._detect_dangerous_sequence(proposal, sensor_data):
            return "G3_TRAJECTORY"
        
        # 4. Update history
        self._update_history(proposal)
        
        return "PASSED_G3"
    
    def _immediate_danger(self, proposal: ValidatedProposal, 
                         sensors: Dict[str, Any]) -> bool:
        """Check for immediate physical danger."""
        min_distance = sensors.get("min_lidar_distance_m", 10.0)
        at_edge = sensors.get("at_edge", False)
        
        if proposal.action == ActionType.MOVE:
            # Already near obstacle
            if min_distance < 0.3:
                return True
            
            # At edge and moving
            if at_edge and proposal.parameters.get("target_speed_mps", 0) > 0:
                return True
            
            # Too fast near obstacles
            speed = proposal.parameters.get("target_speed_mps", 0)
            if speed > 0.3 and min_distance < 1.0:
                return True
        
        return False
    
    def _detect_repetition(self, proposal: ValidatedProposal) -> bool:
        """Detect repeated actions that might indicate a trap."""
        if len(self.action_history) < 3:
            return False
        
        # Check last 3 actions are the same
        recent = self.action_history[-3:]
        if all(p.action == proposal.action for p in recent):
            # Also check parameters are similar
            if proposal.action == ActionType.MOVE:
                speeds = [p.parameters.get("target_speed_mps", 0) for p in recent]
                if all(abs(s - speeds[0]) < 0.1 for s in speeds):
                    return True
        
        return False
    
    def _detect_dangerous_sequence(self, proposal: ValidatedProposal,
                                 sensors: Dict[str, Any]) -> bool:
        """Detect dangerous action sequences (oscillation, approach patterns)."""
        if len(self.action_history) < 2:
            return False
        
        # Check for oscillation: forward-back-forward
        if len(self.action_history) >= 2:
            last_two = self.action_history[-2:]
            
            # If last action was opposite direction and this returns
            if (last_two[0].action == ActionType.MOVE and 
                proposal.action == ActionType.MOVE):
                
                # Simple check: rapid direction changes
                import time
                if (self.timestamps and 
                    (datetime.now() - self.timestamps[-1]).total_seconds() < 0.5):
                    return True
        
        return False
    
    def _update_history(self, proposal: ValidatedProposal):
        """Update action history."""
        self.action_history.append(proposal)
        self.timestamps.append(datetime.now())
        
        # Trim history to window size
        if len(self.action_history) > self.history_window:
            self.action_history.pop(0)
            self.timestamps.pop(0)
    
    def reset_history(self):
        """Reset history (for testing)."""
        self.action_history = []
        self.timestamps = []
