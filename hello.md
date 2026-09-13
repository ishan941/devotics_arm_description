# Devotics Robotic Arm Engineering Course
## Day 4 — Joint Axes, Origins and Coordinate Frames

---

## 1. Objective

The objective of Day 4 was to understand how joint rotation, joint position, visible geometry, and coordinate frames work inside URDF and ROS 2.

The main concepts learned were:

- X, Y and Z axes
- Joint axis
- Positive and negative rotation direction
- Joint origin
- Visual origin
- Local coordinate frames
- TF transformations
- Relationship between links and joints

The most important Day 4 concept is:

axis xyz
=
Which axis does the joint rotate around?

joint origin xyz
=
Where is the joint located?

visual origin xyz
=
Where is the visible shape drawn?

TF
=
Where is one link relative to another?

---

# 2. Starting Robot

Day 4 started from the working Day 3 robotic arm.

Robot structure:

base_link
    |
  joint1
    |
shoulder_link
    |
  joint2
    |
upper_arm_link
    |
  joint3
    |
forearm_link

The robot currently contains:

4 Links
3 Revolute Joints
3 Degrees of Freedom

Joint roles:

Joint 1 = Base Rotation
Joint 2 = Shoulder Movement
Joint 3 = Elbow Movement

---

# 3. Backup the Day 3 Model

Before experimenting with the URDF file, a backup of the working Day 3 model was created.

Command:

cp ~/ros2_ws/src/devotics_arm_description/urdf/devotics_arm.urdf \
~/ros2_ws/src/devotics_arm_description/urdf/devotics_arm_day3_backup.urdf

This allows us to restore the previous working model if anything goes wrong.

---

# 4. Understanding the Coordinate System

ROS uses a 3D coordinate system.

Basic representation:

            Z
            ^
            |
            |
            o------> X
           /
          /
         Y

The three axes are:

X = Horizontal direction
Y = Horizontal direction
Z = Vertical direction

Every link in the robot has its own local coordinate frame.

For example:

base_link
    → own X, Y, Z

shoulder_link
    → own X, Y, Z

upper_arm_link
    → own X, Y, Z

forearm_link
    → own X, Y, Z

Therefore, a robotic arm does not have only one XYZ coordinate system.

Each link has its own frame.

---

# 5. Joint Axis

The URDF axis parameter defines the axis around which a joint rotates.

Example:

<axis xyz="1 0 0"/>

Means:

Rotate around X-axis.

Example:

<axis xyz="0 1 0"/>

Means:

Rotate around Y-axis.

Example:

<axis xyz="0 0 1"/>

Means:

Rotate around Z-axis.

Summary:

1 0 0 = X-axis rotation

0 1 0 = Y-axis rotation

0 0 1 = Z-axis rotation

---

# 6. Experiment 1 — Changing Joint 1 Axis

Joint 1 originally had:

<axis xyz="0 0 1"/>

This means Joint 1 rotates around the Z-axis.

That creates the correct base rotation.

Concept:

        ARM
         |
         |
        BASE

        ↺ ↻

The entire upper robot rotates around the vertical axis.

---

## Testing X-Axis Rotation

Joint 1 was temporarily changed from:

<axis xyz="0 0 1"/>

to:

<axis xyz="1 0 0"/>

Then the package was rebuilt:

cd ~/ros2_ws

colcon build --symlink-install --packages-select devotics_arm_description

source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash

ros2 launch devotics_arm_description display.launch.py

When Joint 1 was moved again, the robot no longer rotated normally around the base.

Instead, the upper structure tilted around the X-axis.

This demonstrated that:

<axis xyz="1 0 0"/>

means:

Rotate around X.

After the experiment, Joint 1 was restored to:

<axis xyz="0 0 1"/>

---

# 7. Positive and Negative Axis Direction

The sign of the axis also controls the positive direction of rotation.

For example:

<axis xyz="0 1 0"/>

and:

<axis xyz="0 -1 0"/>

both rotate around the Y-axis.

However, the positive rotational direction is reversed.

---

## Experiment 2 — Reverse Joint 2 Direction

