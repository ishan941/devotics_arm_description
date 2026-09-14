#!/usr/bin/env python3
"""
Day 12: Inverse Kinematics (IK) Intuition Script for Devotics Arm
Demonstrates how 2-link planar IK works mathematically.
"""
import math

# Link lengths of Devotics Arm (Upper arm & Forearm)
L1 = 0.30  # upper_arm_length (meters)
L2 = 0.25  # forearm_length (meters)

def solve_ik_2d(target_x, target_z):
    """
    Solves Inverse Kinematics for a 2-link planar arm in the (X, Z) plane.
    Returns two possible solutions: Elbow Up and Elbow Down.
    """
    # Distance from shoulder to target
    d_sq = target_x**2 + target_z**2
    d = math.sqrt(d_sq)

    # 1. Check reachability
    max_reach = L1 + L2
    min_reach = abs(L1 - L2)
    if d > max_reach:
        return None, f"Target ({target_x:.2f}, {target_z:.2f}) is OUT OF REACH! Max reach is {max_reach:.2f} m, distance is {d:.2f} m"
    if d < min_reach:
        return None, f"Target is too close to the body (inside self-collision zone)."

    # 2. Law of Cosines to find Elbow angle (theta2)
    cos_theta2 = (d_sq - L1**2 - L2**2) / (2 * L1 * L2)
    # Clamp to [-1, 1] for numerical stability
    cos_theta2 = max(-1.0, min(1.0, cos_theta2))

    # Two solutions for elbow: positive (elbow down) and negative (elbow up)
    theta2_sol1 = math.acos(cos_theta2)
    theta2_sol2 = -math.acos(cos_theta2)

    # 3. Shoulder angle (theta1) for each elbow solution
    # beta = angle from base to target
    beta = math.atan2(target_z, target_x)
    
    # alpha = angle between L1 and target line
    cos_alpha = (d_sq + L1**2 - L2**2) / (2 * d * L1)
    cos_alpha = max(-1.0, min(1.0, cos_alpha))
    alpha = math.acos(cos_alpha)

    theta1_sol1 = beta - alpha
    theta1_sol2 = beta + alpha

    return {
        "solution_1 (Elbow Down)": {
            "shoulder_deg": math.degrees(theta1_sol1),
            "elbow_deg": math.degrees(theta2_sol1)
        },
        "solution_2 (Elbow Up)": {
            "shoulder_deg": math.degrees(theta1_sol2),
            "elbow_deg": math.degrees(theta2_sol2)
        }
    }, None

if __name__ == "__main__":
    print("=" * 60)
    print("  DEVOTICS ARM: INVERSE KINEMATICS (IK) DEMONSTRATION")
    print(f"  Arm Link 1 (Upper Arm): {L1} m | Link 2 (Forearm): {L2} m")
    print("=" * 60)

    test_targets = [
        (0.35, 0.20),   # Reachable comfortable target
        (0.50, 0.10),   # Near full extension
        (0.70, 0.20),   # Out of reach target
    ]

    for tx, tz in test_targets:
        print(f"\n🎯 Target Cartesian Goal: X = {tx:.2f} m, Z = {tz:.2f} m")
        sols, err = solve_ik_2d(tx, tz)
        if err:
            print(f"   ❌ {err}")
        else:
            for name, angles in sols.items():
                print(f"   ✅ {name}:")
                print(f"      Shoulder = {angles['shoulder_deg']:.1f}° | Elbow = {angles['elbow_deg']:.1f}°")
    print("\n" + "=" * 60)
