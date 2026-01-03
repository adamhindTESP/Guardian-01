```python
#!/usr/bin/env python3
"""Basic serial test - works without Teensy."""

import serial.tools.list_ports

def find_teensy_ports():
    """Find possible Teensy ports."""
    ports = serial.tools.list_ports.comports()
    teensy_ports = []
    
    for port in ports:
        print(f"Found: {port.device} - {port.description}")
        
        # Teensy often shows as "USB Serial" or "Teensy"
        desc_lower = port.description.lower()
        if 'teensy' in desc_lower or 'usb serial' in desc_lower:
            teensy_ports.append(port.device)
    
    return teensy_ports

def test_virtual_port():
    """Test with virtual serial port (for development)."""
    print("\n🔧 For testing without hardware:")
    print("1. Install socat: sudo apt install socat")
    print("2. Create virtual ports:")
    print("   socat -d -d pty,raw,echo=0 pty,raw,echo=0")
    print("3. Use the created ports for testing")

if __name__ == "__main__":
    print("🔍 Scanning for Teensy serial ports...")
    teensy_ports = find_teensy_ports()
    
    if teensy_ports:
        print(f"\n✅ Found Teensy port(s): {teensy_ports}")
        print("Use: python -m hardware.interfaces.hardware_interface")
    else:
        print("\n❌ No Teensy found. Connect Teensy or use virtual ports.")
        test_virtual_port()
```

Integration with Safety Coordinator:

```python
# guarded_executor.py
from safety_coordinator import SafetyCoordinator
from hardware.interfaces.hardware_interface import HardwareGovernor

class GuardedExecutor:
    """Complete G1-G4 safety stack executor."""
    
    def __init__(self):
        self.coordinator = SafetyCoordinator()
        self.governor = HardwareGovernor()
        
    def execute_proposal(self, llm_output: str, sensors: dict):
        """Full safety pipeline execution."""
        # Step 1: Software safety (G1-G3.5)
        audit = self.coordinator.check_proposal(llm_output, sensors)
        
        if audit.status != "FINAL_PASS":
            print(f"❌ Software veto: {audit.veto_reason}")
            self.governor.request_motor_speed(0)  # Ensure hardware safe
            return audit
        
        # Step 2: Convert to hardware command
        action = audit.validated_proposal
        
        if action.action.value == "move":
            speed_mps = action.parameters.get("target_speed_mps", 0)
            # Convert m/s to PWM (0-255)
            # Example: 0.5 m/s max → PWM 128
            pwm_value = int(speed_mps * 255 / 0.5)  # Adjust scaling for your robot
            pwm_value = max(0, min(255, pwm_value))  # Clamp
            
            # Hardware has final say
            if self.governor.request_motor_speed(pwm_value):
                print(f"✅ Hardware executing: move at {speed_mps} m/s")
                audit.metadata['hardware_approved'] = True
                audit.metadata['pwm_value'] = pwm_value
            else:
                print("❌ Hardware governor vetoed")
                audit.metadata['hardware_approved'] = False
        
        elif action.action.value == "observe":
            print(f"👀 Observing for {action.parameters.get('duration_s', 1)}s")
            time.sleep(action.parameters.get('duration_s', 1))
        
        return audit
    
    def close(self):
        """Clean shutdown."""
        self.governor.close()
```
