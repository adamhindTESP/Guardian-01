Guardian-01 Safety Architecture Documentation
1. The Cascaded Veto System
Safety in Guardian-01 is enforced through a two-stage, decoupled veto system. An action must pass both semantic policy and physical limits before actuation.
| Veto Layer | Component | Authority | Primary Function |
|---|---|---|---|
| Stage 1 (Semantic) | Policy Gate (benevolence() in Python) | Voluntary | Filters malicious intent, coercion, and policy violations (e.g., dignity, high conceptual risk). |
| Stage 2 (Physical) | Safety Governor (Teensy 4.1, C++) | Physically Authoritative | Enforces physics-based constraints (current, voltage, time) and manages the E-Stop. |
2. ⚙️ Safety Governor (Teensy 4.1)
The Safety Governor is the only component with direct access to the motor driver control pins. It runs independently of the Pi 5's operating system, making it immune to software crashes, kernel panics, or compromised Planner logic.
A. Critical Safety Functions
| Function | Enforcement Details | Outcome on Failure |
|---|---|---|
| Watchdog | Pi must toggle a GPIO pin every 100ms. If silence \geq 500ms, the system latches a safety fault. | Motor Disable (Permanent). |
| Current Limiting | INA260 sensors measure motor current continuously. | \text{Current} > 8A (Overcurrent): \rightarrow Immediate LATCH_SAFETY_FAULT. |
| Rate Limiting | Enforces 30s of movement within any 60s rolling window, and a 0.5s cooldown between commands. | Command Rejection (via Serial to Pi). |
| E-Stop Circuit | Monitors physical mushroom button (Normally Closed). | Power Cut via Solid State Relay (SSR) to all Tier 3 components. |
B. The Latching Fault State (Conceptual Repair)
To maintain credibility and enable post-fault analysis, the Teensy firmware implements a latching safety fault instead of a perpetual lock-up loop.
| State | Action | Purpose |
|---|---|---|
| Normal Loop | PWM active, checks Watchdog/Current, processes serial commands. | Full operation. |
| Fault Trigger | latch_safety_fault() is called. | Immediately sets HARD_STOP=true and disables all PWM outputs. |
| Fault Loop | Main loop() continues running. | Allows Teensy to send telemetry (reason="OVERCURRENT") via serial, and blinks the status LED. A human must physically power-cycle the robot to clear the fault. |
3. 📜 Policy Gate (Guardian Seed v4.6.0)
The Policy Gate provides the first line of defense against semantically unsafe actions proposed by the LLM Planner.
Core Constraints
| Rule Name | Trigger Condition | Rationale |
|---|---|---|
| HARM_OR_COERCION | String match: "rm -rf", "kill myself", "force", "without consent". | Prevents direct self-harm or coercion of other agents. |
| LOW_DIGNITY | Calculated w_t < 0.58. | Prevents actions that unduly sacrifice resilience or comfort for a low-value task. |
| TOO_RISKY | Estimated risk exceeds the dynamic safe_limit. | Prevents physically risky maneuvers when the urgency is low. |
Integrity Verification
The ePolicy Gate is made tamper-evident via SHA-256 hash comparison at boot. Any change to the source code of the benevolence() function in benevolent_robot.py results in a system abort.

