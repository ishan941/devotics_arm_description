# Devotics Robotic Arm V1 — Engineering Build Log (Day 14)

**Packages:** `devotics_arm_description`, `devotics_arm_moveit_config`  
**ROS 2 Distribution:** Jazzy / Ubuntu 24.04 (arm64)  
**Topic:** `ros2_control` Mock Hardware Interface & Controller Pipeline  
**Target:** Providing a simulated hardware layer for MoveIt 2 to send trajectory commands to  

---

## 📌 Goal & Overview
MoveIt 2 does **not** move joints directly. Instead:
1. MoveIt computes a trajectory.
2. MoveIt sends that trajectory as an action goal (`FollowJointTrajectory.action`).
3. A controller (such as `joint_trajectory_controller`) receives the goal and interpolates setpoints at high frequency (100 Hz).
4. The controller writes positions to the **Hardware Interface** (`ros2_control`).

On Day 14, we configured the `mock_components/GenericSystem` hardware interface so the arm can execute trajectories in simulation without physical motors.

---

## 🛠️ Implementation Steps

### 1. The `<ros2_control>` Tag in Xacro
We created [`urdf/devotics_arm.ros2_control.xacro`](file:///home/ishan/ros2_ws/src/devotics_arm_description/urdf/devotics_arm.ros2_control.xacro) and included it into [`urdf/devotics_arm.urdf.xacro`](file:///home/ishan/ros2_ws/src/devotics_arm_description/urdf/devotics_arm.urdf.xacro):

```xml
<ros2_control name="DevoticsMockHardware" type="system">
    <hardware>
        <plugin>mock_components/GenericSystem</plugin>
        <!-- In physical robot, this will be replaced with serial/ESP32 plugin -->
    </hardware>
    
    <xacro:macro name="configure_joint" params="joint_name">
        <joint name="${joint_name}">
            <command_interface name="position"/>
            <state_interface name="position">
                <param name="initial_value">0.0</param>
            </state_interface>
            <state_interface name="velocity"/>
        </joint>
    </xacro:macro>

    <xacro:configure_joint joint_name="joint1"/>
    <xacro:configure_joint joint_name="joint2"/>
    <xacro:configure_joint joint_name="joint3"/>
    <xacro:configure_joint joint_name="joint4"/>
    <xacro:configure_joint joint_name="joint5"/>
    <xacro:configure_joint joint_name="joint6"/>
</ros2_control>
```

### 2. Controller Configuration ([`ros2_controllers.yaml`](file:///home/ishan/ros2_ws/src/devotics_arm_moveit_config/config/ros2_controllers.yaml))
```yaml
controller_manager:
  ros__parameters:
    update_rate: 100 # Hz

    devotics_arm_controller:
      type: joint_trajectory_controller/JointTrajectoryController

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

devotics_arm_controller:
  ros__parameters:
    joints:
      - joint1
      - joint2
      - joint3
      - joint4
      - joint5
      - joint6
    command_interfaces:
      - position
    state_interfaces:
      - position
      - velocity
```

### 3. MoveIt Controller Bridge ([`moveit_controllers.yaml`](file:///home/ishan/ros2_ws/src/devotics_arm_moveit_config/config/moveit_controllers.yaml))
Tells MoveIt which action server to talk to:
```yaml
moveit_controller_manager: moveit_simple_controller_manager/MoveItSimpleControllerManager

moveit_simple_controller_manager:
  controller_names:
    - devotics_arm_controller

  devotics_arm_controller:
    type: FollowJointTrajectory
    action_ns: follow_joint_trajectory
    default: true
    joints:
      - joint1
      - joint2
      - joint3
      - joint4
      - joint5
      - joint6
```

---

## ⚠️ Obstacles, Mistakes & How They Were Solved

### Obstacle 1: Mismatched Action Server Namespaces
* **The Error:** In MoveIt RViz, clicking "Execute" resulted in:
  `Action server /devotics_arm_controller/follow_joint_trajectory not available`
* **Why it happened:** `moveit_controllers.yaml` had `action_ns: devotics_arm_controller/follow_joint_trajectory`, causing MoveIt to look for `/devotics_arm_controller/devotics_arm_controller/follow_joint_trajectory` (double namespace nesting!).
* **How We Solved It:** Standardized the convention:
  * Controller Name: `devotics_arm_controller`
  * Action Namespace: `follow_joint_trajectory`
  * Full ROS 2 Action: `/devotics_arm_controller/follow_joint_trajectory`

### Obstacle 2: Mock Hardware Initial Values
* **The Error:** RViz opened with joints at arbitrary or uninitialized states, causing MoveIt to report the robot was in collision before any plan was even commanded.
* **How We Solved It:** Added `<param name="initial_value">0.0</param>` to the `<state_interface name="position">` for all joints inside the mock hardware interface.

---

## ✅ Verification Test
Verify the controllers spawn and become active:
```bash
ros2 control list_controllers
```
Expected output:
```text
joint_state_broadcaster[joint_state_broadcaster/JointStateBroadcaster] active
devotics_arm_controller[joint_trajectory_controller/JointTrajectoryController] active
```
