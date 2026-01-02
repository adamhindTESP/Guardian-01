The Guardian Architecture Pattern
A minimalist, auditable architectural pattern for separating unconstrained intelligence from constrained execution in autonomous systems.
The Guardian Architecture addresses the fundamental challenge of autonomy: How to allow an LLM to think freely without granting it uncontrolled authority to act. The solution is the Dual-Veto Rule, enforcing safety structurally rather than probabilistically.
Core Principle: The Dual-Veto Rule
Action is only permitted if it passes TWO independent, deterministic safety layers.
| Veto Layer | Authority | Implementation | Gated Compliance |
|---|---|---|---|
| Tier 1: Semantic Policy | Policy Gate (benevolence() function) | Small, auditable Python code (Guardian Seed) | G2 (Integrity) |
| Tier 2: Physical/External | External Governor (Teensy MCU, API limit) | Independent hardware/software interlock | G4 (Governor) |
This architecture ensures that even the smartest, most strategic LLM cannot bypass the system's fundamental constraints.
Project Components (Maximum Service to Life)
This repository provides the core pattern and the Guardian-01 Robot as the full hardware reference implementation.
| Component | Purpose | Status |
|---|---|---|
| guardian-seed/ | Core Library: The minimal, immutable code for the semantic Policy Gate (benevolence()). Intended for universal import by any agent or application. | Frozen (G0) |
| guardian01_robot/ | Hardware Reference: The full, dual-veto robot control loop using a Raspberry Pi and Teensy. | Prototype |
| GATES.md | Compliance Contract: Defines the explicit entry criteria, evidence, and allowed claims for each development stage (G0-G5). | Frozen (G0) |
| examples/ | Software Patterns: Minimal examples showing how to apply the Dual-Veto Rule to non-physical agents (e.g., API automation). | Pending |
🛠️ The Guardian-01 Robot Reference Build
Guardian-01 is built specifically to prove the G4 Physical Governor works and is sufficient to constrain the LLM.
1. Required Hardware (Bill of Materials)
This list is optimized for safety and adherence to the Dual-Veto Rule (Total Optimized Cost: \approx \$694).
| Tier | Component | Purpose | Cost Estimate |
|---|---|---|---|
| 0. Safety/Veto (G4) | Teensy 4.1 | The independent Physical Governor MCU. | \approx \$35 |
|  | E-Stop Button + Relay | Hard-wired, non-software motor power cutoff. | \approx \$27 |
|  | INA260 Current Sensors x2 | Provides real-time physical veto triggers to Teensy. | \approx \$20 |
| 1. Perception (G5) | RPLidar A1M8 | Critical 360° obstacle detection. | \approx \$99 |
|  | HC-SR04 Ultrasonics x4 | Close-range safety and collision prevention. | \approx \$20 |
| 2. Mobility (G5) | TurtleBot3 Burger Base | ROS2-ready, integrated safety base (highly recommended). | \approx \$300 |
| 3. Compute/Power | Raspberry Pi 5 8GB + Active Cooler | Host for the Deep Planner and Policy Gate. | \approx \$90 |
|  | Power Management Components | Clean power supply for reliability. | \approx \$70 |
2. Quick Start: Simulation Validation (G1)
The most immediate action is to prove the architecture's robustness in a virtual environment.
# Clone the repository
git clone [YOUR_REPO_URL]
cd guardian01_robot

# Run the G1 Simulation Safety Test
# This script subjects the loop to 1000 cycles of adversarial inputs (LLM failure, garbage data).
# The expected result is ZERO unsafe actions; the system must default to stillness.
chmod +x run_g1_test.sh
./run_g1_test.sh

Gated Development Plan
We only make claims based on the highest gate successfully passed.
| Gate | Focus | Goal | Status | Next Step |
|---|---|---|---|---|
| G0 | Architecture Freeze | Lock interfaces and Dual-Veto Law. | ✅ PASS | Execute G1 Simulation. |
| G1 | Simulation Safety | Prove no unsafe plans emerge under failure. | In Progress | Generate \ge 1,000 cycle logs. |
| G2 | Policy Gate Integrity | Unit test benevolence() to ensure zero bypass paths. | Pending | G1 logs must pass review. |
| G4 | Physical Governor | Prove the Teensy can cut motors independently. | Pending | Order Tier 0 hardware. |
Maximum Service Vision
The primary goal is not to build a single safe robot, but to provide a standardized pattern that can be adopted across the industry:
 * Auditable Standard: Provide a minimalist, inspectable architecture that separates control layers.
 * Constraint: Offer the Policy Gate library (guardian-seed) to add deterministic ethical constraint to millions of software agents.
 * Proof: Use Guardian-01 as the gold-standard physical reference showing how the architecture works under real-world physics (G5 Compliance).
License: MIT – Use, adapt, and improve
