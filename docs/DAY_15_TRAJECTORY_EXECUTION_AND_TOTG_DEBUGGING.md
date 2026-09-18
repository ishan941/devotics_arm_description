# Devotics Robotic Arm V1 — Engineering Build Log (Day 15)

**Packages:** `devotics_arm_description`, `devotics_arm_moveit_config`  
**ROS 2 Distribution:** Jazzy / Ubuntu 24.04 (arm64)  
**Topic:** The Great Trajectory Execution Obstacle — Time-Optimal Trajectory Generation (TOTG) Debugging  
**Target:** Solving the "Plan Works, Execute Fails" Error and Achieving Autonomous Motion  

---

## 📌 Executive Summary
On Day 15, we faced the most deceptive and notorious obstacle in modern MoveIt 2:
> **"Plan" succeeded in 0.027s, but clicking "Execute" immediately failed and aborted the motion.**

This document details the exact investigative process, the hidden root cause inside ROS 2's controller architecture, and the definitive fix that made the arm move.

---

## 🔍 The Symptom: "Plan Works, Execute Fails"

### 1. What Happened in the GUI
* In RViz (via `demo.launch.py`), we selected Planning Group `devotics_arm` and Goal State `ready`.
* We clicked **Plan**:
  * The planning progress bar turned green.
  * Time displayed: `0.027s`.
  * The ghost arm swept through the motion smoothly in RViz preview.
* We clicked **Execute**:
  * The GUI immediately flashed red with **Failed**.
  * The physical/mock robot did not move at all.

---

## 🕵️ The Investigation: Digging into `~/.ros/log/`

Instead of guessing, we inspected the ROS 2 launch logs located at:
`~/.ros/log/<latest_session>/launch.log`

There we uncovered the exact fatal error:
```text
[devotics_arm_controller]: Received new action goal
[ERROR] [devotics_arm_controller]: Time between points 0 and 1 is not strictly increasing, it is 0.000000 and 0.000000 respectively
[rviz2-4] [INFO] [move_group_interface]: Execute request aborted
```

---

## 🧠 Deep-Dive Root Cause Analysis

### 1. Geometric Paths vs Timed Trajectories
When you ask OMPL (e.g. `RRTConnect`) to plan a motion, it calculates a **purely geometric path**: a sequence of waypoints in joint angle space:
$$W_0 = [0.0, 0.0, \dots], \quad W_1 = [0.05, -0.02, \dots], \quad W_2 = [0.10, -0.05, \dots]$$
**OMPL has no concept of time, velocity, or motor torque.** It only knows geometry and collision avoidance.

### 2. The Job of MoveIt's Response Adapters
To send a path to a real controller, MoveIt 2 passes the geometric path through a pipeline of **Response Adapters**:
```text
OMPL Geometric Path
       │
       ↓
[default_planning_response_adapters/AddTimeOptimalParameterization]
       │
       ↓
Timed Trajectory (Point 0 at 0.0s, Point 1 at 0.12s, Point 2 at 0.25s, ...)
```
The algorithm used is **Time-Optimal Trajectory Generation (TOTG)**.