Joint 2 originally had:

<axis xyz="0 1 0"/>

It was temporarily changed to:

<axis xyz="0 -1 0"/>

After rebuilding and moving the same slider in the same direction, Joint 2 moved in the opposite direction.

Therefore:

0 1 0
=
Y-axis, one positive rotational direction

0 -1 0
=
Y-axis, opposite positive rotational direction

This will become important when controlling real motors.

If a physical motor rotates opposite to the expected ROS direction, we need to check:

- URDF joint axis
- Motor direction
- Encoder direction
- Controller configuration

After testing, Joint 2 was restored to:

<axis xyz="0 1 0"/>

---

# 8. Understanding Joint Origin

A joint origin defines where the joint is located relative to its parent link.

Joint 3 contains:

<origin xyz="0 0 0.30" rpy="0 0 0"/>

This means:

X = 0 m
Y = 0 m
Z = 0.30 m

Joint 3 is therefore located 30 cm along the Z-axis from its parent frame.

The parent of Joint 3 is:

upper_arm_link

The child is:

forearm_link

So the structure is:

upper_arm_link
      |
      | 0.30 m
      |
    joint3
      |
forearm_link

Since the upper arm is 0.30 m long, the elbow is placed at the end of the upper arm.

---

# 9. Experiment 3 — Moving the Elbow Position

Joint 3 originally had:

<origin xyz="0 0 0.30" rpy="0 0 0"/>

It was temporarily changed to:

<origin xyz="0 0 0.15" rpy="0 0 0"/>

Now Joint 3 was only:

0.15 m
=
15 cm

from the upper_arm_link frame.

After rebuilding and launching the robot, the elbow appeared approximately halfway along the upper arm instead of at its end.

This demonstrated:

joint origin xyz
=
Where the joint is attached to the parent link.

The correct value was restored:

<origin xyz="0 0 0.30" rpy="0 0 0"/>

---

# 10. Understanding Visual Origin

A visual origin is different from a joint origin.

Inside upper_arm_link:

<visual>

    <origin xyz="0 0 0.15" rpy="0 0 0"/>

    <geometry>
        <box size="0.08 0.08 0.30"/>
    </geometry>

</visual>

The upper-arm box is:

0.30 m long

or:

30 cm long.

A box in URDF is created around its center.

If the visual origin were:

<origin xyz="0 0 0"/>

the box would extend:

15 cm below the link frame

and

15 cm above the link frame.

But we want the link frame at the bottom of the upper arm.

Therefore we move the visible box upward by half its length.

Calculation:

0.30 / 2
=
0.15 m

Therefore:

<origin xyz="0 0 0.15"/>

positions the visible geometry correctly.

Concept:

        ┌──────┐
        │      │
        │      │
        │      │
        │      │
        │      │
        └──────┘
           ●
       link frame

---

# 11. Experiment 4 — Changing Visual Origin

The upper-arm visual origin was temporarily changed from:

<origin xyz="0 0 0.15" rpy="0 0 0"/>

to:

<origin xyz="0 0 0" rpy="0 0 0"/>

After rebuilding, the visible upper-arm box moved.

However, the actual joint connection did not move.

This demonstrated the difference between:

JOINT ORIGIN

and

VISUAL ORIGIN.

Joint Origin:

Changes where the robot joint or child link is attached.

Visual Origin:

Changes where the visible object is drawn relative to its link frame.

Therefore:

joint origin
=
Kinematic structure

visual origin
=
Appearance of the geometry

The upper-arm visual origin was restored to:

<origin xyz="0 0 0.15" rpy="0 0 0"/>

---

# 12. Forearm Visual Origin

The forearm uses:

<box size="0.07 0.07 0.25"/>

Its length is:

0.25 m

Half of the length is:

0.25 / 2
=
0.125 m

Therefore the visual origin is:

<origin xyz="0 0 0.125" rpy="0 0 0"/>

This places the visible forearm geometry above its link frame.

---

# 13. Understanding RPY

URDF uses:

rpy

for orientation.

RPY means:

