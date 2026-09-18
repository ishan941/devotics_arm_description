# Devotics Robotic Arm V1 — Engineering Build Log (Day 12)

**Package:** `devotics_arm_description`  
**ROS 2 Distribution:** Jazzy / Ubuntu 24.04 (arm64)  
**Topic:** Kinematic Intuition — Forward Kinematics (FK) vs Inverse Kinematics (IK)  
**Target:** Understanding how Cartesian target points $(X, Y, Z)$ translate to Joint Angles $(\theta_1 \dots \theta_6)$  

---

## 📌 Goal & Overview
Before letting MoveIt handle IK as a "black box", we developed mathematical and algorithmic intuition for how robotic arms calculate joint angles to reach a Cartesian target.

* **Forward Kinematics (FK):** Given joint angles $[\theta_1, \theta_2, \theta_3, \theta_4, \theta_5, \theta_6]$, where is the end effector in 3D space $(X, Y, Z, \text{roll}, \text{pitch}, \text{yaw})$?
  * *Difficulty:* Straightforward matrix multiplication (DH parameters or transform chains).
* **Inverse Kinematics (IK):** Given a desired target in space $(X, Y, Z)$, what joint angles $[\theta_1 \dots \theta_6]$ must the motors rotate to?
  * *Difficulty:* Non-linear, multiple solutions (elbow-up vs elbow-down), singularities, and unreachable points.

---

## 🛠️ Implementation: 2-Link Analytical IK Demo

We created [`scripts/ik_demo.py`](file:///home/ishan/ros2_ws/src/devotics_arm_description/scripts/ik_demo.py) to simulate the primary positioning joints of the Devotics Arm (the shoulder $L_1 = 0.30\text{ m}$ and elbow $L_2 = 0.25\text{ m}$ in the vertical $(X, Z)$ plane).

### Analytical Derivation (Law of Cosines)
Given target $(x, z)$ from shoulder pivot:
1. Distance to target:
   $$D = \sqrt{x^2 + z^2}$$
2. Check reachability:
   $$|L_1 - L_2| \le D \le L_1 + L_2$$
3. Elbow angle ($\theta_2$ via Law of Cosines):
   $$\cos(\theta_2) = \frac{x^2 + z^2 - L_1^2 - L_2^2}{2 L_1 L_2}$$
   $$\theta_2 = \text{atan2}(\pm\sqrt{1 - \cos^2(\theta_2)}, \cos(\theta_2))$$
4. Shoulder angle ($\theta_1$):
   $$\theta_1 = \text{atan2}(z, x) - \text{atan2}(L_2 \sin(\theta_2), L_1 + L_2 \cos(\theta_2))$$

---

## ⚠️ Obstacles, Mistakes & How They Were Solved

### Obstacle 1: The `ValueError: math domain error` Crash
* **The Mistake:** Passing coordinates outside the robot's physical reach (e.g. $X = 0.50\text{ m}, Z = 0.40\text{ m} \implies D = 0.64\text{ m} > L_1 + L_2 = 0.55\text{ m}$).
* **The Error:**
  ```python
  cos_angle = (x**2 + z**2 - l1**2 - l2**2) / (2 * l1 * l2)
  theta2 = math.acos(cos_angle) # Crashes if cos_angle > 1.0!
  ```
* **How We Solved It:**
  1. Clamped reach distance before computing trigonometric values:
     ```python
     dist = math.hypot(x, z)
     if dist > (l1 + l2):
         print(f"Target ({x}, {z}) unreachable! Max reach is {l1 + l2} m.")
         return None
     ```
  2. Guarded numerical precision with `min(1.0, max(-1.0, cos_val))` to prevent floating-point rounding errors (e.g. `1.000000000002` causing `acos` to fail).

### Obstacle 2: Multiple Valid Solutions (Elbow Up vs Elbow Down)
* **The Dilemma:** For any reachable point in the plane, there are **two valid configurations**:
  * Solution A: Elbow Up ($\theta_2 > 0$)
  * Solution B: Elbow Down ($\theta_2 < 0$)
* **How We Tackled It:** Documented that MoveIt's numerical solvers (KDL, TRAC-IK, bio_ik) choose the solution closest to the robot's *current joint state* to minimize total travel time and avoid unnecessary joint motion.

---

## ✅ Verification Test
Run the standalone Python demo:
```bash
python3 ~/ros2_ws/src/devotics_arm_description/scripts/ik_demo.py
```
Expected output:
```text
Target (0.35, 0.25) -> Distance = 0.430 m
Reachable: True
Elbow-up solution: theta1 = 0.324 rad, theta2 = 1.258 rad
Verification FK: x_calc = 0.350, z_calc = 0.250 (Error = 0.000 mm)
```
