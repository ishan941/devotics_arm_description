Devotics Robotic Arm Engineering Course

Final System
The final architecture will look approximately like this:
                    DEVOTICS ARM V1
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
              Hardware Interface
                         │
                    USB Serial
                         │
                         ↓
                       ESP32
                         │
                ┌────────┼────────┐
                ↓        ↓        ↓
             Drivers   Drivers   Drivers
                ↓        ↓        ↓
             J1 J2     J3 J4     J5 J6
                         │
                      Gripper
The PC will calculate trajectories. The ESP32 should not calculate MoveIt paths or depend on Wi-Fi for precise motor timing. Its job will be lower-level control: motor commands, homing, limits, feedback and safety.
For V1, we will use USB serial first because it is simpler and more reliable for a bench prototype than Wi-Fi. CAN/RS485 can be considered later.

Course Duration
12 weeks
5 learning/build days per week
60 total days
You have already completed:
Day 1 ✅
Day 2 ✅
Most days:
Theory              20–30 min
Practical work      60–90 min
Documentation       10–15 min
────────────────────────────
Total               ~1.5–2 hr
Mechanical assembly/testing days may require 2–3 hours.
Expected total effort is roughly 90–120 hours, depending mainly on mechanical debugging and hardware availability.

PHASE 1 — ROS ROBOT FUNDAMENTALS
Week 1 — From One Joint to a Real Arm Structure


Day
Topic
Practical Work
Result
Day 1 
ROS 2, RViz, MoveIt introduction
Installed/verified tools
Development environment ready
Day 2 
URDF, links, joints, TF
Built 1-DOF arm
First Devotics arm moves in RViz
Day 3
3-DOF arm
Add base, shoulder and elbow
3 joint sliders
Day 4
Joint axes & coordinate frames
Experiment with X/Y/Z joint axes
Understand why joints rotate differently
Day 5
TF tree
Add TF display and inspect transforms
Understand complete link/joint hierarchy

Day 3
Turn:
Base
 │
J1
 │
Link
into:
        forearm
            │
           J3
            │
        upper_arm
            │
           J2
            │
        shoulder
            │
           J1
            │
          base
You will get:
joint1 slider
joint2 slider
joint3 slider
and manually pose the arm in RViz.
Day 4
Learn exactly what:

<axis xyz="1 0 0"/>

<axis xyz="0 1 0"/>

<axis xyz="0 0 1"/>
means.
You will deliberately change axes and watch what happens.
This will teach you more than memorizing coordinate-system theory.
Day 5
Study:
base_link
    ↓
shoulder_link
    ↓
upper_arm_link
    ↓
forearm_link
and inspect:

ros2 topic echo /tf
Milestone:
You understand how ROS represents the structure and current pose of a robotic arm.

Week 2 — Build the Complete Virtual Devotics Arm
Now we'll create the full kinematic structure before worrying about motors.

Day
Topic
Practical Work
Result
Day 6
Wrist joints
Add J4 and J5
5-DOF arm
Day 7
Wrist roll
Add J6
6-DOF arm
Day 8
Gripper
Add gripper links/joint
Complete virtual robot
Day 9
Xacro
Convert URDF into reusable Xacro
Cleaner robot description
Day 10
Joint limits & home pose
Configure realistic limits
Final V1 kinematic model

Target structure:
                gripper
                    │
                   J6
                    │
                 wrist
                    │
                   J5
                    │
                 wrist
                    │
                   J4
                    │
                forearm
                    │
                   J3
                    │
               upper arm
                    │
                   J2
                    │
                shoulder
                    │
                   J1
                    │
                  base
A six-revolute-joint arm is a useful target because it can eventually control both end-effector position and orientation.
We will still reserve the right to build 5 DOF + gripper physically if our cost/torque analysis later shows that a sixth joint gives little value for V1.
That's a hardware decision, not something we should guess today.

PHASE 2 — KINEMATICS AND MOVEIT
Week 3 — Learn How an Arm Knows Where Its Hand Is


Day
Topic
Practical Work
Result
Day 11
Forward kinematics
Change joint angles and observe XYZ
Understand FK
Day 12
Inverse kinematics
Concept + simple examples
Understand IK
Day 13
End-effector frame
Create tool/gripper frame
Correct TCP
Day 14
Workspace
Explore reachable positions
Understand robot reach
Day 15
Singularity & unreachable poses
Test problematic configurations
Understand arm limitations

