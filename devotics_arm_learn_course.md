# Devotics Robotic Arm — Agentic Engineering Course
**Learning Mode: Agentic (AI pair-programmer active)**
**Started:** September 2026 | **Target:** Devotics Arm V1 — fully integrated physical robot

---

## Final System Architecture
```
             RViz / User
                  │
                  ↓
               MoveIt 2
                  │
          Motion Planning
                  ↓
         Joint Trajectory
                  │
                  ↓
            ros2_control
                  │
                  ↓
       Devotics Hardware Interface
                  │
              USB Serial
                  │
                  ↓
                ESP32
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
    Drivers    Drivers    Drivers
       ↓          ↓          ↓
    J1  J2     J3  J4     J5  J6
                  │
               Gripper
```

**PC calculates trajectories. ESP32 handles low-level control: step timing, homing, limits, feedback, safety.**
**V1 uses USB Serial first — simpler and more reliable than Wi-Fi for a bench prototype.**

---

## How Agentic Learning Works

> **Old way:** Read theory → try to build → get stuck → search → repeat.
> **Agentic way:** Build immediately → AI explains in context → verify with a real test → push to git → next day.

### Rules
- Every day ends with a **concrete file in your repo** and a **pass/fail test** you can run
- **No day is "reading only"** — every day you write or modify real ROS2 code
- Paste errors directly to the AI — don't spend more than 5 minutes stuck alone
- **Commit every day**: `git add -A && git commit -m "Day X: <what you built>"`
- Days can be compressed: if you finish early, ask "what's next?" and keep going

---

## Progress Tracker

| Phase | Days | Status |
|-------|------|--------|
| PHASE 1 — ROS Fundamentals (URDF + TF) | 1–10 | 🔄 Day 5 next |
| PHASE 2 — Kinematics + MoveIt | 11–20 | ⬜ |
| PHASE 3 — ros2_control | 21–25 | ⬜ |
| PHASE 4 — Gazebo Simulation | 26–30 | ⬜ (ARM64 budget rule applies) |
| PHASE 5 — Mechanical Engineering | 31–35 | ⬜ |
| PHASE 6 — Physical Joint Prototype | 36–45 | ⬜ |
| PHASE 7 — Build Full Physical Arm | 46–55 | ⬜ |
| PHASE 8 — MoveIt → Real Arm Integration | 56–60 | ⬜ |

---

## PHASE 1 — ROS FUNDAMENTALS: URDF + TF

### Completed Work

| Day | Topic | Deliverable | Status |
|-----|-------|-------------|--------|
| 1 | ROS2 install, RViz, tools | Dev environment ready | ✅ |
| 2 | URDF, links, joints, TF | `devotics_arm_day2_backup.urdf` — 1-DOF arm | ✅ |
| 3 | 3-DOF arm (base→shoulder→elbow) | `devotics_arm.urdf` — 3 joint sliders | ✅ |
| 4 | Joint axes (X/Y/Z experiments) | Understood why `axis xyz` changes rotation direction | ✅ |

---

### DAY 5 — TF Tree: Understanding Your Arm's Spatial Identity
**Goal:** Inspect the live TF tree of your 3-DOF arm and understand exactly how ROS tracks every link in space.

**What you will learn:** How `robot_state_publisher` broadcasts transforms. How `joint_state_publisher_gui` drives them. How to read a TF tree.

#### Step 1 — Launch your arm
```bash
cd ~/ros2_ws
colcon build --packages-select devotics_arm_description
source install/setup.bash
ros2 launch devotics_arm_description display.launch.py
```
RViz should open with your 3-DOF arm and 3 joint sliders.

#### Step 2 — Inspect the live TF topic
Open a second terminal:
```bash
source ~/ros2_ws/install/setup.bash
ros2 topic echo /tf
```
Move a slider. Watch the transform numbers change in real time.
**What you see:** `translation` (x,y,z) + `rotation` (quaternion) for each joint frame.

#### Step 3 — See the full static TF
```bash
ros2 topic echo /tf_static
```
These are the fixed transforms (joints at zero position).

#### Step 4 — View the TF tree as a graph
```bash
ros2 run tf2_tools view_frames
xdg-open frames.pdf
```
You should see:
```
base_link
    └── shoulder_link   (joint1 — Z axis rotation)
            └── upper_arm_link  (joint2 — Y axis rotation)
                    └── forearm_link    (joint3 — Y axis rotation)
```

