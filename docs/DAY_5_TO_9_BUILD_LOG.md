# Devotics Robotic Arm V1 — Engineering Build Log (Days 5 to 9)

**Package:** `devotics_arm_description`  
**ROS 2 Distribution:** Jazzy / Ubuntu 24.04  
**Author:** Ishan  
**Architecture:** 6-DOF Revolute Articulated Arm + 2-Finger Prismatic Gripper (Xacro-driven)

---

## 📌 Executive Summary

Between Day 5 and Day 9, the virtual robot evolved from a basic 3-DOF prototype into a fully articulated, parameterized, 6-DOF industrial-style manipulator with an active end-effector.

```
                   Devotics Arm V1 Kinematic Hierarchy
                   
                             base_link
                                 │
                            [joint1: Z-rev]
                                 │
                            shoulder_link
                                 │
                            [joint2: Y-rev]
                                 │
                           upper_arm_link
                                 │
                            [joint3: Y-rev]
                                 │
                            forearm_link
                                 │
                            [joint4: Y-rev]  (Wrist Pitch)
                                 │
                             wrist1_link
                                 │
                            [joint5: Z-rev]  (Wrist Roll)
                                 │
                             wrist2_link
                                 │
                            [joint6: Y-rev]  (Wrist Yaw / Tool Flange)
                                 │
                             wrist3_link
                                 │
                        [gripper_base_joint: Fixed]
                                 │
                         gripper_base_link
                         ┌───────┴───────┐
             [left_finger_joint: Prism]   [right_finger_joint: Prism]
                         │                                │
                  left_finger_link                 right_finger_link
```

---

## 📅 Day-by-Day Build Log

### 🔹 Day 5: TF Tree & Spatial Coordinates Inspection
* **Goal:** Understand and inspect how ROS 2 computes and broadcasts spatial transforms between links across the robot tree.
* **Key Components Verified:**
  * `robot_state_publisher`: Subscribes to `/joint_states` and uses the URDF kinematic tree to broadcast transforms over `/tf` and `/tf_static`.
  * `joint_state_publisher_gui`: Emits interactive joint angles at ~10 Hz.
* **Key Tools & Commands:**
  ```bash
  ros2 topic echo /tf
  ros2 run tf2_tools view_frames
  ros2 run tf2_ros tf2_echo base_link forearm_link
  ```
* **Milestone Achieved:**
  * Captured `frames_<timestamp>.pdf` and dot graph confirming clean transform flow: `base_link -> shoulder_link -> upper_arm_link -> forearm_link`.
  * Verified forward kinematics live in real-time as sliders shifted XYZ translations.

---

### 🔹 Day 6: Wrist Articulation (J4 & J5 — 5-DOF)
* **Goal:** Add wrist pitch and wrist roll to give the arm pointing orientation capability.
* **URDF Additions:**
  * **Link `wrist1_link`**: Cylinder ($r = 0.04\text{ m}, h = 0.10\text{ m}$)
  * **Joint `joint4` (Wrist Pitch)**:
    * Parent: `forearm_link`, Child: `wrist1_link`
    * Origin: `xyz="0 0 0.25"`
    * Axis: `xyz="0 1 0"` (Pitch)
    * Limits: $[-1.57, +1.57]\text{ rad}$ ($\pm 90^\circ$)
  * **Link `wrist2_link`**: Cylinder ($r = 0.035\text{ m}, h = 0.10\text{ m}$)
  * **Joint `joint5` (Wrist Roll)**:
    * Parent: `wrist1_link`, Child: `wrist2_link`
    * Origin: `xyz="0 0 0.10"`
    * Axis: `xyz="0 0 1"` (Roll along link axis)
    * Limits: $[-3.14, +3.14]\text{ rad}$ ($\pm 180^\circ$)
* **Milestone Achieved:**
  * 5 active joint sliders in GUI.
  * Arm now poses the wrist in arbitrary pitch and roll angles.

---

### 🔹 Day 7: Spherical Wrist Completion (J6 — 6-DOF Industrial Standard)
* **Goal:** Add the 6th degree of freedom to achieve a full 6-DOF serial manipulator capable of independent 3D position $(x,y,z)$ and 3D orientation $(\text{roll}, \text{pitch}, \text{yaw})$.
* **URDF Additions:**
  * **Link `wrist3_link` (Tool Flange)**: Cylinder ($r = 0.03\text{ m}, h = 0.06\text{ m}$)
  * **Joint `joint6` (Wrist Yaw / Tool Rotation)**:
    * Parent: `wrist2_link`, Child: `wrist3_link`
    * Origin: `xyz="0 0 0.10"`
    * Axis: `xyz="0 1 0"`
    * Limits: $[-3.14, +3.14]\text{ rad}$