You won't spend hours deriving matrices by hand.
The objective is to understand:
Forward Kinematics

Joint angles
    ↓
θ1 θ2 θ3 θ4 θ5 θ6
    ↓
Where is gripper?
    ↓
X Y Z + orientation
versus:
Inverse Kinematics

Desired gripper position
       ↓
     X Y Z
       ↓
What joint angles?
       ↓
θ1 θ2 θ3 θ4 θ5 θ6
That distinction is fundamental to MoveIt.

Week 4 — MoveIt 2
This is where the arm becomes much more intelligent.
MoveIt's Setup Assistant takes a URDF and generates additional configuration such as planning groups, end effectors, kinematics information and collision configuration.

Day
Topic
Practical Work
Result
Day 16
MoveIt demo
Use an existing robot in MoveIt
Understand Plan/Execute
Day 17
Setup Assistant
Import Devotics URDF/Xacro
Start MoveIt configuration
Day 18
Planning groups
Configure devotics_arm and gripper
MoveIt understands arm
Day 19
End effector + poses
Home, ready, pickup poses
Named robot states
Day 20
Motion planning
Plan targets in RViz
Devotics arm plans motion

MoveIt's RViz plugin lets you create target poses, calculate trajectories and inspect the planned path before execution.
By Day 20:
Drag gripper target
        ↓
      MoveIt
        ↓
     IK solver
        ↓
Collision checking
        ↓
Path planning
        ↓
      PLAN
        ↓
Virtual Devotics Arm moves
Stage Gate 1
We do not purchase complete arm hardware unless this works:
Devotics arm appears correctly in MoveIt and can plan to multiple reachable poses.

PHASE 3 — ROBOT CONTROL
Week 5 — ros2_control
Now you learn the layer between MoveIt and real motors.
ros2_control manages controllers and hardware interfaces. Its joint_trajectory_controller executes timed joint-space trajectories containing position and optionally velocity/acceleration targets.

Day
Topic
Practical Work
Result
Day 21
ros2_control concepts
Controller Manager, interfaces
Understand control stack
Day 22
URDF control tags
Add <ros2_control>
Arm becomes controllable
Day 23
Joint State Broadcaster
Configure state feedback
Joint states via controller
Day 24
Joint Trajectory Controller
Configure six joints
Trajectory execution
Day 25
MoveIt → ros2_control
Plan & Execute
Full software pipeline

Architecture becomes:
MoveIt
   ↓
FollowJointTrajectory
   ↓
JointTrajectoryController
   ↓
ros2_control
   ↓
Mock Hardware
   ↓
Joint States
   ↓
RViz
MoveIt expects trajectory controllers capable of accepting planned trajectories; the Setup Assistant can configure these interfaces.
Milestone:
MoveIt no longer simply animates the arm. It sends trajectories through the same controller structure we can later connect to hardware.

PHASE 4 — PHYSICS SIMULATION
Week 6 — Gazebo Harmonic
ROS 2 Jazzy's recommended Gazebo pairing is Gazebo Harmonic, and ROS-Gazebo bridges allow ROS topics and simulated systems to communicate.

Day
Topic
Practical Work
Result
Day 26
Gazebo installation
Install Jazzy-compatible Gazebo
Simulator runs
Day 27
Spawn robot
Devotics arm inside world
3D simulated robot
Day 28
Mass & inertia
Add physical properties
Robot affected by physics
Day 29
Controllers
Move joints in Gazebo
Controlled simulated arm
Day 30
Object interaction
Add table + cube
Simulation test environment

You will learn the difference between:
RViz
"Where ROS believes the arm is"
and:
Gazebo
"What happens to the modeled arm under physics"
Day 30 world:
┌──────────────────────────────┐
│                              │
│             🟥               │
│           object             │
│      ─────────────           │
│          table               │
│                              │
│   🤖 Devotics Arm            │
│                              │
└──────────────────────────────┘
ARM64 rule
We'll give Gazebo a fixed troubleshooting budget.
If your ARM64 VM becomes the main problem instead of robotics learning:
Gazebo → temporarily pause