#### Step 5 — Query a specific transform live
```bash
ros2 run tf2_ros tf2_echo base_link forearm_link
```
Move joint sliders. Watch the transform from base to forearm tip update.
**This is the essence of forward kinematics** — joint angles → end-effector position.

#### Step 6 — See all active nodes and topics
```bash
ros2 node list
ros2 topic list
ros2 topic info /joint_states
```

#### ✅ Day 5 Pass Test
Run this and confirm values change when you move sliders:
```bash
ros2 run tf2_ros tf2_echo base_link forearm_link
```
You should see XYZ translation values that are **not zero** when joints are moved.

**Commit:**
```bash
cd ~/ros2_ws/src/devotics_arm_description
git add -A && git commit -m "Day 5: TF tree inspected, understood link/joint hierarchy"
```

---

### DAY 6 — Wrist Joints: J4 and J5 (5-DOF)
**Goal:** Extend your arm from 3 joints to 5 by adding wrist pitch (J4) and wrist roll (J5).

Add after the forearm_link and joint3 block in `urdf/devotics_arm.urdf`:

```xml
    <!-- WRIST LINK 1 -->
    <link name="wrist1_link">
        <visual>
            <origin xyz="0 0 0.05" rpy="0 0 0"/>
            <geometry>
                <cylinder radius="0.04" length="0.10"/>
            </geometry>
            <material name="wrist1_color">
                <color rgba="0.85 0.50 0.10 1"/>
            </material>
        </visual>
    </link>

    <!-- JOINT 4 - WRIST PITCH -->
    <joint name="joint4" type="revolute">
        <parent link="forearm_link"/>
        <child link="wrist1_link"/>
        <origin xyz="0 0 0.25" rpy="0 0 0"/>
        <axis xyz="0 1 0"/>
        <limit lower="-1.57" upper="1.57" effort="10" velocity="1.0"/>
    </joint>

    <!-- WRIST LINK 2 -->
    <link name="wrist2_link">
        <visual>
            <origin xyz="0 0 0.05" rpy="0 0 0"/>
            <geometry>
                <cylinder radius="0.035" length="0.10"/>
            </geometry>
            <material name="wrist2_color">
                <color rgba="0.90 0.70 0.10 1"/>
            </material>
        </visual>
    </link>

    <!-- JOINT 5 - WRIST ROLL -->
    <joint name="joint5" type="revolute">
        <parent link="wrist1_link"/>
        <child link="wrist2_link"/>
        <origin xyz="0 0 0.10" rpy="0 0 0"/>
        <axis xyz="0 0 1"/>
        <limit lower="-3.14" upper="3.14" effort="10" velocity="1.5"/>
    </joint>
```

#### ✅ Day 6 Pass Test
```bash
colcon build --packages-select devotics_arm_description && source install/setup.bash
ros2 launch devotics_arm_description display.launch.py
```
You should see **5 joint sliders** in the joint_state_publisher_gui window.

**Commit:** `git add -A && git commit -m "Day 6: Added J4 (wrist pitch) and J5 (wrist roll) — 5-DOF arm"`

---

### DAY 7 — Wrist Roll J6: 6-DOF Arm Complete
**Goal:** Add the 6th degree of freedom (wrist yaw). Your arm now has the same kinematic structure as industrial robots.

Add after joint5 in `urdf/devotics_arm.urdf`:

```xml
    <!-- WRIST LINK 3 (tool flange) -->
    <link name="wrist3_link">
        <visual>
            <origin xyz="0 0 0.03" rpy="0 0 0"/>
            <geometry>
                <cylinder radius="0.03" length="0.06"/>
            </geometry>
            <material name="wrist3_color">
                <color rgba="0.95 0.90 0.10 1"/>
            </material>
        </visual>
    </link>

    <!-- JOINT 6 - WRIST YAW (tool rotation) -->
    <joint name="joint6" type="revolute">
        <parent link="wrist2_link"/>
        <child link="wrist3_link"/>
        <origin xyz="0 0 0.10" rpy="0 0 0"/>
        <axis xyz="0 1 0"/>
        <limit lower="-3.14" upper="3.14" effort="5" velocity="2.0"/>
    </joint>
```

