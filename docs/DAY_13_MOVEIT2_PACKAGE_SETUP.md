# Devotics Robotic Arm V1 — Engineering Build Log (Day 13)

**Package:** `devotics_arm_moveit_config`  
**ROS 2 Distribution:** Jazzy / Ubuntu 24.04 (arm64)  
**Topic:** MoveIt 2 Setup Assistant & Configuration Package Generation  
**Target:** Generating the SRDF, Planning Groups, and MoveIt Launch Pipeline  

---

## 📌 Goal & Overview
MoveIt 2 needs more than just a URDF to plan motion. It requires a specialized configuration package containing:
1. **SRDF (`devotics_arm.srdf`)**: Semantic Robot Description Format defining planning groups, end-effectors, and disabled self-collisions.
2. **Kinematics Config (`kinematics.yaml`)**: Solver parameters (KDL kinematic plugin, search resolution, timeout).
3. **OMPL Planning Config (`ompl_planning.yaml`)**: Algorithms (RRTConnect, RRT*, PRM) and request/response adapters.
4. **Trajectory Execution Config (`moveit_controllers.yaml`)**: Links MoveIt to hardware controller actions.

---

## 🛠️ Setup Assistant Workflow

To generate the configuration package, we launched the MoveIt Setup Assistant:
```bash
ros2 launch moveit_setup_assistant setup_assistant.launch.py
```

### 1. Load Robot Description
Selected the Xacro file:
`/home/ishan/ros2_ws/src/devotics_arm_description/urdf/devotics_arm.urdf.xacro`

### 2. Self-Collision Matrix
Ran the automatic self-collision sampling generator (10,000 random samples). This generated `<disable_collisions>` tags in the SRDF for adjacent and non-colliding links.

### 3. Planning Groups Defined
* **Group 1: `devotics_arm`**
  * Kinematic Solver: `kdl_kinematics_plugin/KDLKinematicsPlugin`
  * Kinematic Chain:
    * Base Link: `base_link`
    * Tip Link: `tool0` (or `wrist3_link`)
  * Joints: `joint1`, `joint2`, `joint3`, `joint4`, `joint5`, `joint6`
* **Group 2: `hand`**
  * Joints: `left_finger_joint`, `right_finger_joint`

### 4. End-Effector Attachment
* Name: `hand`
* End-Effector Group: `hand`
* Parent Link: `wrist3_link`
* Parent Group: `devotics_arm`

### 5. Package Generation
Saved configuration to:
`/home/ishan/ros2_ws/src/devotics_arm_moveit_config`

---

## ⚠️ Obstacles, Mistakes & How They Were Solved

### Obstacle 1: Missing ROS 2 Jazzy Controller Packages
* **The Error:** Launching `demo.launch.py` immediately crashed with:
  ```text
  package 'controller_manager' not found
  package 'ros2_controllers' not found
  ```
* **Why it happened:** ROS 2 Jazzy on Ubuntu 24.04 does not install `ros2_control` and `controller_manager` by default with desktop install.
* **How We Solved It:**
  ```bash
  sudo apt-get update
  sudo apt-get install -y \
      ros-jazzy-controller-manager \
      ros-jazzy-ros2-controllers \
      ros-jazzy-joint-trajectory-controller \
      ros-jazzy-joint-state-broadcaster
  ```

### Obstacle 2: Setup Assistant Kinematic Chain Tip Selection
* **The Trap:** When creating the `devotics_arm` group chain, selecting `gripper_base_link` as the tip link caused the Kinematics solver to compute IK to the wrist mount rather than the fingertip TCP.
* **How We Tackled It:** Made sure the chain tip link was set to `tool0`. If `tool0` is fixed to the gripper base, KDL computes the full transformation matrix from `base_link` through all 6 joints to `tool0`.

---

## ✅ Verification Test
Build and verify package registration:
```bash
cd ~/ros2_ws
colcon build --packages-select devotics_arm_moveit_config
source install/setup.bash
ros2 pkg prefix devotics_arm_moveit_config
```
Expected output: `/home/ishan/ros2_ws/install/devotics_arm_moveit_config`
