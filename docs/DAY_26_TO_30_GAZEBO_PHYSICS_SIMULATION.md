# Devotics Robotic Arm V1 — Engineering Build Log (Days 26 to 30)

**Packages:** `devotics_arm_description`, `devotics_arm_moveit_config`  
**ROS 2 Distribution:** Jazzy / Ubuntu 24.04 (arm64)  
**Branch:** `P-4`  
**Topic:** Phase 4 — Gazebo Harmonic Physics Simulation, Inertia Modeling, and Workstation Environments  
**Target:** Realistic Rigid-Body Dynamics, Joint Holding Torques, and SDF Scene Creation  

---

## 📌 Executive Summary
In Phase 4, the Devotics Arm transitioned from purely kinematic visualization into a **fully simulated physical entity** subject to gravity ($-9.81\text{ m/s}^2$), inertia tensors, motor control, and contact friction.

We:
1. Installed and configured **Gazebo Sim Harmonic (v8.11.0)** via `ros-jazzy-ros-gz`.
2. Formulated and embedded parametric **3D inertia tensors (`<inertial>`)** for all 10 links.
3. Created an automated model spawner pipeline in [`launch/gazebo.launch.py`](file:///home/ishan/ros2_ws/src/devotics_arm_description/launch/gazebo.launch.py).
4. Solved the "toppling arm" collapse by introducing a static `world` anchor.
5. Implemented the **dual-mode hardware architecture** (`sim_mode:=true/false`) using `gz_ros2_control` and bridged `/clock`.
6. Designed and loaded an SDF workstation environment ([`worlds/table_cube.sdf`](file:///home/ishan/ros2_ws/src/devotics_arm_description/worlds/table_cube.sdf)) equipped with a table and friction-enabled target cube.

---

## 🏗️ Architecture Overview

```
                        Gazebo Harmonic (gz_sim)
             ┌──────────────────────────────────────────────┐
             │ World: table_cube.sdf                        │
             │   ├── Physics Engine (ODE 1ms step)          │
             │   ├── Work Table & Target Cube               │
             │   └── devotics_arm (Spawned via /robot_desc) │
             │         └── gz_ros2_control Plugin           │
             └──────────────────────┬───────────────────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            │                                               │
            ▼ (/clock)                                      ▼ (/joint_states)
     [ros_gz_bridge]                               [controller_manager]
            │                                       ├── devotics_arm_controller
            ▼                                       └── gripper_controller
    ROS 2 Sim Time Sync                                     ▲
                                                            │ (FollowJointTrajectory)
                                                            │
                                              [scripts/pick_and_place.py]
```

---

## 🛠️ Step-by-Step Implementation

### 1. Mathematical Inertia Modeling ([`urdf/devotics_arm.urdf.xacro`](file:///home/ishan/ros2_ws/src/devotics_arm_description/urdf/devotics_arm.urdf.xacro))
Solid body inertia tensors were calculated using closed-form analytical formulas embedded as Xacro macros:

* **Cylinder Inertia ($r, l, m$):**
  $$I_{xx} = I_{yy} = \frac{m(3r^2 + l^2)}{12}, \quad I_{zz} = \frac{m \cdot r^2}{2}$$
* **Box Inertia ($x, y, z, m$):**
  $$I_{xx} = \frac{m(y^2 + z^2)}{12}, \quad I_{yy} = \frac{m(x^2 + z^2)}{12}, \quad I_{zz} = \frac{m(x^2 + y^2)}{12}$$

Mass distribution assigned:
* `base_link`: $2.5\text{ kg}$ (Counterweight base)
* `shoulder_link`: $1.2\text{ kg}$ (Motor bracket & J1/J2 actuators)
* `upper_arm_link`: $0.9\text{ kg}$
* `forearm_link`: $0.7\text{ kg}$
* `wrist1_link` & `wrist2_link`: $0.3\text{ kg}$ & $0.25\text{ kg}$
* `wrist3_link`: $0.15\text{ kg}$
* `gripper_base_link`: $0.2\text{ kg}$
* `left_finger_link` & `right_finger_link`: $0.05\text{ kg}$ each

### 2. Dual-Mode Hardware Interface ([`urdf/devotics_arm.ros2_control.xacro`](file:///home/ishan/ros2_ws/src/devotics_arm_description/urdf/devotics_arm.ros2_control.xacro))
To avoid breaking the RViz mock pipeline while supporting Gazebo, we introduced a conditional macro switch:

```xml
<hardware>
  <xacro:if value="${sim_mode}">
    <plugin>gz_ros2_control/GazeboSimSystem</plugin>
  </xacro:if>
  <xacro:unless value="${sim_mode}">
    <plugin>mock_components/GenericSystem</plugin>
  </xacro:unless>
</hardware>
```

### 3. The Workstation World ([`worlds/table_cube.sdf`](file:///home/ishan/ros2_ws/src/devotics_arm_description/worlds/table_cube.sdf))
Constructed an SDF world containing:
* **Physics Settings**: 1 ms step size ($1000\text{ Hz}$).
* **Work Table**: Static box ($0.30 \times 0.35 \times 0.25\text{ m}$) at $X = 0.35\text{ m}$.
* **Target Cube**: Dynamic red box ($30\text{ mm}$ side, $50\text{ g}$) with friction coefficient $\mu = 1.5$.

---

## ⚠️ Obstacles, Mistakes & How We Tackled Them

### Obstacle 1: The "Toppling Arm" Collapse
* **The Symptom:** Upon first spawn into Gazebo, the arm instantly tipped sideways and fell limply onto the ground plane.
* **The Root Cause:** In URDF, `base_link` was free-floating. In gravity, the cantilevered arm exerted a torque that flipped the unanchored base over. Additionally, KDL parser warned that root links cannot have inertia.
* **How We Tackled It:** Defined an unmovable `world` frame and bolted the base down:
  ```xml
  <link name="world"/>
  <joint name="world_to_base_joint" type="fixed">
      <parent link="world"/>
      <child link="base_link"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>
  ```
  Immediately afterward, the robot stood rock-solid and upright.

### Obstacle 2: `InvalidPythonLaunchFileError` on Empty File
* **The Symptom:** Running `ros2 launch devotics_arm_description gazebo.launch.py` failed with:
  `launch file does not contain the required function 'generate_launch_description()'`.
* **The Root Cause:** The launch script had been created as a 0-byte blank file before saving the code.
* **How We Tackled It:** Populated the complete launch description with `robot_state_publisher`, `ros_gz_sim create`, `ros_gz_bridge`, and controller spawners.

### Obstacle 3: URDF vs SDF Format Confusion
* **The Question:** Why create `.sdf` files when we already have `.urdf` and `.xacro`?
* **The Core Distinction:**
  * **URDF**: A ROS-specific format that only describes a single robotic kinematic chain.
  * **SDF (Simulation Description Format)**: A physics-engine format (Gazebo) that describes entire multi-object worlds, lighting, skies, friction coefficients ($\mu$), and physics solver properties.

---

## ✅ Phase 4 Pass Criteria Met
1. `gz sim --version` verifies Gazebo Sim v8.11.0 (Harmonic).
2. Arm spawns without KDL warnings or physics explosions.
3. `ros2 control list_controllers` inside Gazebo shows all controllers `active`.
4. Robot stands upright in gravity and executes multi-joint motions in the table and cube world.