#### ✅ Day 7 Pass Test
6 sliders visible. Run TF and count 7 frames (base + 6 links):
```bash
ros2 run tf2_tools view_frames && xdg-open frames.pdf
```

**Commit:** `git add -A && git commit -m "Day 7: Added J6 (wrist yaw) — full 6-DOF kinematic chain"`

---

### DAY 8 — Gripper: The End Effector
**Goal:** Add a parallel gripper with prismatic (sliding) finger joints.

Add after joint6 in `urdf/devotics_arm.urdf`:

```xml
    <!-- GRIPPER BASE LINK -->
    <link name="gripper_base_link">
        <visual>
            <origin xyz="0 0 0.02" rpy="0 0 0"/>
            <geometry>
                <box size="0.08 0.04 0.04"/>
            </geometry>
            <material name="gripper_base_color">
                <color rgba="0.20 0.20 0.20 1"/>
            </material>
        </visual>
    </link>

    <joint name="gripper_base_joint" type="fixed">
        <parent link="wrist3_link"/>
        <child link="gripper_base_link"/>
        <origin xyz="0 0 0.06" rpy="0 0 0"/>
    </joint>

    <!-- LEFT FINGER -->
    <link name="left_finger_link">
        <visual>
            <origin xyz="0 0.02 0.03" rpy="0 0 0"/>
            <geometry>
                <box size="0.02 0.02 0.06"/>
            </geometry>
            <material name="finger_color">
                <color rgba="0.60 0.60 0.60 1"/>
            </material>
        </visual>
    </link>

    <joint name="left_finger_joint" type="prismatic">
        <parent link="gripper_base_link"/>
        <child link="left_finger_link"/>
        <origin xyz="0 0 0.02" rpy="0 0 0"/>
        <axis xyz="0 1 0"/>
        <limit lower="0.0" upper="0.04" effort="5" velocity="0.1"/>
    </joint>

    <!-- RIGHT FINGER -->
    <link name="right_finger_link">
        <visual>
            <origin xyz="0 -0.02 0.03" rpy="0 0 0"/>
            <geometry>
                <box size="0.02 0.02 0.06"/>
            </geometry>
            <material name="finger_color">
                <color rgba="0.60 0.60 0.60 1"/>
            </material>
        </visual>
    </link>

    <joint name="right_finger_joint" type="prismatic">
        <parent link="gripper_base_link"/>
        <child link="right_finger_link"/>
        <origin xyz="0 0 0.02" rpy="0 0 0"/>
        <axis xyz="0 -1 0"/>
        <limit lower="0.0" upper="0.04" effort="5" velocity="0.1"/>
    </joint>
```

#### ✅ Day 8 Pass Test
**8 sliders** (6 revolute + 2 prismatic fingers). Move the finger sliders — fingers open and close.

**Commit:** `git add -A && git commit -m "Day 8: Added parallel gripper with prismatic finger joints"`

---

### DAY 9 — Xacro: Convert URDF to Reusable Macros
**Goal:** Convert `devotics_arm.urdf` into `devotics_arm.urdf.xacro`.

#### Step 1 — Install Xacro (if needed)
```bash
sudo apt install ros-jazzy-xacro
```

#### Step 2 — Create `urdf/devotics_arm.urdf.xacro`

Header:
```xml
<?xml version="1.0"?>
<robot name="devotics_arm" xmlns:xacro="http://www.ros.org/wiki/xacro">

    <!-- PROPERTIES — edit here once, used everywhere -->
    <xacro:property name="base_radius"   value="0.10"/>
    <xacro:property name="base_height"   value="0.10"/>
    <xacro:property name="upper_arm_len" value="0.30"/>
    <xacro:property name="forearm_len"   value="0.25"/>
    <xacro:property name="pi"            value="3.14159"/>

    <!-- ... paste all links/joints using ${upper_arm_len} etc. ... -->

</robot>
```

#### Step 3 — Update launch file to use xacro
Edit `launch/display.launch.py` — replace the file.read() block:
```python
import xacro

robot_description_doc = xacro.process_file(
    os.path.join(package_path, 'urdf', 'devotics_arm.urdf.xacro')
)
robot_description = robot_description_doc.toxml()
```