* **Key Theory Internalized:**
  * **Joints 1–3**: Primary contributors to End-Effector **position** in workspace.
  * **Joints 4–6**: Form a 3-axis wrist controlling End-Effector **orientation**.
* **Milestone Achieved:**
  * 6-DOF kinematics tree matches industrial standards (UR5, ABB, KUKA).
  * TF echo verified from `base_link` all the way to `wrist3_link`.

---

### 🔹 Day 8: Parallel End-Effector Gripper (Prismatic Actuation)
* **Goal:** Attach a parallel jaw gripper with linear sliding fingers.
* **URDF Additions:**
  * **Link `gripper_base_link`**: Mount plate attached to `wrist3_link` via a **fixed joint** (`gripper_base_joint`).
  * **Link `left_finger_link` & `right_finger_link`**: Rectangular jaws ($0.02 \times 0.02 \times 0.06\text{ m}$).
  * **Joints `left_finger_joint` & `right_finger_joint` (`type="prismatic"`)**:
    * Sliding axis: Left uses `<axis xyz="0 1 0"/>`, Right uses `<axis xyz="0 -1 0"/>`.
    * Limits: `lower="0.0"` to `upper="0.03"` (total grip stroke $60\text{ mm}$).
* **Milestone Achieved:**
  * 8 sliders visible in RViz (6 revolute joints + 2 prismatic gripper fingers).
  * Tested symmetric open/close gripping motions in RViz.

---

### 🔹 Day 9: Parameterization & Migration to Xacro
* **Goal:** Eliminate hardcoded magic numbers and replace raw XML with clean, modular, scalable Xacro.
* **Created:** [`urdf/devotics_arm.urdf.xacro`](file:///home/ishan/ros2_ws/src/devotics_arm_description/urdf/devotics_arm.urdf.xacro)
* **Architectural Improvements:**
  1. **Global Properties**:
     * Dimensions, radius, link lengths, strokes, and joint angle limits are declared once at the top of the file:
     ```xml
     <xacro:property name="upper_arm_length" value="0.30"/>
     <xacro:property name="forearm_length"   value="0.25"/>
     <xacro:property name="finger_stroke"    value="0.03"/>
     ```
  2. **Parametric Positioning & Math**:
     * Attachment origins and link center-of-visual offsets are dynamically evaluated via expressions like `${upper_arm_length / 2}` and origin `${forearm_length}`.
     * Changing a link length automatically shifts all subsequent joint origins cleanly without manual re-calculation.
  3. **Launch File Modernization ([`display.launch.py`](file:///home/ishan/ros2_ws/src/devotics_arm_description/launch/display.launch.py))**:
     * Migrated from reading static `.urdf` text to dynamic runtime processing:
     ```python
     import xacro
     robot_description_doc = xacro.process_file(xacro_path)
     robot_description = robot_description_doc.toxml()
     ```
* **Milestone Achieved:**
  * Verified via `ros2 run xacro xacro urdf/devotics_arm.urdf.xacro`.
  * Clean build and verification in RViz with full 8-joint articulation.

---

## 📊 Comparison Matrix (Day 5 vs Day 9)

| Feature | Day 5 Baseline | Day 9 Final |
| :--- | :--- | :--- |
| **Active Revolute Joints** | 3 (Base, Shoulder, Elbow) | 6 (Full Industrial Chain) |
| **Prismatic Joints** | 0 | 2 (Parallel Gripper) |
| **Total Controlled DOFs** | 3 | 8 |
| **Description Format** | Static Raw URDF | Dynamic Modular Xacro |
| **End Effector** | None (bare forearm link) | Parallel Gripper with tool mounting |
| **Orientation Reach** | Restricted | Full 3D SO(3) spherical wrist |
| **Launch Pipeline** | Static string read | In-memory `xacro.process_file()` |

---

## 🎯 Next Step: Day 10
* Define realistic mechanical joint limits and velocity constraints.
* Create named robot poses YAML configuration (`home`, `ready`, `pickup_approach`).
* Complete **Stage Gate 1** (Full virtual robot signed off and ready for MoveIt 2 integration).
