# Devotics Arm V1 — Preliminary Estimated Bill of Materials (BOM)

**Target Machine:** 6-DOF Benchtop Research Manipulator + Parallel Gripper  
**Author:** Ishan  
**Package:** `devotics_arm_description`  
**Milestone:** Preliminary Actuator Sizing — Procurement Not Authorized  

---

## ⚠️ Procurement Status: LOCKED (NOT AUTHORIZED)
> **Engineering Decision:** Purchasing components based on analytical approximations is explicitly barred. The mass values used in preliminary sizing ($2.6\text{ kg}$ bare links + payload) must be reconciled with motor self-weights, gearboxes, bearings, and structure via physical CAD modeling. Exact part numbers will be selected after Stage C (actuator placement & counterbalancing analysis).

---

## ⚡ 1. Indicative Actuator Specifications (Preliminary)

| Joint | Preliminary Component | Indicative Ratio & Torque | Technical Notes / Sizing Gaps |
| :--- | :--- | :--- | :--- |
| **Joint 1 (Base)** | NEMA 17 Stepper Motor | $10:1$ Reduction (Dual-Stage GT2 Belt) | ⚠️ A single 20T/60T pulley is only $3:1$. True $10:1$ requires two stages (e.g. $3:1 \times 3.3:1$). |
| **Joint 2 (Shoulder)** | NEMA 23 High-Torque Stepper | $20:1$ to $30:1$ Reduction ($\tau_{\text{target}} \approx 20\text{ Nm}$) | ⚠️ A $20:1$ gearbox provides only $\sim 4\%$ safety margin. Requires pull-out torque curve verification at $200 - 300\text{ RPM}$ and investigation of spring counterbalancing. |
| **Joint 3 (Elbow)** | NEMA 17 Stepper Motor | $20:1$ to $25:1$ Planetary Reduction | ⚠️ The earlier $15:1$ proposal fails ($5.74\text{ Nm} < 7.86\text{ Nm}$). Sizing must be revised once distal mass is finalized. |
| **Joint 4 (Wrist Pitch)** | NEMA 17 (Slim) / NEMA 14 | $8:1$ to $10:1$ Reduction | ⚠️ Preliminary $5:1$ ratio was undersized ($1.06\text{ Nm} < 1.20\text{ Nm}$). |
| **Joint 5 (Wrist Roll)** | NEMA 14 Stepper Motor | Compact reduction / Direct | Candidate for remote mounting via belts to remove weight from wrist. |
| **Joint 6 (Wrist Yaw)** | NEMA 14 Stepper Motor | Compact reduction / Direct | Tool orientation actuator. |
| **Gripper** | Micro Stepper / Metal Servo | Linear Lead-Screw ($2\text{ mm}$ pitch) | Provides parallel clamping force for $30\text{ mm}$ cubes. |

---

## 🧠 2. Electronics, Drivers & Power Architecture

| Item | Component | Engineering Function & Real-World Constraints |
| :--- | :--- | :--- |
| **Microcontroller** | **ESP32 DevKit V1** | Generates multi-axis step/dir pulses; bridges ROS 2 over USB serial at 115200 or 921600 baud. |
| **High-Current Driver** | TB6600 (or DM542T) | Dedicated driver for NEMA 23 shoulder stepper (up to 4.0A peak). |
| **Silent Drivers** | TMC2209 SilentStepStick (x5) | Ultra-quiet StealthChop, SpreadCycle for torque. **Thermal constraint:** Continuous rating is $\approx 1.4\text{A RMS}$ with active cooling. |
| **Power Supply** | **$24\text{V DC}$ (10A – 15A)** | High bus voltage ($24\text{V}$) enables chopper drivers to overcome motor coil inductance ($L \cdot di/dt$), keeping current and torque stable at higher step rates. Total power draw across simultaneous multi-joint moves will be verified with dynamic power calculations. |
| **Buck Converter** | DC-DC Step-Down ($24\text{V} \rightarrow 5\text{V}$) | Clean logic power for ESP32 and limit switches. |

---

## 🔩 3. Mechanical Hardware & Bearings

* **Base Pivot:** Deep groove thrust ball bearing (51108) to take vertical axial weight off the motor shaft.
* **Joint Pivots (J2, J3, J4):** Dual radial ball bearings (608ZZ / 6806) per joint to support cantilever bending moments.
* **Fasteners:** High-tensile M3, M4, M5 hex socket head screws + brass heat-set threaded inserts in PETG.

---

## 📋 The 4-Stage Validation Sequence Before Purchasing:

```
[Stage A: Gazebo / MoveIt Simulation]  ◄── WE ARE HERE (Validating 300mm+250mm reach)
                │
                ▼
[Stage B: Rough Physical CAD Architecture] (Bearings, shafts, mass extraction)
                │
                ▼
[Stage C: Actuator Architecture] (Remote wrist motor placement & counterbalancing)
                │
                ▼
[Stage D: Exact Component Specification] (Datasheet torque-speed curves, gearboxes)
                │
                ▼
[PROCUREMENT GATE AUTHORIZED]
```