#### Step 4 — Test xacro
```bash
ros2 run xacro xacro urdf/devotics_arm.urdf.xacro
```
No errors = working Xacro.

#### ✅ Day 9 Pass Test
```bash
colcon build --packages-select devotics_arm_description && source install/setup.bash
ros2 launch devotics_arm_description display.launch.py
```
Arm appears exactly as before.

**Commit:** `git add -A && git commit -m "Day 9: Converted URDF to Xacro with properties"`

---

### DAY 10 — Joint Limits, Home Pose, Final Kinematic Model
**Goal:** Set realistic joint limits and define named poses in YAML.

#### Step 1 — Realistic limits (add as Xacro properties)
```xml
<xacro:property name="j1_lower" value="-3.14"/>   <!-- Base: full rotation -->
<xacro:property name="j1_upper" value="3.14"/>
<xacro:property name="j2_lower" value="-1.57"/>   <!-- Shoulder: +/-90deg -->
<xacro:property name="j2_upper" value="1.57"/>
<xacro:property name="j3_lower" value="-2.09"/>   <!-- Elbow: -120 to +120deg -->
<xacro:property name="j3_upper" value="2.09"/>
<xacro:property name="j4_lower" value="-1.57"/>
<xacro:property name="j4_upper" value="1.57"/>
<xacro:property name="j5_lower" value="-3.14"/>
<xacro:property name="j5_upper" value="3.14"/>
<xacro:property name="j6_lower" value="-3.14"/>
<xacro:property name="j6_upper" value="3.14"/>
```

#### Step 2 — Create `config/joint_poses.yaml`
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

#### ✅ Day 10 Pass Test — Stage Gate 1
```bash
ros2 run xacro xacro urdf/devotics_arm.urdf.xacro | grep "joint name"
```
All 9 joints appear: joint1-6 + gripper_base_joint + left/right_finger_joint.

**Commit:** `git add -A && git commit -m "Day 10: Joint limits set, named poses defined — complete virtual arm V1"`

**STAGE GATE 1 COMPLETE: Full 6-DOF + gripper virtual arm ready for MoveIt**

---

## PHASE 2 — KINEMATICS + MOVEIT 2
### Days 11–20

| Day | Topic | Key Command/Deliverable |
|-----|-------|------------------------|
| 11 | Forward Kinematics intuition | `tf2_echo base_link wrist3_link` while moving joints |
| 12 | Inverse Kinematics concept | Read MoveIt IK docs + test moveit_commander in Python |
| 13 | End-effector frame | Add `tool0` link at gripper tip as fixed child of `wrist3_link` |
| 14 | Workspace analysis | Use MoveIt RViz: drag target, find reachable envelope |
| 15 | Singularity testing | Identify arm-straight and wrist-lock configurations |
| 16 | MoveIt demo (demo robot) | `ros2 launch moveit_resources_panda_moveit_config demo.launch.py` |
| 17 | MoveIt Setup Assistant | Import devotics Xacro, start config generation |
| 18 | Planning groups | Configure `devotics_arm` (joints 1-6) + `gripper` group |
| 19 | End effector + named poses | Set home/ready/pickup in Setup Assistant |
| 20 | First motion plan | Plan to multiple poses, Execute in RViz |

#### Day 16 Quick Start:
```bash
sudo apt install ros-jazzy-moveit
ros2 launch moveit_resources_panda_moveit_config demo.launch.py
```

#### Day 17 Setup Assistant:
```bash
ros2 launch moveit_setup_assistant setup_assistant.launch.py
```
Load your `devotics_arm.urdf.xacro` → follow wizard → save config to:
`~/ros2_ws/src/devotics_arm_moveit_config/`

#### ✅ Phase 2 Gate Test (Day 20):
In RViz MoveIt plugin:
1. Drag interactive marker to a target pose
2. Click Plan
3. Click Execute
4. Virtual arm moves along planned trajectory — no errors

---

## PHASE 3 — ROS2_CONTROL
### Days 21–25

| Day | Topic | Key File/Command |
|-----|-------|-----------------|
| 21 | Controller Manager, hardware interfaces | Read ros2_control architecture |
| 22 | Add ros2_control block to Xacro | `urdf/devotics_arm.urdf.xacro` |
| 23 | Joint State Broadcaster | `config/controllers.yaml` |
| 24 | Joint Trajectory Controller | Add to controllers.yaml, test with `ros2 topic pub` |
| 25 | MoveIt → ros2_control pipeline | Full Plan + Execute through controller |

