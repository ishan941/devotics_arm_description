# Devotics Robotic Arm V1 — Engineering Build Log (Day 11)

**Package:** `devotics_arm_description`  
**ROS 2 Distribution:** Jazzy / Ubuntu 24.04 (arm64)  
**Topic:** Collision Geometries, Planning Scene Safety, and Self-Collision Matrix  
**Target:** Equipping all links with collision models required for MoveIt 2  

---

## 📌 Goal & Overview
In standard RViz visualization, a robot only needs `<visual>` tags to look correct on screen. However, **MoveIt 2 motion planners (OMPL) completely ignore `<visual>` tags**! MoveIt relies 100% on `<collision>` tags to construct the collision world and check for self-collisions and environmental collisions.

On Day 11, we added complete `<collision>` definitions for every link in the robot.

---

## 🛠️ Implementation Steps

### 1. Adding `<collision>` to Every Link
For every link in [`urdf/devotics_arm.urdf.xacro`](file:///home/ishan/ros2_ws/src/devotics_arm_description/urdf/devotics_arm.urdf.xacro), we created an exact collision geometry mirroring the visual dimensions:

```xml
<!-- Example: Upper Arm Link with Collision Geometry -->
<link name="upper_arm_link">
    <visual>
        <origin xyz="0 0 ${upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
            <cylinder radius="${upper_arm_radius}" length="${upper_arm_length}"/>
        </geometry>
        <material name="upper_arm_mat">
            <color rgba="0.10 0.45 0.85 1"/>
        </material>
    </visual>
    <collision>
        <origin xyz="0 0 ${upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
            <cylinder radius="${upper_arm_radius}" length="${upper_arm_length}"/>
        </geometry>
    </collision>
</link>
```

Links covered:
1. `base_link` (Cylinder: $r = 0.10\text{ m}, l = 0.10\text{ m}$)
2. `shoulder_link` (Box: $0.12 \times 0.12 \times 0.10\text{ m}$)
3. `upper_arm_link` (Cylinder: $r = 0.05\text{ m}, l = 0.30\text{ m}$)
4. `forearm_link` (Cylinder: $r = 0.045\text{ m}, l = 0.25\text{ m}$)
5. `wrist1_link` (Cylinder: $r = 0.04\text{ m}, l = 0.10\text{ m}$)
6. `wrist2_link` (Cylinder: $r = 0.035\text{ m}, l = 0.10\text{ m}$)
7. `wrist3_link` (Cylinder: $r = 0.03\text{ m}, l = 0.06\text{ m}$)
8. `gripper_base_link` (Box: $0.08 \times 0.04 \times 0.04\text{ m}$)
9. `left_finger_link` & `right_finger_link` (Boxes: $0.02 \times 0.02 \times 0.06\text{ m}$)

---

## ⚠️ Obstacles, Mistakes & How They Were Solved

### Obstacle 1: The "Ghost Link" Phenomenon in MoveIt
* **The Mistake:** Earlier in development, we tested planning with only `<visual>` tags in the URDF.
* **The Error:** In RViz MoveIt, moving the arm worked visually, but planning paths caused links to clip through each other and through obstacles without raising any warnings or errors. MoveIt treated the links as empty space.
* **Why it happened:** The Collision Detection Engine (FCL - Flexible Collision Library) queries collision bodies. If a link has no `<collision>` element, FCL considers that link non-existent for physics and collision checking.
* **How We Solved It:** Systematically matched every `<visual>` tag with an identical `<collision>` tag in the Xacro file.

### Obstacle 2: Adjacent Links Flagged as Self-Colliding
* **The Trap:** When two connected links touch at a joint (e.g. `wrist3_link` and `gripper_base_link`), their collision cylinders physically touch or overlap by 1 mm at the joint origin. MoveIt's default collision checker flags this as an immediate self-collision and rejects all start states.
* **How We Solved It:** In the SRDF (`devotics_arm.srdf`), we disabled collision checking between adjacent parent-child links:
  ```xml
  <disable_collisions link1="wrist3_link" link2="gripper_base_link" reason="Adjacent"/>
  ```
  Adjacent links that can never physically collide or whose joint motion does not cause destructive interference must be explicitly disabled in the SRDF.

---

## ✅ Verification Test
Verify collision geometry parsing:
```bash
ros2 run xacro xacro src/devotics_arm_description/urdf/devotics_arm.urdf.xacro | grep "<collision>" | wc -l
```
Expected output: Exactly `9` (or `10` with base mount) collision bodies.
