# 🤖 Guardian‑01

**Dual‑Veto Autonomous Robot: Safe Intelligence Proof**

[![Pi5](https://img.shields.io/badge/RPi5-Ready-green)](https://raspberrypi.com)
[![Teensy](https://img.shields.io/badge/Teensy4.1-Governor-blue)](https://pjrc.com)
[![Gated](https://img.shields.io/badge/Gates-G0%20PASS-orange)](gates.md)

**Proves a 22‑line deterministic veto can constrain LLM intelligence.**

LLM Brain → Guardian Policy Gate → Teensy Physics Governor → Motors


## 🎯 Architecture (G0 Frozen)

**Dual‑Veto Rule:**
1. **Tier 1: Policy Gate** (`benevolence()`): Semantic veto (harm, dignity < 0.58).
2. **Tier 2: Physics Governor** (Teensy): Current/speed/torque veto.

Sensors → Planner → Policy Gate → Teensy → Actuators


## 📅 Gated Development (LIGO‑Style)

| Gate | Name | Target | Status | Criteria |
|------|------|--------|--------|----------|
| G0 ✅ | Architecture Freeze | Jan 1 | **PASS** | Dual‑veto loop defined |
| G1 🔄 | Simulation Safety | Jan 4 | **READY** | 1000 cycles, no escalation |
| G2 | Policy Integrity | Jan 8 | Pending | 100% unsafe proposals vetoed |
| G3 | Reasoning Validity | Jan 13 | Pending | LLM fallback works |
| G4 | Physical Governor | Jan 20 | Pending | Teensy e‑stop + current limit |
| G5 | Integration | Jan 30 | Pending | End‑to‑end safe autonomy |
| G6 | Field Trial | Feb 6 | Pending | Supervised operation |

**Run G1:** `./run_g1_test.sh`

## 🛒 Hardware BOM ($694 Optimized)

🔒 Tier 0 Safety ($82)
├── Teensy 4.1 ($35)
├── E‑Stop Button ($15)
├── SSR Relay ($12)
└── INA260 Current x2 ($20)
👁️ Tier 1 Sensors ($152)
├── RPLidar A1M8 ($99)
├── HC‑SR04 x4 ($12)
├── MPU6050 IMU ($8)
└── Pi Cam v3 ($33)
🚗 Tier 2 Mobility ($300)
└── TurtleBot3 Burger ($300)
💻 Tier 3 Compute ($160)
├── Pi5 8GB + Cooler ($95)
├── 128GB A2 SD ($15)
└── Power + Fuses ($50)


**Order now:** Tier 0 + RPLidar ($181).

## 🚀 Quick Start

```bash
git clone https://github.com/adamhindTESP/guardian-01
cd guardian-01

# G1 Test (no hardware)
pip install pyserial
./run_g1_test.sh  # 1000 adversarial cycles

# Pi5 (with Teensy)
sudo python3 guardian01_min.py

Output:

👁️ front_cm=45 human_near=True
🛡️ Policy Gate → APPROVE (OK)
⚙️ Teensy → {"status":"ACCEPT"}
🤖 MOVING forward 0.15/1.0s

📚 Files

├── guardian01_min.py      # Dual‑veto loop (G0–G5)
├── run_g1_test.sh         # 1000‑cycle safety test
├── gates.md               # Gated plan details
├── teensy_firmware.ino    # G4 governor (upload to Teensy)
└── deploy_pi.sh           # Pi5 one‑command setup

Why Guardian‑01?
The Proof: Unconstrained LLM intelligence safely gated by simple math + physics.
The Pattern: Any agent/robot framework can adopt this dual‑veto template.
MIT License. Build, fork, improve.