#### Day 22 — ros2_control block to add to Xacro:
```xml
<ros2_control name="devotics_arm_hardware" type="system">
    <hardware>
        <plugin>mock_components/GenericSystem</plugin>
    </hardware>
    <joint name="joint1">
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
    </joint>
    <!-- Repeat for joint2 through joint6 -->
</ros2_control>
```

#### Day 23 — `config/controllers.yaml`:
```yaml
controller_manager:
  ros__parameters:
    update_rate: 100
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster
    joint_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController

joint_trajectory_controller:
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

#### ✅ Phase 3 Gate Test (Day 25):
```bash
ros2 control list_controllers
```
Expected:
```
joint_state_broadcaster[...] active
joint_trajectory_controller[...] active
```
MoveIt Plan+Execute works through the controller.

---

## PHASE 4 — GAZEBO SIMULATION
### Days 26–30

> ARM64 Rule: If Gazebo becomes the main blocker, skip to Phase 5. Return later.

| Day | Topic | Deliverable |
|-----|-------|-------------|
| 26 | Install Gazebo Harmonic | `gz sim --version` works |
| 27 | Spawn Devotics arm in Gazebo | Robot appears in 3D world |
| 28 | Mass + inertia tags | Physics-correct URDF |
| 29 | ROS-Gazebo bridge + controllers | Joint commands work in sim |
| 30 | Table + cube world | Pick-and-place test environment |

#### Day 26 Install:
```bash
sudo apt install ros-jazzy-ros-gz
gz sim --version
```

#### Day 28 — Inertia macro (add to Xacro):
```xml
<xacro:macro name="cylinder_inertia" params="mass radius length">
    <inertial>
        <mass value="${mass}"/>
        <inertia
            ixx="${mass*(3*radius*radius + length*length)/12}"
            iyy="${mass*(3*radius*radius + length*length)/12}"
            izz="${mass*radius*radius/2}"
            ixy="0" ixz="0" iyz="0"/>
    </inertial>
