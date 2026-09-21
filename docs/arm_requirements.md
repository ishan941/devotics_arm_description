# Devotics Arm V1 — Engineering Requirements Specification

**Target Machine:** 6-DOF Benchtop Articulated Manipulator + Parallel Gripper  
**Author:** Ishan  
**Stage:** Concept Phase / Pre-Procurement  

---

## 1. Operational Parameters

| Parameter | Specification | Engineering Rationale |
| :--- | :--- | :--- |
| **Mounting Style** | Rigid Desktop Base Plate | Screwed or clamped to a workbench ($200 \times 200\text{ mm}$ aluminum/steel plate). |
| **Max Horizontal Reach** | **$550\text{ mm}$** ($0.55\text{ m}$) | Shoulder to wrist: $L_1(300\text{ mm}) + L_2(250\text{ mm})$. Fingertips reach ~630 mm with gripper. |
| **Rated Payload** | **$300\text{ g}$ nominal** ($500\text{ g}$ max) | Standard small parts, cans, 3D prints, tools, and pick-and-place items. |
| **End-Effector Speed** | **$100\text{ mm/s}$ to $250\text{ mm/s}$** | Safe desktop speed; fast enough for responsive automation without high kinetic hazard. |
| **Joint Velocities** | $\omega_{\max} = 60^\circ/\text{s}$ (J1–J3), $90^\circ/\text{s}$ (J4–J6) | Matches our `joint_limits.yaml` ($1.0\text{ to } 1.5\text{ rad/s}$). |
| **Position Repeatability** | **$\pm 1.0\text{ mm}$** | Achievable with closed-loop magnetic encoders or precision microstepping belts. |
| **Total Arm Mass (Target)** | **$< 3.5\text{ kg}$** (excluding base plate) | Lightweight aluminum tubes / PETG 3D printed housings keep motor torque manageable. |
| **Duty Cycle** | Intermittent Desktop Prototyping | ~30 minutes continuous run, passive ambient cooling. |
| **Power Supply** | **$24\text{V DC}$ (10A – 15A)** | Higher voltage ($24\text{V}$) reduces motor current ($I = P/V$), minimizing heating in stepper coils. |
| **Controller Architecture** | **PC (ROS 2 / MoveIt) ➔ USB Serial ➔ ESP32** | PC plans trajectories; ESP32 generates synchronized step/dir pulses and reads limit switches. |





 ## Worst-Case Torque Calculations ($\tau = F \times r$)
1. Shoulder Pitch (Joint 2) — The Heavyweight Joint
The shoulder must lift everything (Upper arm + Forearm + Wrist + Gripper + Payload):

$$\tau_{\text{upper_arm}} = 8.83\text{ N} \times 0.15\text{ m} = 1.32\text{ N}\cdot\text{m}$$ $$\tau_{\text{forearm}} = 6.87\text{ N} \times 0.425\text{ m} = 2.92\text{ N}\cdot\text{m}$$ $$\tau_{\text{wrist}} = 6.87\text{ N} \times 0.55\text{ m} = 3.78\text{ N}\cdot\text{m}$$ $$\tau_{\text{gripper}} = 2.94\text{ N} \times 0.62\text{ m} = 1.82\text{ N}\cdot\text{m}$$ $$\tau_{\text{payload}} = 4.91\text{ N} \times 0.65\text{ m} = 3.19\text{ N}\cdot\text{m}$$

$$\tau_{\text{static, total}} = 1.32 + 2.92 + 3.78 + 1.82 + 3.19 = \mathbf{13.05\text{ N}\cdot\text{m}}$$

Adding a Safety Factor $S = 1.5$ (for dynamic angular acceleration $\alpha = 2.0\text{ rad/s}^2$ and friction losses): $$\tau_{\text{required, shoulder}} = 13.05\text{ N}\cdot\text{m} \times 1.5 \approx \mathbf{19.6\text{ N}\cdot\text{m}}$$

2. Elbow Pitch (Joint 3)
The elbow only lifts what is downstream (Forearm + Wrist + Gripper + Payload):

Forearm: $6.87\text{ N} \times 0.125\text{ m} = 0.86\text{ N}\cdot\text{m}$
Wrist: $6.87\text{ N} \times 0.25\text{ m} = 1.72\text{ N}\cdot\text{m}$
Gripper: $2.94\text{ N} \times 0.32\text{ m} = 0.94\text{ N}\cdot\text{m}$
Payload: $4.91\text{ N} \times 0.35\text{ m} = 1.72\text{ N}\cdot\text{m}$
$$\tau_{\text{static, elbow}} = 0.86 + 1.72 + 0.94 + 1.72 = 5.24\text{ N}\cdot\text{m}$$ With Safety Factor $S = 1.5$: $$\tau_{\text{required, elbow}} = 5.24 \times 1.5 \approx \mathbf{7.86\text{ N}\cdot\text{m}}$$

3. Wrist Pitch (Joint 4)
The wrist only lifts the Gripper + Payload ($r \approx 0.10\text{ m}$): $$\tau_{\text{static, wrist}} = (2.94 + 4.91)\text{ N} \times 0.10\text{ m} \approx 0.79\text{ N}\cdot\text{m}$$ With Safety Factor $S = 1.5$: $$\tau_{\text{required, wrist}} \approx \mathbf{1.2\text{ N}\cdot\text{m}}$$

💡 The Big Engineering Revelation: Why We Need Gearboxes!
Look at the motor requirements:

Shoulder (J2): Needs $\sim 20\text{ N}\cdot\text{m}$!
A bare NEMA 17 stepper motor directly on the shaft only provides $0.45\text{ N}\cdot\text{m}$!
If you mount a NEMA 17 directly to the shoulder, it is under-powered by 44 times! It will not even be able to lift its own arm, let alone a payload!
👉 The Solution is Mechanical Transmission (Day 34): If we use a NEMA 23 stepper ($1.2\text{ N}\cdot\text{m}$) with a 20:1 planetary gearbox (or 30:1 cycloidal drive): $$\text{Output Torque} = 1.2\text{ N}\cdot\text{m} \times 20 \times 0.85\text{ (efficiency)} = \mathbf{20.4\text{ N}\cdot\text{m}} \quad \text{✅ FITS PERFECTLY!}$$