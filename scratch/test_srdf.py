import os
import yaml
import xacro

pkg_dir = '/home/ishan/ros2_ws/src/devotics_arm_description'
urdf_file = os.path.join(pkg_dir, 'urdf', 'devotics_arm_v0.urdf.xacro')
srdf_text = """<?xml version="1.0" encoding="UTF-8"?>
<robot name="devotics_arm_v0">
  <group name="arm_v0">
    <joint name="base_joint"/>
    <joint name="shoulder_joint"/>
    <joint name="elbow_joint"/>
    <chain base_link="base_link" tip_link="forearm_link"/>
  </group>

  <group name="gripper_v0">
    <joint name="gripper_joint"/>
    <link name="gripper_link"/>
    <link name="tool0"/>
  </group>

  <end_effector name="v0_gripper" parent_link="forearm_link" group="gripper_v0" parent_group="arm_v0"/>

  <group_state name="home" group="arm_v0">
    <joint name="base_joint"     value="0.0"/>
    <joint name="shoulder_joint" value="0.0"/>
    <joint name="elbow_joint"    value="0.0"/>
  </group_state>

  <group_state name="ready" group="arm_v0">
    <joint name="base_joint"     value="0.0"/>
    <joint name="shoulder_joint" value="0.54"/>
    <joint name="elbow_joint"    value="0.65"/>
  </group_state>

  <group_state name="pick_ready" group="arm_v0">
    <joint name="base_joint"     value="-0.46"/>
    <joint name="shoulder_joint" value="0.42"/>
    <joint name="elbow_joint"    value="1.28"/>
  </group_state>

  <group_state name="place_ready" group="arm_v0">
    <joint name="base_joint"     value="0.46"/>
    <joint name="shoulder_joint" value="0.42"/>
    <joint name="elbow_joint"    value="1.28"/>
  </group_state>

  <group_state name="open" group="gripper_v0">
    <joint name="gripper_joint" value="0.35"/>
  </group_state>

  <group_state name="close" group="gripper_v0">
    <joint name="gripper_joint" value="-0.52"/>
  </group_state>

  <disable_collisions link1="base_link"           link2="base_rotating_link" reason="Adjacent"/>
  <disable_collisions link1="base_rotating_link"  link2="upper_arm_link"     reason="Adjacent"/>
  <disable_collisions link1="upper_arm_link"      link2="forearm_link"       reason="Adjacent"/>
  <disable_collisions link1="forearm_link"        link2="gripper_link"       reason="Adjacent"/>
  <disable_collisions link1="base_link"           link2="upper_arm_link"     reason="Never"/>
</robot>
"""

with open('/tmp/test_srdf.srdf', 'w') as f:
    f.write(srdf_text)

print("Test SRDF written")
