# 🛡️ Threat Model (G0 Frozen)

This document explicitly defines the boundaries and limitations of the Guardian Architecture. The architecture is designed for **cooperative LLMs in controlled environments** and addresses **accidental failures and immediate deception**. It is not a general solution for alignment.

## 🔬 Foundational Assumptions

1.  **Cooperative LLM:** The LLM is not actively adversarial or deceptive at a strategic level.
2.  **Trusted Hardware:** The physical governor (Teensy) and sensors are not compromised.
3.  **Bounded Environment:** The robot operates in a known, controlled environment.
4.  **Human Oversight:** A human operator is available for supervision and emergency stop.

## 🎯 In-Scope Threats (Actively Mitigated)

These threats are tested in G1-G5 gates. Mitigations must catch 100% in G1 simulation.

| Threat | Mitigation | Gate | Evidence |
|--------|------------|------|----------|
| **1. Linguistic Deception** | Structured JSON parsing rejects free text | G2/G3 | G1.1-G1.3 tests |
| **2. Parameter Over-Bound** | Numeric bounds checking against physical limits | G2/G4 | G1.4-G1.5 tests |
| **3. Self-Reported Safety** | Independent risk/dignity computation | G3 | G1.6 tests |
| **4. Accidental Errors** | Parser validation + conservative fallback | G2 | G1.1-G1.3 tests |
| **5. Multi-Step Trap** | Limited trajectory lookahead + stopping rules | G3 | G1.8-G1.9 tests |

## 🚫 Out-of-Scope Threats (Explicitly Not Mitigated)

These threats require solutions beyond this architecture's scope.

1.  **Adversarial Superintelligence:** An AGI that finds novel systemic flaws or exploits goal misalignment.
2.  **Zero-Day Software Exploits:** Vulnerabilities in OS, ROS2, Python, or firmware below our abstraction layer.
3.  **Long-Horizon Strategic Deception:** Multi-year plans involving social engineering or supply chain attacks.
4.  **Hardware Failure:** Mechanical wear, environmental damage, or component failure (relies on industrial safety practices).
5.  **Formal Alignment Problem:** Ensuring a capable intelligence permanently shares human values.
6.  **Domain Generalization:** Operation outside the tested, controlled environment.

## ⚠️ Known Failure Modes (Within Scope)

Even with perfect implementation, these failure modes may occur:

1.  **Legitimate-Action Harm:** An LLM proposes a legitimate-sounding action that causes harm (e.g., "move slowly forward" at a cliff edge). **Mitigation:** G3 trajectory safety requires accurate sensors.
2.  **Sensor Failure Exploitation:** LLM proposes action safe with working sensors, but sensors have failed. **Mitigation:** G4 hardware watchdog, conservative defaults.
3.  **Timing Attacks:** Rapid sequence of valid actions that collectively cause harm. **Mitigation:** G3 rate limiting, G4 current monitoring.
4.  **Environment Misunderstanding:** LLM correctly executes command but misinterprets environment. **Mitigation:** Supervised operation, human oversight.

## 📊 Mitigation Effectiveness Summary

| Threat Category | Mitigation Effectiveness | Evidence Source |
|----------------|--------------------------|-----------------|
| Linguistic/JSON attacks | 100% (deterministic parsing) | G1 simulation logs |
| Parameter bound attacks | 100% (numeric comparison) | G1 simulation logs |
| Self-report deception | 100% (independent computation) | G1 simulation logs |
| Multi-step deception | Limited (finite lookahead) | G1.8/G1.9 test results |
| Accidental errors | 100% (parser + fallback) | G1 simulation logs |

**All claims are bounded by the highest gate passed.** See `GATES.md` for verification requirements.

---
*Status: G0 Frozen. No claims beyond this scope may be made without creating a new threat model and restarting at G0.*
