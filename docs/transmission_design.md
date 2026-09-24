# Devotics Arm V1 — Preliminary Transmission Design & Motor Sizing Review

**Target Machine:** 6-DOF Benchtop Research Manipulator + Parallel Gripper  
**Author:** Ishan  
**Package:** `devotics_arm_description`  
**Stage:** Preliminary Actuator Sizing (Procurement Not Authorized)  

---

## 📌 1. Critical Engineering Reality Checks

### A. Holding Torque $\neq$ Running Torque
A stepper motor's datasheet "Holding Torque" (e.g., $1.2\text{ N}\cdot\text{m}$ for NEMA 23, $0.45\text{ N}\cdot\text{m}$ for NEMA 17) only applies at **zero velocity (standstill)**. 
* As rotational speed increases, motor winding inductance ($L$) resists rapid current changes ($V = L \cdot di/dt$), causing motor torque to drop off precipitously.
* At our target joint speed of $\omega = 60^\circ/\text{s}$ ($10\text{ RPM}$ at the joint):
  * With a $20:1$ reduction, the motor shaft turns at **$200\text{ RPM}$**.
  * With a $30:1$ reduction, the motor shaft turns at **$300\text{ RPM}$**.
* Motor selection must be evaluated against the **pull-out torque curve at $200 - 300\text{ RPM}$ at $24\text{V}$**, not static holding torque.

---

### B. Joint Torque Margin & Sizing Discrepancies

A rigorous review of the preliminary sizing calculations reveals that several joints are either marginal or fundamentally undersized:

| Joint | Target Static + Dynamic Requirement | Proposed Baseline Calculation | Net Output Torque | Status / Engineering Evaluation |
| :--- | :--- | :--- | :--- | :--- |
| **J2 (Shoulder)** | **$19.6\text{ N}\cdot\text{m}$** (with 1.5x margin) | NEMA 23 ($1.2\text{ Nm}$) with $20:1$ ($\eta=0.85$) | $1.2 \times 20 \times 0.85 = \mathbf{20.4\text{ N}\cdot\text{m}}$ | ⚠️ **Marginal**: Only a **~4% safety buffer**. Unacceptable if motor torque drops at $200\text{ RPM}$. Needs $30:1$, counterbalancing, or remote motor placement. |
| **J3 (Elbow)** | **$7.86\text{ N}\cdot\text{m}$** | NEMA 17 ($0.45\text{ Nm}$) with $15:1$ ($\eta=0.85$) | $0.45 \times 15 \times 0.85 = \mathbf{5.74\text{ N}\cdot\text{m}}$ | ❌ **FAILS**: Far below $7.86\text{ Nm}$. Even a $20:1$ gives $7.65\text{ N}\cdot\text{m}$ ($< 7.86\text{ Nm}$). Requires higher-torque NEMA 17, $25:1$ - $30:1$ ratio, or lighter distal mass. |
| **J4 (Wrist Pitch)** | **$1.20\text{ N}\cdot\text{m}$** | Slim NEMA 17 ($0.25\text{ Nm}$) with $5:1$ ($\eta=0.85$) | $0.25 \times 5 \times 0.85 = \mathbf{1.06\text{ N}\cdot\text{m}}$ | ❌ **Undersized**: Below $1.20\text{ N}\cdot\text{m}$ requirement. Needs $8:1$ to $10:1$ reduction. |
| **J1 (Base Swivel)** | Inertial load ($\approx 4\text{ Nm}$) | Timing belt listed as 20T/60T | $\frac{60}{20} = \mathbf{3:1\text{ ratio}}$ | ❌ **Ratio Error**: 20T to 60T provides only **$3:1$**, not $10:1$. Requires a 2-stage belt reduction (e.g. $3:1 \times 3.3:1 = 10:1$) or planetary unit. |

---

### C. Backlash vs Position Repeatability

* **The Backlash Trap:** A planetary gearbox rated at $< 15\text{ arcmin}$ ($0.25^\circ$) allows angular play.
* At a $550\text{ mm}$ lever arm, the linear endpoint displacement from J2 alone is:
  $$\Delta x = 550\text{ mm} \times \sin(0.25^\circ) \approx \mathbf{2.4\text{ mm}}$$
* For an endpoint repeatability of $\pm 1.0\text{ mm}$, the total allowable angular error budget across the entire kinematic chain is:
  $$\theta_{\text{budget}} = \arcsin\left(\frac{1.0\text{ mm}}{550\text{ mm}}\right) \approx 0.104^\circ \approx \mathbf{6.25\text{ arcmin}}$$
* This $< 6.25\text{ arcmin}$ budget must absorb gearbox backlash, bearing radial play, belt compliance, and printed PETG structural deflection. Therefore, $\pm 1.0\text{ mm}$ must remain an aspirational stretch target for V1.

---

## 🏗️ 2. Strategies to Mitigate Actuator Loads

Rather than simply upsizing all motors to heavier NEMA 23s (which adds self-weight in a vicious cycle), we will evaluate two mechanical design strategies during CAD modeling:

1. **Remote Motor Placement (Distal Mass Reduction):**
   * Keep wrist actuators mounted closer to the elbow or base, transferring rotation via closed-loop GT2 belts or concentric drive shafts.
   * Removing $500\text{ g}$ from the wrist tip reduces required shoulder torque by $\approx 2.7\text{ N}\cdot\text{m}$.
2. **Mechanical Counterbalancing:**
   * Adding a gas strut, extension spring, or counterweight to Joint 2 cancels out the continuous static gravity load, leaving the motor to provide only dynamic acceleration torque.

---

## 🚦 Status
* **Preliminary Sizing Complete — Design Review Required.**
* Motor and gearbox models will not be finalized until rough CAD provides verified mass, center-of-gravity (COM), and inertia tensors.
