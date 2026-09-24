# Devotics Arm V1 — Engineering Requirements Specification

**Target Machine:** 6-DOF Benchtop Research & Engineering Manipulator + Parallel Gripper  
**Designation:** R&D Prototype / Benchtop Manipulator (Not an Industrial Robot)  
**Author:** Ishan  
**Stage:** Concept & Simulation Validation (Pre-Procurement)  

---

## 1. Product Classification & Primary Objective

> **Classification Note:** Devotics Arm V1 is a **benchtop research and engineering manipulator**, constructed using 3D-printed PETG housings, structural aluminum/carbon elements, stepper motors, and micro-ROS / ESP32 control. It is **not** an industrial-grade robot arm. Stating industrial capability before multi-thousand-hour endurance, absolute repeatability, rigidity, and safety certification overstates the machine.

**Primary Objective for V1:**  
**Reliably manipulate approximately $300\text{ g}$ (with $500\text{ g}$ maximum capability) through a designated benchtop workstation envelope using ROS 2 and MoveIt 2.**

---

## 2. Operational Parameters & Engineering Limits

| Parameter | Preliminary Target | Engineering Rationale & Constraints |
| :--- | :--- | :--- |
| **Mounting** | Rigid Workbench Plate | Clamped or bolted to an aluminum/steel table plate ($250 \times 250\text{ mm}$). |
| **Kinematic Reach** | **$\approx 550\text{ mm}$** ($0.55\text{ m}$) | Shoulder to wrist: $L_1(300\text{ mm}) + L_2(250\text{ mm})$. Fingertips reach $\approx 630\text{ mm}$ with gripper. |
| **Rated Payload** | **$300\text{ g}$ nominal** ($500\text{ g}$ max) | Sized for tabletop pick-and-place, small lab objects, sensors, and 3D prints. |
| **Joint Velocities** | $\omega \approx 60^\circ/\text{s}$ ($10\text{ RPM}$) | Safe operating speed. (Note: At $20:1$ to $30:1$ reduction, motor runs at $200 - 300\text{ RPM}$ where stepper torque drops significantly). |
| **Position Repeatability** | **$\pm 1.0\text{ mm}$ (Stretch Target)** | **Crucial constraint:** A $15\text{ arcmin}$ ($0.25^\circ$) gearbox backlash at $550\text{ mm}$ produces $\approx 2.4\text{ mm}$ endpoint play from J2 alone! For $\pm 1.0\text{ mm}$, total angular error budget across all joints, bearings, and structure must be $< 6.25\text{ arcmin}$. $\pm 1.0\text{ mm}$ is an aspirational goal, not a guaranteed spec. |
| **Total Arm Mass** | **$< 3.5\text{ kg}$ (Estimated Budget)** | Subject to revision once full CAD model with motor, gearbox, and bearing placements is completed. |
| **Duty Cycle** | Intermittent R&D Testing | ~30 minutes continuous run, ambient cooling. |
| **Power Supply** | **$24\text{V DC}$** | Higher bus voltage enables stepper drivers (TMC2209) to overcome winding inductance ($L \cdot di/dt$), maintaining coil current and torque at higher step frequencies. |
| **Control Pipeline** | PC (ROS 2 / MoveIt) ➔ USB Serial ➔ ESP32 | High-level trajectory planning on host PC; real-time step/dir generation on microcontroller. |

---

## 3. Engineering Stance on Procurement
* Hardware procurement is **NOT authorized** based on preliminary analytical approximations.
* Actuator and gearbox selections must be validated against motor torque-speed curves and true CAD mass distributions before purchasing components.