### 3. The "Silent Killer": Zero Acceleration Limits
TOTG calculates the time duration between waypoints using physics:
$$v(t) \le v_{\max}, \quad a(t) \le a_{\max}$$
We inspected [`config/joint_limits.yaml`](file:///home/ishan/ros2_ws/src/devotics_arm_moveit_config/config/joint_limits.yaml) and discovered:
```yaml
joint_limits:
  joint1:
    has_velocity_limits: true
    max_velocity: 1.0
    has_acceleration_limits: false  # <-- THE CULPRIT!
    max_acceleration: 0.0           # <-- THE CULPRIT!
  joint2:
    has_velocity_limits: true
    max_velocity: 1.0
    has_acceleration_limits: false
    max_acceleration: 0.0
  # ... same for joints 3, 4, 5, 6
```
Because `has_acceleration_limits` was `false` and `max_acceleration` was `0.0`:
1. TOTG could not apply an acceleration curve to the trajectory.
2. It failed to parameterize timestamps.
3. Waypoint 0 was assigned `time_from_start = 0.000000`.
4. Waypoint 1 was ALSO assigned `time_from_start = 0.000000`.
5. When this goal arrived at `joint_trajectory_controller`, the controller strictly asserted:
   $$t_{i+1} > t_i$$
   Since $0.000000 \ngtr 0.000000$, the controller rejected the goal immediately!

### 4. The Colcon Build Gotcha
Even when files inside `src/devotics_arm_moveit_config/config/` were edited, RViz was loading parameters from `install/devotics_arm_moveit_config/share/...`. Because the package was not built with `--symlink-install`, the active nodes were running the outdated files from the previous build!

---

## 🛠️ The Complete Solution (Step-by-Step)

### Step 1: Fix [`joint_limits.yaml`](file:///home/ishan/ros2_ws/src/devotics_arm_moveit_config/config/joint_limits.yaml)
We enabled acceleration limits and set realistic values:
```yaml
default_velocity_scaling_factor: 0.5
default_acceleration_scaling_factor: 0.5

joint_limits:
  joint1:
    has_velocity_limits: true
    max_velocity: 1.0
    has_acceleration_limits: true
    max_acceleration: 2.0
  joint2:
    has_velocity_limits: true
    max_velocity: 1.0
    has_acceleration_limits: true
    max_acceleration: 2.0
  joint3:
    has_velocity_limits: true
    max_velocity: 1.0
    has_acceleration_limits: true
    max_acceleration: 2.0
  joint4:
    has_velocity_limits: true
    max_velocity: 1.0
    has_acceleration_limits: true
    max_acceleration: 2.0
  joint5:
    has_velocity_limits: true
    max_velocity: 1.5
    has_acceleration_limits: true
    max_acceleration: 3.0
  joint6:
    has_velocity_limits: true
    max_velocity: 2.0
    has_acceleration_limits: true
    max_acceleration: 4.0
  left_finger_joint:
    has_velocity_limits: true
    max_velocity: 0.1
    has_acceleration_limits: true
    max_acceleration: 0.5
  right_finger_joint:
    has_velocity_limits: true
    max_velocity: 0.1
    has_acceleration_limits: true
    max_acceleration: 0.5
```

### Step 2: Ensure Response Adapters in [`ompl_planning.yaml`](file:///home/ishan/ros2_ws/src/devotics_arm_moveit_config/config/ompl_planning.yaml)
```yaml
planning_plugins:
  - ompl_interface/OMPLPlanner
request_adapters:
  - default_planning_request_adapters/ResolveConstraintFrames
  - default_planning_request_adapters/ValidateWorkspaceBounds
  - default_planning_request_adapters/CheckStartStateBounds
  - default_planning_request_adapters/CheckStartStateCollision
response_adapters:
  - default_planning_response_adapters/AddTimeOptimalParameterization
  - default_planning_response_adapters/ValidateSolution
  - default_planning_response_adapters/DisplayMotionPath
default_planning_pipeline: ompl
```

### Step 3: Clean Lingering Processes
Stale background nodes holding the controller manager or RViz ports were killed:
```bash
killall -9 rviz2 move_group ros2_control_node robot_state_publisher 2>/dev/null || true
```

### Step 4: Rebuild with `--symlink-install`
```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select devotics_arm_description devotics_arm_moveit_config
source install/setup.bash
```
*Why `--symlink-install` is critical:* It links the configuration YAML files directly from `src/` to `install/`, ensuring any future parameter changes take effect immediately upon next launch without requiring a rebuild!

---

## ✅ The Result: Flawless Execution!
We launched:
```bash
ros2 launch devotics_arm_moveit_config demo.launch.py
```
1. Selected Planning Group `devotics_arm`.
2. Picked Goal State `ready`.
3. Clicked **Plan** — Trajectory parameterized with non-zero duration (~2.5 seconds).
4. Clicked **Execute** — **The arm smoothly animated to the `ready` position! No crashes, no aborts!**