RViz + MoveIt + Mock ros2_control → continue
We won't lose a week fighting simulation infrastructure.

PHASE 5 — ENGINEER THE REAL ARM
Week 7 — Mechanical Design Before Buying Motors
This is where many hobby robotic-arm projects make the biggest mistake:
Motor first → design later.
We'll do the opposite.

Day
Topic
Practical Work
Result
Day 31
Requirements
Define reach, use case, payload target
Engineering specification
Day 32
Arm geometry
Determine link lengths
Mechanical architecture
Day 33
Torque calculation
Calculate required joint torque
Motor requirements
Day 34
Transmission design
Gear/belt/direct drive comparison
Reduction strategy
Day 35
BOM and costing
Motors, drivers, bearings, PSU etc.
Purchase decision

Day 31 — Requirements
We decide things such as:
Desktop or floor mounted?
Maximum reach?
Target payload?
Desired speed?
Position accuracy?
Gripper size?
Total arm weight?
Continuous or occasional use?
We will not invent these specifications.

Day 33 — Torque
For example, shoulder torque depends approximately on:
Torque = Force × Distance
But we also need:
forearm mass
wrist mass
gripper mass
payload
link length
acceleration
gear ratio
safety margin
That calculation determines whether we need:
servo
stepper
geared stepper
BLDC
closed-loop stepper
rather than choosing motors because they look popular.

Stage Gate 2 — Hardware Purchase
Only on or after approximately Day 35 do we approve a BOM.
Before buying, we calculate:
motor cost
driver cost
bearings
shafts
belts
pulleys
fasteners
power supply
wiring
connectors
filament
limit switches
encoders if required
replacement/spares
And compare:
Complete prototype cost
vs
Learning value
vs
Expected reuse

PHASE 6 — BUILD ONE REAL JOINT
Week 8 — Physical Joint Prototype
We will not print the entire arm yet.
We'll build one demanding joint first, probably the shoulder.

Day
Topic
Practical Work
Result
Day 36
Print mechanical prototype
Joint housing/link
Mechanical joint
Day 37
Motor + driver
Bench-test actuator
Reliable rotation
Day 38
Homing
Install limit/home switch
Known zero position
Day 39
ESP32 control
Angle/steps commands
Low-level controller
Day 40
ROS → ESP32
Command joint from ROS 2
First physical ROS joint

Architecture:
ROS 2
 ↓
command: 45°
 ↓
USB serial
 ↓
ESP32
 ↓
motor driver
 ↓
motor
 ↓
gear/belt
 ↓
physical joint
Very important
The microcontroller will handle:
step timing
motor direction
homing
limit switches
emergency behavior
ROS won't generate each motor pulse remotely.

Week 9 — Validate the Joint Before Scaling

Day
Topic
Practical Work
Result
Day 41
Calibration
Compare requested/actual angle
Joint mapping
Day 42
Backlash
Direction-change testing
Backlash measured
Day 43
Thermal testing
Run repeated movement
Motor/driver validated
Day 44
Load testing
Increase controlled load
Real capability measured
Day 45
Design revision
Fix mechanical/electrical issues
Joint V2 approved

Test:
Command      Actual

0°     →     ?
30°    →     ?
60°    →     ?
90°    →     ?
60°    →     ?
30°    →     ?
0°     →     ?
This exposes:
backlash
missed steps
gear slippage
flex
calibration errors
Stage Gate 3
We don't build five more bad joints.
Only proceed if this one joint proves:
repeatable motion
acceptable temperature
sufficient torque
reliable homing
mechanical rigidity

PHASE 7 — BUILD THE PHYSICAL ARM
Week 10 — Base, Shoulder and Elbow


Day
Topic
Practical Work
Result
Day 46
Base joint
Print/assemble J1
Base rotation
Day 47
Shoulder
Assemble J2
Main lifting joint
Day 48
Elbow
Assemble J3
3-axis structure
Day 49
Electronics
Connect three actuators
3-joint controller
Day 50
ROS control
Control J1–J3 together
Half-arm works

Now we have:
     elbow
        ● J3
       /
      /
     ● J2
     │
     │
     ● J1
   ███████
     BASE
This will be a significant milestone.

Week 11 — Wrist + Gripper + Complete Mechanics