</xacro:macro>
```

---

## PHASE 5 — MECHANICAL ENGINEERING
### Days 31–35: Engineer Before Buying

| Day | Topic | Deliverable |
|-----|-------|-------------|
| 31 | Requirements specification | `docs/arm_requirements.md` |
| 32 | Link lengths + geometry | `docs/arm_geometry.md` + sketch |
| 33 | Torque calculations | `docs/torque_analysis.md` with numbers |
| 34 | Transmission design | Gear ratio decision per joint |
| 35 | BOM + costing | `docs/bom.md` — hardware purchase decision |

#### Day 31 — Spec Template (fill in with AI):
```
Desktop or floor mounted?    →
Maximum reach?               → mm
Target payload?              → g
Desired speed?               → deg/s
Position accuracy?           → mm
Total arm weight target?     → kg
Continuous or occasional?    →
```

#### Day 33 — Torque Formula:
```
τ_shoulder = (m_forearm + m_wrist + m_gripper + m_payload) × g × L_upper_arm × safety_factor
```
- safety_factor = 1.5 to 2.0 recommended

**STAGE GATE 2: Only purchase hardware after Day 35 BOM is complete and torque math confirms motor selection.**

---

## PHASE 6 — BUILD ONE REAL JOINT
### Days 36–45: Physical Prototype (Shoulder First)

| Day | Topic | Pass Test |
|-----|-------|-----------|
| 36 | Print joint housing + link | Part fits motor shaft |
| 37 | Motor + driver bench test | Motor spins on command |
| 38 | Homing + limit switch | Known zero position repeatable |
| 39 | ESP32 serial protocol | `angle 45` → joint moves to 45deg |
| 40 | ROS2 → ESP32 bridge | `ros2 topic pub /joint_cmd` moves physical joint |
| 41 | Angle calibration | Requested vs actual within +/-2deg |
| 42 | Backlash measurement | Direction-reversal error documented |
| 43 | Thermal test | 30-min continuous run, no overheating |
| 44 | Load test | Moves target payload without stalling |
| 45 | Design revision | Joint V2 approved or issues fixed |

#### Day 39 — ESP32 Serial Protocol (minimal):
```
Command format:  MOVE,<joint_id>,<angle_degrees>
Response:        OK,<joint_id>,<actual_angle>
Homing:          HOME,<joint_id>
Emergency stop:  STOP
```

**STAGE GATE 3: Only buy remaining 5 joint hardware after this one passes all Day 45 tests.**

---

## PHASE 7 — BUILD PHYSICAL ARM
### Days 46–55

| Day | Topic | Milestone |
|-----|-------|-----------|
| 46 | Base (J1) | Base rotation working |
| 47 | Shoulder (J2) | Main lifting joint |
| 48 | Elbow (J3) | 3-axis structure |
| 49 | Electronics (J1-J3) | 3-joint coordinated control |
| 50 | ROS control J1-J3 | Half-arm responds to ROS commands |
| 51 | Wrist pitch (J4) | Wrist assembly |
| 52 | Wrist roll/yaw (J5/J6) | Full orientation |
| 53 | Gripper | End effector open/close |
| 54 | Cable management | Safe, reliable wiring |
| 55 | Full joint test | Every joint moves individually |

---

## PHASE 8 — FINAL INTEGRATION
### Days 56–60: MoveIt → Real Arm

| Day | Topic | Deliverable |
|-----|-------|-------------|
| 56 | Hardware interface plugin | `devotics_hw_interface` connects ros2_control to ESP32 |
| 57 | Joint calibration | URDF limits match physical limits |
| 58 | MoveIt Plan+Execute on real arm | First automated movement |
| 59 | Pick-and-place demo | Known cube position picked and placed |
| 60 | Validation + documentation | Full test suite + project docs |

#### Day 56 — Hardware Interface Structure:
```
src/devotics_hw_interface/
├── include/devotics_hw_interface/
│   └── devotics_hw_interface.hpp
├── src/
│   └── devotics_hw_interface.cpp
├── CMakeLists.txt
└── package.xml
```

Key class inherits `hardware_interface::SystemInterface`.
Overrides: `on_init()`, `read()`, `write()`.
`write()` sends serial commands to ESP32. `read()` receives joint state feedback.

---

## Final Acceptance Criteria (V1 Complete)

| Requirement | Status |
|-------------|--------|
| URDF/Xacro model | 🔄 |
| RViz visualization | ✅ (Day 3) |
| Correct TF tree | 🔄 (Day 5) |
| MoveIt configuration | ⬜ |
| Motion planning | ⬜ |
| ros2_control | ⬜ |
| Physical arm | ⬜ |
| Homing | ⬜ |
| Joint limits | 🔄 (Day 10) |
| Gripper | ⬜ |
| Real joint calibration | ⬜ |
| MoveIt → real arm | ⬜ |
| Emergency stop | ⬜ |
| Pick-and-place demo | ⬜ |
| BOM | ⬜ |
| Wiring diagram | ⬜ |
| CAD/STL files | ⬜ |
| Software repository | ✅ (github pushed) |
| Assembly documentation | ⬜ |
| Test results | ⬜ |

---

## After V1 — Optional Phase (Week 13+)

Only after reliable pick-and-place:
1. Camera → ROS image → OpenCV → detect cube position
2. Coordinate transformation → camera frame → robot frame via TF
3. Vision-guided pick → camera sees cube → MoveIt picks automatically
4. YOLO / AI grasp → unstructured pick (not Day 60 scope)

---

## Spending Plan (Enforced by Stage Gates)

| Phase | Hardware Budget |
|-------|----------------|
| Days 1-30 | NPR 0 — software/simulation only |
| Days 31-35 | Engineering calculations + BOM only |
| Days 36-45 | ONE joint hardware only |
| Days 46-55 | Remaining arm hardware (only if Stage Gate 3 passed) |

---

## Quick Reference Commands

```bash
# Build and source
colcon build --packages-select devotics_arm_description
source install/setup.bash

# Launch arm in RViz
ros2 launch devotics_arm_description display.launch.py

# TF inspection
ros2 topic echo /tf
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo base_link wrist3_link

# Xacro check
ros2 run xacro xacro urdf/devotics_arm.urdf.xacro

# Controller check
ros2 control list_controllers

# Daily commit
git add -A && git commit -m "Day X: <what you built>"
git push origin main
```