R = Roll
P = Pitch
Y = Yaw

Approximately:

Roll
=
Rotation around X

Pitch
=
Rotation around Y

Yaw
=
Rotation around Z

Example:

rpy="0 0 0"

means:

No initial rotation.

Example:

rpy="0 1.57 0"

means approximately:

90° rotation around the Y-axis.

ROS normally uses radians.

Important values:

1.57 rad ≈ 90°

3.14 rad ≈ 180°

---

# 14. Joint Origin vs Visual Origin

This was one of the most important concepts of Day 4.

Example:

<joint name="joint3">

    <origin xyz="0 0 0.30"/>

</joint>

This means:

Place Joint 3 at this position relative to its parent.

But:

<link name="upper_arm_link">

    <visual>

        <origin xyz="0 0 0.15"/>

    </visual>

</link>

means:

Draw the visible upper-arm geometry at this offset from the link frame.

Therefore:

JOINT ORIGIN
=
Changes robot structure.

VISUAL ORIGIN
=
Changes visible geometry.

---

# 15. Understanding Local Coordinate Frames

Every link has its own coordinate frame.

For example:

base_link
    |
    | X Y Z
    |
shoulder_link
    |
    | X Y Z
    |
upper_arm_link
    |
    | X Y Z
    |
forearm_link
    |
    | X Y Z

When Joint 2 rotates, upper_arm_link rotates.

Its local coordinate frame also rotates.

All child links below it are affected.

Example:

base_link
    ↓
joint1
    ↓
shoulder_link
    ↓
joint2
    ↓
upper_arm_link
    ↓
joint3
    ↓
forearm_link

If Joint 1 moves:

shoulder_link
upper_arm_link
forearm_link

all move.

If Joint 2 moves:

upper_arm_link
forearm_link

move.

If Joint 3 moves:

forearm_link

moves.

This is the robot's kinematic chain.

---

# 16. Visualizing TF in RViz

TF was added inside RViz.

Steps:

Add
↓
TF
↓
OK

The following coordinate frames could be observed:

base_link

shoulder_link

upper_arm_link

forearm_link

When the joints were moved, the corresponding coordinate frames also moved.

This shows that TF continuously tracks the position and orientation of robot links.

---

# 17. Understanding TF

TF allows ROS to answer questions such as:

Where is forearm_link relative to base_link?

or:

Where is gripper_link relative to base_link?

The relationship can include:

Translation

X
Y
Z

and:

Rotation

orientation

TF is extremely important for:

- Robotic arms
- Cameras
- LiDAR
- Mobile robots
- MoveIt
- Object detection
- Coordinate conversion
- Robot manipulation

---

# 18. Inspecting TF from the Terminal

The robot was kept running.

A second terminal was opened.

ROS was sourced:

source /opt/ros/jazzy/setup.bash

source ~/ros2_ws/install/setup.bash

Then:

ros2 run tf2_ros tf2_echo base_link forearm_link

ROS displayed information similar to:

Translation:

x: ...
y: ...
z: ...

Rotation:

x: ...
y: ...
z: ...
w: ...

When Joint 1, Joint 2 or Joint 3 was moved, the values changed.

This means ROS continuously knows:

Where is forearm_link relative to base_link?

---

# 19. ROS Data Flow

The complete Day 4 flow is:

Joint State Publisher GUI
          |
          ↓
     /joint_states
          |
          ↓
robot_state_publisher
          |
          ↓
         /tf
          |
          ↓
        RViz
          |
          ↓
3D robot visualization

Joint State Publisher GUI provides joint angles.

robot_state_publisher combines:

URDF
+
Joint States

and calculates the coordinate transformations.

TF publishes those transformations.

RViz displays them.

---

# 20. Understanding a Complete Joint Definition

Example:

<joint name="joint3" type="revolute">

    <parent link="upper_arm_link"/>

    <child link="forearm_link"/>

    <origin xyz="0 0 0.30"
            rpy="0 0 0"/>

    <axis xyz="0 1 0"/>

</joint>

This can be understood in normal English as:

Start from upper_arm_link