Day
Topic
Practical Work
Result
Day 51
Wrist design
J4 assembly
Wrist pitch
Day 52
Wrist orientation
J5/J6 assembly
Full orientation capability
Day 53
Gripper
Print + actuate gripper
End effector
Day 54
Cable management
Route power/signals safely
Reliable wiring
Day 55
Manual joint test
Move every joint individually
Complete physical arm

At Day 55:
           ┌──┐
            │  │ gripper
             \/
              │
            ● J6
              │
            ● J5
              │
            ● J4
             /
            /
          ● J3
         /
        /
      ● J2
      │
      │
      ● J1
   ──────────
       BASE
This is when we can legitimately call it a physical robotic arm.
But it still won't be finished.
A robot that moves manually is not yet an integrated robotics system.

PHASE 8 — CONNECT MOVEIT TO THE REAL ARM
Week 12 — Final Integration


Day
Topic
Practical Work
Result
Day 56
Hardware interface
Connect ros2_control to ESP32
ROS sees real joints
Day 57
Joint calibration
Establish zero offsets and limits
URDF matches reality
Day 58
MoveIt execution
Plan & execute on real robot
Automated movement
Day 59
Pick-and-place
Pick known cube position
Functional manipulation
Day 60
Validation & documentation
Full test + final documentation
Devotics Arm V1 complete

The final pipeline:
               RViz
                  │
            Choose Target
                  │
                  ↓
               MoveIt
                  │
        Inverse Kinematics
                  │
          Motion Planning
                  │
                  ↓
        Joint Trajectory
                  │
                  ↓
       JointTrajectoryController
                  │
                  ↓
          ros2_control
                  │
                  ↓
       Devotics Hardware Interface
                  │
                  ↓
             USB Serial
                  │
                  ↓
                ESP32
                  │
                  ↓
          Motor Controllers
                  │
                  ↓
          PHYSICAL ARM 🤖
The ros2_control Controller Manager is specifically designed to sit between ROS controllers and hardware interfaces.

Final Test — No AI Yet
The first final demonstration should be deliberately simple.
Place a cube at a known position:
                  🟥
                   cube
             ─────────────
                 table


        🤖
Sequence:
HOME
 ↓
Move above cube
 ↓
Open gripper
 ↓
Move downward
 ↓
Close gripper
 ↓
Lift cube
 ↓
Move to destination
 ↓
Lower
 ↓
Open gripper
 ↓
Return HOME
If this works repeatedly, Devotics Arm V1 is complete.
Not because it looks cool, but because the full engineering stack works.

What Counts as “Complete”
I would not call the project complete merely because the arm moves.
The final acceptance criteria are:

Requirement
Required
URDF/Xacro model
✅
RViz visualization
✅
Correct TF tree
✅
MoveIt configuration
✅
Motion planning
✅
ros2_control
✅
Physical arm
✅
Homing
✅
Joint limits
✅
Gripper
✅
Real joint calibration
✅
MoveIt → real arm
✅
Emergency stop / safe shutdown
✅
Known-position pick & place
✅
BOM
✅
Wiring diagram
✅
CAD/STL files
✅
Software repository
✅
Assembly documentation
✅
Test results
✅

That is a real engineering prototype.

After V1 — Optional Phase
Only after the arm works reliably should we add vision.
Week 13 — Camera
camera
 ↓
ROS image
 ↓
OpenCV
 ↓
detect cube
Week 14 — Coordinate Transformation
Camera coordinates
       ↓
Calibration
       ↓
TF transformation
       ↓
Robot coordinates
Then:
Camera sees cube
       ↓
Determine X,Y,Z
       ↓
MoveIt
       ↓
Arm automatically picks cube
Only later:
YOLO
AI grasp detection
object classification
voice commands
reinforcement learning
robotic hand
I specifically would not add AI before Day 60. It would increase complexity without fixing the basic manipulation problem.

Spending Plan
This course has intentional purchasing gates:
Days 1–30
NPR 0 additional robotic-arm hardware
Software + simulation

Day 31–35
Engineering calculations + BOM

Days 36–45
Buy hardware for ONE joint only

If one joint passes
        ↓
Buy remaining arm hardware

If one joint fails
        ↓
Fix design before spending more

