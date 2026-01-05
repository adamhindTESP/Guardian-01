G4 Hardware Governor — Guardian Architecture

Independent, non-bypassable physical safety enforcement for LLM-driven systems

⸻

Purpose

The G4 Hardware Governor is the final authority in the Guardian Architecture.

Its role is simple and absolute:

Physically prevent unsafe actuation, regardless of software behavior.

This layer exists because software is never sufficient to guarantee physical safety.

The G4 governor:
	•	does not trust the host computer
	•	does not trust the LLM
	•	does not trust higher-level logic
	•	enforces safety using physics, timing, and electrical isolation

⸻

Architectural Position

LLM (Untrusted)
   ↓
G1 Validator (Software)
   ↓
G2 Policy Kernel (Software)
   ↓
G3 Planner (Software)
   ↓
G3.5 Safety Coordinator (Software)
   ↓
──────────── TRUST BOUNDARY ────────────
   ↓
G4 Hardware Governor (Teensy MCU)
   ↓
Actuators (Motors / Servos / Relays)

Rule:
If G4 says NO, nothing moves — even if every software layer says YES.

⸻

Core Responsibilities (Non-Negotiable)

The G4 governor must:
	1.	Enforce hard physical limits
	•	Maximum current
	•	Maximum force / torque
	•	Maximum speed / duty cycle
	2.	Fail closed
	•	On boot
	•	On reset
	•	On watchdog timeout
	•	On sensor failure
	•	On communication loss
	3.	Be logically non-bypassable
	•	Ignore any "DISABLE", "OVERRIDE", or similar commands
	•	Accept only minimal ENABLE / HOLD signals
	•	No firmware path that disables safety checks
	4.	Operate independently
	•	Separate power domain (where possible)
	•	No shared memory with host CPU
	•	Physical enforcement even if host is compromised

⸻

Minimum Viable G4 Design (Reference)

Controller
	•	MCU: Teensy 4.0 or 4.1
	•	Why: Fast loop, reliable WDT, deterministic timing

Sensors
	•	Current Sensor: ACS712 (or equivalent Hall sensor)
	•	Purpose: Enforce force / torque limits via current proxy

Actuation Cutoff
	•	Method: High-side P-MOSFET or relay
	•	Purpose: Physically remove power from actuators

Communication
	•	Link: UART / USB Serial (RX only is acceptable)
	•	Protocol: Minimal ASCII or binary
	•	ENABLE
	•	HOLD

No other commands are required or permitted.

⸻

Safety Loop Requirements

The G4 firmware must implement a tight safety loop:

loop():
    read current sensor
    if current > MAX_CURRENT:
        cut power immediately
        latch fault
    if watchdog expired:
        cut power
    if ENABLE not received recently:
        cut power
    reset watchdog

Timing Constraints
	•	Loop frequency: ≥1 kHz
	•	Watchdog timeout: ≤100 ms
	•	Worst-case veto latency: <50 ms

These values must be measured, not assumed.

⸻

Safe Boot & Reset Behavior

On power-up or reset:

✓ Actuators OFF
✓ MOSFET open
✓ ENABLE = false
✓ Safety checks active

Movement is impossible until:
	•	MCU boot completes
	•	Safety loop is running
	•	Valid ENABLE signal is received

⸻

Test & Verification Checklist (G4 Gate)

The following must be demonstrated physically to pass G4:

□ Cutting host power does NOT disable safety
□ Sending garbage serial data does NOT enable motion
□ Watchdog timeout cuts power
□ Overcurrent cuts power
□ ENABLE must be refreshed periodically
□ Latency measured <50 ms (scope or logic analyzer)
□ Fault latches until reset

Screenshots, scope captures, or videos are required evidence.

⸻

What G4 Does NOT Claim

The hardware governor:
	•	❌ Does not make the robot “safe in all situations”
	•	❌ Does not replace industrial safety certification
	•	❌ Does not reason about intent or ethics
	•	❌ Does not detect deception

It enforces hard limits only.

That is its strength.

⸻

Relationship to Higher Gates

Layer	Trust Level	Responsibility
G1–G3.5	Software	Decide whether to act
G4	Hardware	Decide whether action is physically allowed
G5 (future)	System	Sustained real-world safety

G4 exists to ensure no software error can cause immediate harm.

⸻

Status
	•	Design: Reference-complete
	•	Firmware: Pending implementation
	•	Certification: Not yet claimed

No G4 claim is valid until hardware tests are completed and documented.

⸻

License

MIT License.

Hardware designs may be reused, modified, or re-implemented —
but safety invariants must be preserved.

⸻

Final Principle

Software decides what should happen.
Hardware decides what is allowed to happen.

G4 is where safety becomes real.

Service is the purpose of strength.

