# G4 Hardware Bill of Materials (BOM) - CERTIFIED MINIMUM

**Scope:** Gate 4 Safety Governor (2A limit, <100μs veto)  
**Status:** Production-ready specification  
**Total:** $118 CAD | **Lead Time:** 5-7 days Canada

## REQUIRED SAFETY COMPONENTS (8 Core Parts)

| # | Component | Exact Part | Qty | CAD | Link | G4 Role |
|---|-----------|------------|-----|-----|------|---------|
| 1 | MCU | Teensy 4.1 | 1 | $35 | [PJRC](https://www.pjrc.com/store/teensy41.html) | Control + WDT |
| 2 | Current | ACS712-05B | 1 | $5 | [Amazon.ca](https://www.amazon.ca/s?k=acs712+05b) | **Inline sensing** |
| 3 | Relay | 5V SPDT NO | 1 | $8 | [Amazon.ca](https://www.amazon.ca/s?k=5v+spdt+relay) | **Fail-open power cut** |
| 4 | E-Stop | 22mm Red NO | 1 | $12 | [Amazon.ca](https://www.amazon.ca/s?k=22mm+emergency+stop) | Pin 2 ISR |
| 5 | Motor Driver | TB6612FNG | 1 | $8 | [SparkFun #14450](https://www.sparkfun.com/products/14450) | **Bench test only** |
| 6 | PSU | 12V 3A | 1 | $15 | [Amazon.ca](https://www.amazon.ca/s?k=12v+3a+adapter) | Fused power |
| 7 | Fuse Holder | Inline 5A | 1 | $5 | [Amazon.ca](https://www.amazon.ca/s?k=inline+fuse+holder) | 12V protection |
| 8 | Fuses | 5A Fast-Blow | 3 | $2 | [Amazon.ca](https://www.amazon.ca/s?k=5a+blade+fuse) | Spares |

## VALIDATION TOOLS (Required for Evidence)

| # | Component | Exact Part | Qty | CAD | Role |
|---|-----------|------------|-----|-----|------|
| 9 | **Multimeter** | ANENG AN8008 | 1 | $40 | **Current + voltage proof** |
| 10 | **Shunt** | 0.1Ω 3W | 1 | $5 | **2A calibration standard** |

**GRAND TOTAL: $125 CAD**

## WIRING INFRASTRUCTURE

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Power Wire | 16AWG Red/Black | 1m | 12V path (ACS712→Relay→Motor) |
| Signal Wire | 22AWG Multi | 2m | Teensy→components |
| Breadboard | 830pt | 1 | Prototype |
| USB-C | Standard | 1 | Pi→Teensy |

## 🔒 G4 SUBSTITUTION RULES

| Component | Allowed | Requires |
|-----------|---------|----------|
| **ACS712** | ❌ NO | **Re-certify** (firmware change) |
| Relay | 5V SPDT **NO** | Verify fail-open |
| **Teensy** | ❌ NO | **Pinout + WDT** |
| Wire | ≥16AWG power | ✅ OK |

## EXPLICIT G4 SCOPE EXCLUSIONS

❌ Chassis, production motors, batteries, enclosures, cameras → **G5+**

---
**Certified for:** `G4_WIRING_DIAGRAM_ACS712.md` + `g4_governor.ino`  
**Next:** Order → Build → `g4_evidence/` → G4 CERTIFIED
