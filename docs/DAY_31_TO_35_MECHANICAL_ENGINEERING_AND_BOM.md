# Devotics Robotic Arm V1 — Engineering Build Log (Days 31 to 35)

**Packages:** `devotics_arm_description`, `devotics_arm_moveit_config`  
**Topic:** Phase 5 — Mechanical Engineering, Preliminary Torque Analysis, Transmission Review & BOM  
**Milestone:** Stage Gate 2 — Preliminary Sizing Complete (Procurement Not Authorized)  

---

## 📌 Executive Summary
In Phase 5, the project transitioned from virtual kinematics into **physical engineering scrutiny**. 

Rather than prematurely purchasing motors and gearboxes based on static holding torque approximations, a rigorous mechanical peer-review established the following critical facts:

1. **Classification Locked**: Devotics Arm V1 is designated as a **Benchtop Research/Engineering Manipulator** ($300\text{ g}$ nominal payload, $550\text{ mm}$ reach), not an industrial robot.
2. **Torque Reality Check**:
   * Holding torque $\neq$ Running torque. Stepper torque falls sharply at $200 - 300\text{ RPM}$ (the speed corresponding to $60^\circ/\text{s}$ joint motion at $20:1 - 30:1$ reduction).
   * Preliminary ratios for J2 (4% margin), J3 ($5.74\text{ Nm}$ vs $7.86\text{ Nm}$ required), and J4 ($1.06\text{ Nm}$ vs $1.20\text{ Nm}$ required) were audited and identified as undersized.
3. **Backlash & Repeatability Limits**:
   * A $15\text{ arcmin}$ ($0.25^\circ$) gearbox backlash yields $\approx 2.4\text{ mm}$ of play at $550\text{ mm}$ reach from J2 alone. $\pm 1.0\text{ mm}$ repeatability is classified as an aspirational stretch goal, not a guaranteed specification.
4. **Mass Budget Reconciliation**:
   * Component masses must be extracted from physical CAD rather than rough estimates to prevent self-weight circularity.
5. **Procurement Gate Locked**:
   * Hardware purchasing is explicitly held until the 4-stage validation sequence (Simulation Validation ➔ Rough CAD ➔ Actuator Placement & Counterbalancing ➔ Component Torque-Speed Matching) is satisfied.

---

## 🚦 Stage Gate 2 Status:
**PRELIMINARY ACTUATOR SIZING COMPLETE — PROCUREMENT NOT AUTHORIZED**  
Immediate priority: **Stage A** — Validate the 6-DOF mechanism and $300\text{ mm} + 250\text{ mm}$ link geometry across the tabletop workspace in MoveIt and Gazebo.
