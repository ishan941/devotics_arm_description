# Devotics Robotic Arm V1 — Engineering Build Log (Day 10)

**Package:** `devotics_arm_description`  
**ROS 2 Distribution:** Jazzy / Ubuntu 24.04 (arm64)  
**Topic:** Stage Gate 1, Joint Limits, Named Poses, and Tool Center Point (TCP)  
**Target:** Finalizing the complete virtual model ready for MoveIt 2 integration  

---

## 📌 Goal & Overview
Day 10 completes **Stage Gate 1**: turning the geometric 6-DOF + parallel gripper model into an engineering-ready robotic manipulator with realistic physical constraints, standardized named poses, and a designated Tool Center Point (`tool0`).

---

## 🛠️ Implementation Steps

### 1. Mechanical Joint Limits Parameterization
In [`urdf/devotics_arm.urdf.xacro`](file:///home/ishan/ros2_ws/src/devotics_arm_description/urdf/devotics_arm.urdf.xacro), physical limits were defined as Xacro properties:

```xml
<!-- REVOLUTE JOINT LIMITS (radians) -->
<xacro:property name="j1_lower" value="-3.14159"/>  <!-- Base rotation: 360° range -->
<xacro:property name="j1_upper" value="3.14159"/>
<xacro:property name="j2_lower" value="-1.5708"/>   <!-- Shoulder pitch: ±90° -->
<xacro:property name="j2_upper" value="1.5708"/>
<xacro:property name="j3_lower" value="-2.0944"/>   <!-- Elbow pitch: ±120° -->
<xacro:property name="j3_upper" value="2.0944"/>
<xacro:property name="j4_lower" value="-1.5708"/>   <!-- Wrist pitch: ±90° -->
<xacro:property name="j4_upper" value="1.5708"/>
<xacro:property name="j5_lower" value="-3.14159"/>  <!-- Wrist roll: 360° continuous -->
<xacro:property name="j5_upper" value="3.14159"/>
<xacro:property name="j6_lower" value="-3.14159"/>  <!-- Wrist yaw: 360° tool rotation -->
<xacro:property name="j6_upper" value="3.14159"/>

<!-- GRIPPER PRISMATIC LIMITS (meters) -->
<xacro:property name="finger_lower" value="0.0"/>
<xacro:property name="finger_upper" value="0.03"/>  <!-- 30 mm per finger = 60 mm total stroke -->
```

### 2. Adding the Virtual Tool Center Point (`tool0`)
Industrial motion planning (MoveIt, KUKA, ABB) does not calculate IK to the last metal joint (`wrist3_link`); it plans for the **Tool Center Point (TCP)** where grasping actually occurs.

We added the virtual `tool0` frame at the fingertip contact center:
```xml
<!-- Virtual TCP Frame for Kinematics & MoveIt -->
<link name="tool0"/>

<joint name="tool0_joint" type="fixed">
    <parent link="gripper_base_link"/>
    <child link="tool0"/>
    <origin xyz="0 0 0.08" rpy="0 0 0"/>
</joint>
```

### 3. Named Joint Configurations ([`config/joint_poses.yaml`](file:///home/ishan/ros2_ws/src/devotics_arm_description/config/joint_poses.yaml))
We defined standard operating configurations:
```yaml
home:
  joint1: 0.0
  joint2: 0.0
  joint3: 0.0
  joint4: 0.0
  joint5: 0.0
  joint6: 0.0

ready:
  joint1: 0.0
  joint2: -0.5
  joint3: 0.8
  joint4: 0.0
  joint5: 0.0
  joint6: 0.0

pickup_approach:
  joint1: 0.0
  joint2: -1.0
  joint3: 1.4
  joint4: -0.4
  joint5: 0.0
  joint6: 0.0
```

---

## ⚠️ Obstacles, Mistakes & How They Were Solved

### Obstacle 1: Where Should the End-Effector Frame Be?
* **The Trap:** Initially, the kinematic chain ended at `wrist3_link` or `gripper_base_link`.
* **The Problem:** If you ask an inverse kinematics solver to position `wrist3_link` at an object $(X, Y, Z)$, the actual gripper fingers will collide with the table or object because the fingertips extend ~10 cm past `wrist3_link`.
* **How We Tackled It:** Created link `tool0` as a fixed child of `gripper_base_link` with an origin offset corresponding exactly to the tip of the fingers ($z = 0.08\text{ m}$). MoveIt 2 now uses `tool0` as the IK tip frame.

### Obstacle 2: Gripper Symmetry Mismatch
* **The Trap:** When making the prismatic fingers move, setting both finger joints with `<axis xyz="0 1 0"/>` resulted in both fingers moving to the left together instead of pinching symmetrically.
* **How We Tackled It:** Inverted the right finger's prismatic axis to `<axis xyz="0 -1 0"/>`. When both joint positions increase from $0.0$ to $0.03\text{ m}$, the left finger moves in $+Y$ and the right in $-Y$, opening symmetrically.

---

## ✅ Stage Gate 1 Verification Test
To verify the complete kinematic structure:
```bash
cd ~/ros2_ws
colcon build --packages-select devotics_arm_description
source install/setup.bash
ros2 run xacro xacro src/devotics_arm_description/urdf/devotics_arm.urdf.xacro | grep "<joint name="
```
Expected output: Exactly 10 joints:
1. `joint1` (revolute)
2. `joint2` (revolute)
3. `joint3` (revolute)
4. `joint4` (revolute)
5. `joint5` (revolute)
6. `joint6` (revolute)
7. `gripper_base_joint` (fixed)
8. `left_finger_joint` (prismatic)
9. `right_finger_joint` (prismatic)
10. `tool0_joint` (fixed)
