# Devotics Robotic Arm V1 — Engineering Build Log (Days 31 to 35)

**Packages:** `devotics_arm_description`, `devotics_arm_moveit_config`  
**Topic:** Phase 5 — Mechanical Engineering, Torque Physics, Transmission Design & BOM  
**Milestone:** Stage Gate 2 — Hardware Procurement Decision  

---

## 📌 Executive Summary
In Phase 5, we moved from simulation into **real-world physical engineering**. 

Rather than prematurely buying motors that would fail under gravity, we conducted a rigorous mechanical analysis:
1. **Requirements Specification ([`docs/arm_requirements.md`](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/arm_requirements.md))**: Set benchtop constraints ($550\text{ mm}$ reach, $300\text{g} - 500\text{g}$ payload, $24\text{V}$ power, ESP32 USB-serial brain).
2. **Kinematic Geometry & Intuition**: Mapped the arm to the human bicep ($30\text{ cm}$), forearm ($25\text{ cm}$), 3-axis wrist, and parallel gripper.
3. **Torque Sizing**: Discovered that holding the arm outstretched creates a **$\approx 20\text{ N}\cdot\text{m}$** torque at the shoulder (Joint 2), proving that direct-drive NEMA 17 steppers ($0.45\text{ N}\cdot\text{m}$) would fail by a factor of 44 without reduction.
4. **Transmission Design ([`docs/transmission_design.md`](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/transmission_design.md))**: Applied the "bicycle climbing gear" principle, selecting a **20:1 planetary gearbox** for the shoulder ($20.4\text{ N}\cdot\text{m}$ output), 15:1 for the elbow, and timing belts/direct drives for the wrist.
5. **Bill of Materials ([`docs/bom.md`](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/bom.md))**: Finalized parts selection (ESP32, TMC2209 silent drivers, NEMA 23/17/14 steppers, 24V 10A supply, bearings, fasteners) totaling **~$226 USD**.

---

## 🏆 Stage Gate 2: Hardware Engineering Sign-Off
All mechanical, electrical, and firmware requirements are mathematically validated. 
**Phase 5 is officially completed and signed off!**
