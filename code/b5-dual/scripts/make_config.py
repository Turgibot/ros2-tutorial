#!/usr/bin/env python3
"""Build the two-arm MoveIt config files from the single-arm ones that ship with the Kinova packages.

Run it once (it is already run, the results are in config/):
    python3 scripts/make_config.py
It reads /opt/kortex_ws/.../kinova_gen3_7dof_robotiq_2f_85_moveit_config/config and writes into ../config.
The idea of the whole lesson: every joint and link name gets a prefix, "left_" or "right_".
"""
import os
import re

SRC = ("/opt/kortex_ws/install/kinova_gen3_7dof_robotiq_2f_85_moveit_config/share/"
       "kinova_gen3_7dof_robotiq_2f_85_moveit_config/config")
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config")
SIDES = ("left", "right")
JOINTS = [f"joint_{i}" for i in range(1, 8)]


def read(name):
    with open(os.path.join(SRC, name)) as f:
        return f.read()


def write(name, text):
    with open(os.path.join(DST, name), "w") as f:
        f.write(text)
    print("wrote config/" + name)


# 1. SRDF: two groups, and the "never collide" pairs of the single arm, once per arm (no gripper in this lesson)
pairs = [l for l in read("gen3.srdf").splitlines()
         if "<disable_collisions" in l and "robotiq" not in l]
out = ['<?xml version="1.0"?>', '<robot name="dual">']
for s in SIDES:
    out.append(f'  <group name="{s}_arm">')
    out.append(f'    <chain base_link="{s}_base_link" tip_link="{s}_end_effector_link"/>')
    out.append('  </group>')
for s in SIDES:
    out.append(f'  <group_state name="Vertical" group="{s}_arm">')
    out += [f'    <joint name="{s}_{j}" value="0"/>' for j in JOINTS]
    out.append('  </group_state>')
for s in SIDES:
    for l in pairs:
        out.append(re.sub(r'link([12])="(\w+)"', lambda m: f'link{m.group(1)}="{s}_{m.group(2)}"', l.rstrip()))
out.append('</robot>')
write("dual.srdf", "\n".join(out) + "\n")

# 2. kinematics: one KDL solver per group
write("kinematics.yaml", "".join(
    f"{s}_arm:\n  kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin\n"
    "  kinematics_solver_search_resolution: 0.005\n  kinematics_solver_timeout: 0.05\n" for s in SIDES))

# 3. joint limits: the single-arm values, with the prefix on every joint name
lim = read("joint_limits.yaml").split("joint_limits:\n")
head = lim[0]
body = []
for s in SIDES:
    for j in JOINTS:
        m = re.search(rf"  {j}:\n((?:    .*\n)+)", lim[1])
        body.append(f"  {s}_{j}:\n{m.group(1)}")
write("joint_limits.yaml", head + "joint_limits:\n" + "".join(body))

# 4. OMPL: the group sections are renamed, the gripper section is dropped
ompl = read("ompl_planning.yaml")
i = ompl.index("\nmanipulator:")
j = ompl.index("\ngripper:")
section = ompl[i:j].strip("\n").replace("manipulator:", "{g}:", 1)
write("ompl_planning.yaml", ompl[:i].rstrip("\n") + "\n\n" +
      "\n\n".join(section.format(g=f"{s}_arm") for s in SIDES) + "\n")

# 5. MoveIt -> controller: one FollowJointTrajectory controller per arm
ctl = "moveit_controller_manager: moveit_simple_controller_manager/MoveItSimpleControllerManager\n\n"
ctl += "moveit_simple_controller_manager:\n  controller_names:\n"
ctl += "".join(f"    - {s}_joint_trajectory_controller\n" for s in SIDES)
for s in SIDES:
    ctl += f"\n  {s}_joint_trajectory_controller:\n    type: FollowJointTrajectory\n    joints:\n"
    ctl += "".join(f"      - {s}_{j}\n" for j in JOINTS)
    ctl += "    action_ns: follow_joint_trajectory\n    default: true\n"
write("moveit_controllers.yaml", ctl)

# 6. ros2_control: one controller manager, a joint trajectory controller per arm
rc = "controller_manager:\n  ros__parameters:\n    update_rate: 1000  # Hz\n\n"
rc += "    joint_state_broadcaster:\n      type: joint_state_broadcaster/JointStateBroadcaster\n"
for s in SIDES:
    rc += f"\n    {s}_joint_trajectory_controller:\n      type: joint_trajectory_controller/JointTrajectoryController\n"
for s in SIDES:
    rc += f"\n{s}_joint_trajectory_controller:\n  ros__parameters:\n    joints:\n"
    rc += "".join(f"      - {s}_{j}\n" for j in JOINTS)
    rc += ("    command_interfaces:\n      - position\n    state_interfaces:\n      - position\n      - velocity\n"
           "    state_publish_rate: 100.0\n    action_monitor_rate: 20.0\n    allow_partial_joints_goal: false\n"
           "    constraints:\n      stopped_velocity_tolerance: 0.0\n      goal_time: 0.0\n")
write("ros2_controllers.yaml", rc)

# 7. RViz: the single-arm MoveIt layout works as it is (Fixed Frame is "world")
write("moveit.rviz", read("moveit.rviz"))