↓

Go 30 cm along the Z-axis

↓

Create Joint 3 there

↓

Keep the initial orientation unchanged

↓

Allow rotation around the Y-axis

↓

Attach forearm_link

Therefore:

origin xyz
=
WHERE?

origin rpy
=
INITIAL ORIENTATION?

axis xyz
=
ROTATE AROUND WHICH AXIS?

joint value
=
HOW MUCH ROTATION?

---

# 21. Correct Final Day 4 Configuration

After completing all experiments, the original correct values were restored.

Joint 1:

<axis xyz="0 0 1"/>

Meaning:

Base rotates around Z.

---

Joint 2:

<axis xyz="0 1 0"/>

Meaning:

Shoulder rotates around Y.

---

Joint 3:

<origin xyz="0 0 0.30" rpy="0 0 0"/>

<axis xyz="0 1 0"/>

Meaning:

Elbow is positioned 30 cm from the upper-arm frame and rotates around Y.

---

Upper Arm Visual:

<origin xyz="0 0 0.15" rpy="0 0 0"/>

Meaning:

The 30 cm upper-arm box is shifted upward by 15 cm so its bottom aligns with the link frame.

---

Forearm Visual:

<origin xyz="0 0 0.125" rpy="0 0 0"/>

Meaning:

The 25 cm forearm box is shifted upward by 12.5 cm.

---

# 22. Final Build

After restoring the correct configuration:

cd ~/ros2_ws

colcon build --symlink-install --packages-select devotics_arm_description

source /opt/ros/jazzy/setup.bash

source ~/ros2_ws/install/setup.bash

ros2 launch devotics_arm_description display.launch.py

The robot was checked again to ensure:

Joint 1 works correctly.

Joint 2 works correctly.

Joint 3 works correctly.

The robot structure appears correctly in RViz.

TF frames appear correctly.

---

# 23. Day 4 Key Learning

The four most important concepts learned were:

1. axis xyz

Defines which axis a joint rotates around.

Example:

1 0 0 = X

0 1 0 = Y

0 0 1 = Z

---

2. Joint Origin

Defines where a joint is attached relative to its parent link.

Example:

<origin xyz="0 0 0.30"/>

means:

Place the joint 30 cm along Z from the parent frame.

---

3. Visual Origin

Defines where the visible geometry is drawn relative to the link frame.

It does not directly change the kinematic connection.

---

4. TF

Tracks where every link frame is located relative to other frames.

Example:

base_link
↓
shoulder_link
↓
upper_arm_link
↓
forearm_link

---

# 24. Day 4 Final Mental Model

Remember:

axis xyz
=
WHICH AXIS?

joint origin xyz
=
WHERE IS THE JOINT?

visual origin xyz
=
WHERE IS THE SHAPE?

origin rpy
=
WHAT IS THE INITIAL ORIENTATION?

joint angle
=
HOW MUCH DOES IT ROTATE?

TF
=
WHERE IS ONE LINK RELATIVE TO ANOTHER?

---

# 25. Day 4 Result

At the end of Day 4, the following concepts were understood:

X/Y/Z coordinate axes ✅

Joint axis ✅

Positive and negative axis direction ✅

Joint origin ✅

Visual origin ✅

Roll, Pitch and Yaw ✅

Local coordinate frames ✅

TF visualization ✅

tf2_echo ✅

Kinematic hierarchy ✅

URDF joint interpretation ✅

---

# Day 4 Status

COMPLETED

Devotics Robotic Arm
Joint Axes, Origins and Coordinate Frames

---

# Next — Day 5

Day 5 will focus on:

TF Tree and Transformations

The robot structure will remain:

base_link
    ↓
shoulder_link
    ↓
upper_arm_link
    ↓
forearm_link

The goal will be to understand:

How does ROS know where the end of the robotic arm is?

We will study:

- TF tree
- Parent and child frames
- Translation
- Rotation
- base_link to forearm_link transformation
- Static and dynamic transforms
- Forward kinematics concept

This will prepare the Devotics robotic arm for later MoveIt motion planning.

