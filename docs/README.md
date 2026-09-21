# Devotics Robotic Arm V1 — Engineering Build Logs & Documentation

**Package:** `devotics_arm_description` / `devotics_arm_moveit_config`  
**ROS 2 Distribution:** Jazzy / Ubuntu 24.04 (arm64)  
**Author:** Ishan  
**Methodology:** Agentic Robotics Engineering (AI Pair-Programming)  

---

## 📚 Master Index of Engineering Logs

| Chapter / Log File | Focus Areas | Key Milestones & Solved Obstacles |
| :--- | :--- | :--- |
| 📘 [**Days 5–9 Build Log**](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/DAY_5_TO_9_BUILD_LOG.md) | TF Tree, 6-DOF Wrist, Parallel Gripper, Xacro Migration | Built the 8-joint kinematic tree, resolved symmetric gripper actuation, eliminated XML magic numbers with Xacro properties. |
| 📘 [**Day 10: Stage Gate 1 & TCP**](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/DAY_10_STAGE_GATE_1_AND_TCP.md) | Mechanical Joint Limits, Named Poses (`joint_poses.yaml`), Virtual `tool0` TCP Link | Prevented MoveIt IK errors by creating a dedicated Tool Center Point at the fingertips instead of the wrist flange. |
| 📘 [**Day 11: Collision Modeling**](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/DAY_11_COLLISION_MODELING.md) | `<collision>` vs `<visual>`, Planning Scene, Self-Collision Matrix | Solved the "Ghost Link" phenomenon where MoveIt ignored links lacking collision geometries; configured SRDF adjacent link exemptions. |
| 📘 [**Day 12: Inverse Kinematics Intuition**](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/DAY_12_INVERSE_KINEMATICS.md) | Forward vs Inverse Kinematics, 2-Link Planar IK (`ik_demo.py`), Law of Cosines | Handled math domain crashes (`math.acos`) for out-of-reach coordinates and understood elbow-up vs elbow-down branch selection. |
| 📘 [**Day 13: MoveIt 2 Setup Assistant**](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/DAY_13_MOVEIT2_PACKAGE_SETUP.md) | MoveIt Package Generation, SRDF, Planning Groups (`devotics_arm`, `hand`) | Installed missing ROS 2 Jazzy controller packages; correctly chained KDL solver from `base_link` to `tool0`. |
| 📘 [**Day 14: ros2_control & Mock Hardware**](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/DAY_14_ROS2_CONTROL_AND_MOCK_HARDWARE.md) | `mock_components/GenericSystem`, `ros2_controllers.yaml`, `moveit_controllers.yaml` | Aligned action namespaces (`follow_joint_trajectory`) between controller manager and MoveIt Simple Controller Manager. |
| 📘 [**Day 15: Trajectory Execution & TOTG**](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/DAY_15_TRAJECTORY_EXECUTION_AND_TOTG_DEBUGGING.md) | **The "Plan Works, Execute Fails" Mystery**, Time-Optimal Parameterization (TOTG), `joint_limits.yaml` | **Major Milestone:** Diagnosed zero acceleration limits causing identical 0.0s timestamps; rebuilt with `--symlink-install`; achieved autonomous execution! |
| 📘 [**Day 16: Graphify Knowledge Graph**](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/DAY_16_GRAPHIFY_KNOWLEDGE_GRAPH.md) | Codebase AST Knowledge Graph, Standalone `uv`, `graphifyy` CLI, Interactive HTML | Bypassed sudo/pip restrictions with `uv`; mapped code into AST graph (`graph.html`); registered native Antigravity skill. |
| 📘 [**Days 21–25: ros2_control & Autonomous Execution**](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/DAY_21_TO_25_ROS2_CONTROL_AND_AUTONOMOUS_EXECUTION.md) | Multi-Controller Management, `gripper_controller`, ROS 2 Action Clients, Autonomous State Machine | Added parallel gripper hardware interfaces; installed `ros2controlcli`; verified `[claimed]` channels; executed autonomous Python pick-and-place script. |
| 📘 [**Days 26–30: Gazebo Physics Simulation**](file:///home/ishan/ros2_ws/src/devotics_arm_description/docs/DAY_26_TO_30_GAZEBO_PHYSICS_SIMULATION.md) | Gazebo Harmonic, Parametric Inertia Tensors, Dual-Mode Hardware Interface, SDF Workstation Scene | Modeled rigid-body dynamics (`<inertial>`); resolved the toppling base with `world` anchor; integrated `gz_ros2_control`; created work table and target cube world. |

---

## 🚀 How to Run the Complete System Today

```bash
# 1. Source workspace
cd ~/ros2_ws
source install/setup.bash

# 2. Launch MoveIt 2 Motion Planning with RViz
ros2 launch devotics_arm_moveit_config demo.launch.py
```

### In RViz:
1. Select Planning Group: `devotics_arm`
2. Select Goal State: `ready` (or drag the interactive marker)
3. Click **Plan** (calculates time-parameterized trajectory)
4. Click **Execute** (simulated arm moves smoothly to target pose)

### To Explore the Codebase Knowledge Graph:
```bash
xdg-open ~/ros2_ws/src/devotics_arm_description/graphify-out/graph.html
```
