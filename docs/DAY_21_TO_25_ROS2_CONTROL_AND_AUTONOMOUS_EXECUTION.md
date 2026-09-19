# Devotics Robotic Arm V1 — Engineering Build Log (Days 21 to 25)

**Packages:** `devotics_arm_description`, `devotics_arm_moveit_config`  
**ROS 2 Distribution:** Jazzy / Ubuntu 24.04 (arm64)  
**Branch:** `P-3` (merged to `main`, active in `P-4`)  
**Topic:** Phase 3 — Multi-Controller `ros2_control` Pipeline & Autonomous Python Mission Control  
**Target:** Direct Hardware Control, Gripper Actuation, and Autonomous Pick & Place Execution  

---

## 📌 Executive Summary
Between Day 21 and Day 25, the Devotics Arm transitioned from an interactive RViz demo into an **autonomous industrial manipulator**. 

We:
1. Integrated both parallel gripper fingers into the `<ros2_control>` hardware interface layer.
2. Configured and activated the multi-controller architecture (`devotics_arm_controller` + `gripper_controller` + `joint_state_broadcaster`).
3. Installed `ros2controlcli` to inspect and claim live hardware interfaces.
4. Verified headless action commanding over `control_msgs/action/FollowJointTrajectory`.
5. Created and executed [`scripts/pick_and_place.py`](file:///home/ishan/ros2_ws/src/devotics_arm_description/scripts/pick_and_place.py)—an autonomous Python state machine executing a full pick-and-place cycle without GUI interaction.

---

## 🏗️ Architecture Overview

```
                      Autonomous Python Node
                   (scripts/pick_and_place.py)
                                │
          ┌─────────────────────┴─────────────────────┐
          │ (Action Goal: FollowJointTrajectory)      │ (Action Goal: FollowJointTrajectory)
          ▼                                           ▼
/devotics_arm_controller/follow_joint_trajectory   /gripper_controller/follow_joint_trajectory
          │                                           │
          └─────────────────────┬─────────────────────┘
                                ▼
                       controller_manager
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
       devotics_arm_controller         gripper_controller
      (JointTrajectoryController)   (JointTrajectoryController)
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
                  ros2_control Resource Manager
                                │
        Claims 8 Command Interfaces (6 arm + 2 finger positions)
                                │
                                ▼
                    Hardware Interface Layer
                 (mock_components/GenericSystem)
```

---

## 🛠️ Step-by-Step Implementation

### 1. Expanding the Hardware Interface Layer ([`urdf/devotics_arm.ros2_control.xacro`](file:///home/ishan/ros2_ws/src/devotics_arm_description/urdf/devotics_arm.ros2_control.xacro))
Previously, only `joint1` through `joint6` existed in the hardware tag. We added both prismatic finger joints:

```xml
<!-- LEFT FINGER -->
<joint name="left_finger_joint">
  <command_interface name="position"/>
  <state_interface name="position">
    <param name="initial_value">0.0</param>
  </state_interface>
  <state_interface name="velocity"/>
</joint>

<!-- RIGHT FINGER -->
<joint name="right_finger_joint">
  <command_interface name="position"/>
  <state_interface name="position">
    <param name="initial_value">0.0</param>
  </state_interface>
  <state_interface name="velocity"/>
</joint>
```

### 2. Multi-Controller Configuration ([`config/ros2_controllers.yaml`](file:///home/ishan/ros2_ws/src/devotics_arm_moveit_config/config/ros2_controllers.yaml))
We registered `gripper_controller` with the `controller_manager`:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100

    devotics_arm_controller:
      type: joint_trajectory_controller/JointTrajectoryController

    gripper_controller:
      type: joint_trajectory_controller/JointTrajectoryController

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

gripper_controller:
  ros__parameters:
    joints:
      - left_finger_joint
      - right_finger_joint
    command_interfaces:
      - position
    state_interfaces:
      - position
      - velocity
```

### 3. MoveIt Controller Bridge ([`config/moveit_controllers.yaml`](file:///home/ishan/ros2_ws/src/devotics_arm_moveit_config/config/moveit_controllers.yaml))
```yaml
moveit_simple_controller_manager:
  controller_names:
    - devotics_arm_controller
    - gripper_controller

  gripper_controller:
    type: FollowJointTrajectory
    action_ns: follow_joint_trajectory
    default: true
    joints:
      - left_finger_joint
      - right_finger_joint
```

---

## ⚠️ Obstacles, Mistakes & How We Tackled Them

### Obstacle 1: The Missing Finger Hardware Interfaces
* **The Mistake:** Attempting to define `gripper_controller` in YAML before adding finger joints to Xacro.
* **The Problem:** The `controller_manager` rejected `gripper_controller` during startup with errors stating `command interface 'left_finger_joint/position' does not exist`.
* **How We Tackled It:** Added explicit `<joint>` tags inside `<ros2_control>` in `devotics_arm.ros2_control.xacro` with `initial_value = 0.0`.

### Obstacle 2: `ros2: error: invalid choice: 'control'`
* **The Error:** Running `ros2 control list_controllers` produced an argument error:
  `ros2: error: argument: invalid choice: 'control'`
* **Why It Happened:** The `ros2 control` command-line tool is not part of the standard core ROS 2 install. It lives in a separate package called `ros2controlcli`.
* **How We Tackled It:** Installed the missing tool:
  ```bash
  sudo apt install -y ros-jazzy-ros2controlcli
  ```
  Immediately afterward, `ros2 control list_controllers` and `ros2 control list_hardware_interfaces` functioned perfectly.

### Obstacle 3: Understanding `[available] [claimed]` Status
* **The Confusion:** When running `ros2 control list_hardware_interfaces`, we saw:
  `joint1/position [available] [claimed]`
* **What This Means:**
  * `[available]`: The hardware interface plugin successfully created the memory handle for this joint.
  * `[claimed]`: An active controller (`devotics_arm_controller` or `gripper_controller`) has successfully taken exclusive ownership of the write channel. If an interface is `[unclaimed]`, no motor commands will be sent.

---

## 🤖 The Autonomous Pick & Place Node ([`scripts/pick_and_place.py`](file:///home/ishan/ros2_ws/src/devotics_arm_description/scripts/pick_and_place.py))

Instead of manually clicking buttons or sending individual YAML strings from bash, we authored a complete Python ROS 2 node using asynchronous action clients:

```python
class DevoticsMissionController(Node):
    def __init__(self):
        super().__init__('devotics_mission_controller')
        self.arm_client = ActionClient(self, FollowJointTrajectory, '/devotics_arm_controller/follow_joint_trajectory')
        self.gripper_client = ActionClient(self, FollowJointTrajectory, '/gripper_controller/follow_joint_trajectory')
```

### Execution Cycle:
1. **Ready Pose:** Arm moves to $[0.0, -0.5, 0.8, 0.0, 0.0, 0.0]$ in 3.0 seconds.
2. **Open Gripper:** Fingers slide outward to $0.03\text{ m}$ ($60\text{ mm}$ total opening).
3. **Approach Object:** Arm pitches down to $[0.0, -1.0, 1.4, -0.4, 0.0, 0.0]$.
4. **Grasp:** Fingers clamp shut to $0.0\text{ m}$.
5. **Lift:** Arm returns up to Ready Pose holding the virtual target.
6. **Home:** Arm returns safely to $[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]$.

---

## ✅ Phase 3 Pass Criteria Met
1. `ros2 control list_controllers` displays `devotics_arm_controller`, `gripper_controller`, and `joint_state_broadcaster` as `active`.
2. Direct terminal actions move the gripper and arm independently.
3. `python3 scripts/pick_and_place.py` runs end-to-end with zero errors and smooth visual execution in RViz.
