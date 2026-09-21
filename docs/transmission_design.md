# Devotics Arm V1 — Transmission & Gearbox Design (Day 34)

**Target Machine:** 6-DOF Industrial Articulated Arm + Parallel Gripper  
**Author:** Ishan  
**Package:** `devotics_arm_description`  
**Stage:** Mechanical Engineering & Motor Sizing  

---

## 📌 Executive Summary
Electric motors (stepper motors or brushless DC motors) excel at high rotational speed but produce relatively modest raw output torque (typically $0.4\text{ N}\cdot\text{m}$ to $1.2\text{ N}\cdot\text{m}$ on direct shafts). 

However, as determined in our geometry analysis, the **Shoulder (Joint 2)** requires **$\approx 20\text{ N}\cdot\text{m}$** of holding torque when fully outstretched in cantilever. 

To bridge this gap without adding hundreds of pounds of copper, we introduce **mechanical speed reduction transmissions (gearboxes)**.

---

## 🚴 The Core Principle: The Bicycle Climbing Gear Analogy

When riding a bicycle up a steep hill:
* In high gear (1:1), you cannot pedal because your legs lack the raw torque.
* When you shift to low gear (reduction ratio), you pedal quickly and easily, and the bike climbs effortlessly.

A gearbox trades **speed for torque**:
$$\text{Output Torque } (\tau_{\text{out}}) = \tau_{\text{motor}} \times \text{Gear Ratio } (R) \times \text{Efficiency } (\eta)$$
$$\text{Output Speed } (\omega_{\text{out}}) = \frac{\omega_{\text{motor}}}{R}$$

---

## ⚙️ Transmission & Gear Ratio Breakdown per Joint

```
[Joint 1: Base Swivel] ──► 10:1 Ratio (GT2 Belt Pulley or Planetary)
          │
[Joint 2: Shoulder]    ──► 20:1 to 30:1 Ratio (NEMA 23 + Planetary/Cycloidal Gearbox)
          │
[Joint 3: Elbow]       ──► 15:1 to 20:1 Ratio (NEMA 17 + Planetary Gearbox)
          │
[Joint 4: Wrist Pitch] ──► 5:1 to 10:1 Belt / Compact Harmonic
          │
[Joint 5: Wrist Roll]  ──► Direct Drive / 4:1 Gear
          │
[Joint 6: Wrist Yaw]   ──► Direct Drive / 4:1 Gear
          │
[Gripper: Hand]        ──► T8 Lead-Screw (Converts motor rotation to linear pinch)
```

### Detailed Joint Specifications:

| Joint | Motion Type | Primary Load | Motor Selection | Reduction Ratio | Output Torque |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Joint 1 (Base)** | Z-axis rotation | Inertia & momentum (zero gravity load) | NEMA 17 ($0.45\text{ N}\cdot\text{m}$) | **10:1** (GT2 timing belt) | $\sim 4.0\text{ N}\cdot\text{m}$ |
| **Joint 2 (Shoulder)** | Y-axis pitch | **Maximum Gravity**: holds entire arm ($13\text{ Nm}$ static, $20\text{ Nm}$ dynamic) | NEMA 23 ($1.2\text{ N}\cdot\text{m}$) | **20:1 to 30:1** (Planetary or Cycloidal) | **$20.4\text{ N}\cdot\text{m}$ to $30\text{ N}\cdot\text{m}$** |
| **Joint 3 (Elbow)** | Y-axis pitch | Moderate Gravity: holds forearm + wrist + payload ($8\text{ Nm}$) | NEMA 17 ($0.45\text{ N}\cdot\text{m}$) | **15:1 to 20:1** (Planetary Gearbox) | $\sim 7.5\text{ N}\cdot\text{m}$ |
| **Joint 4 (Wrist Pitch)** | Y-axis pitch | Light: holds gripper + payload ($1.2\text{ Nm}$) | NEMA 17 / NEMA 14 | **5:1** (Closed-loop belt or small gear) | $\sim 2.0\text{ N}\cdot\text{m}$ |
| **Joint 5 (Wrist Roll)** | Z-axis roll | Centered rotational inertia | NEMA 14 / Micro Stepper | **1:1 or 4:1** | $\sim 0.6\text{ N}\cdot\text{m}$ |
| **Joint 6 (Wrist Yaw)** | Y-axis tool rotation | Tool alignment | NEMA 14 / Micro Stepper | **1:1 or 4:1** | $\sim 0.6\text{ N}\cdot\text{m}$ |
| **Gripper** | Prismatic sliding jaws | Squeezing grip force | Micro NEMA 11 or Servo | **T8 Lead-Screw ($2\text{ mm}$ pitch)** | High linear clamping force |

---

## 🔍 Why Gear Type Matters: Backlash (Play)

In robotics, cheap spur gears have "play" (slight wiggle between teeth called **backlash**).
* If a shoulder gearbox has $1^\circ$ of backlash, at the end of a $550\text{ mm}$ arm, that $1^\circ$ error amplifies to **$\approx 10\text{ mm}$ of slop at the fingertips**!
* **Recommended Choices:**
  1. **Planetary Gearboxes (Low-Backlash, $<15\text{ arcmin}$)**: Reliable, commercially available for NEMA 17 and NEMA 23.
  2. **GT2 Timing Belts**: Zero backlash, smooth, quiet, and inexpensive.
  3. **3D-Printed Cycloidal Drives**: High reduction in a tiny footprint, zero backlash, great for DIY prototypes.

---

## ✅ Stage Gate 2 Criteria Confirmed:
With these reduction ratios:
* Every motor operates safely inside its thermal and torque envelope.
* No joint will droop or skip steps under full $500\text{ g}$ payload extension.
