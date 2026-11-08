#!/usr/bin/env python3
"""Forward kinematics of the Kinova Gen3 (7 joints): from seven joint angles to the pose of end_effector_link.

  fk_gen3.py Q1 Q2 Q3 Q4 Q5 Q6 Q7      joint angles in radians

The pose is given in base_link, the same as: ros2 run tf2_ros tf2_echo base_link end_effector_link
"""
import math
import sys

import numpy as np

H = math.pi / 2

# Where each joint sits relative to the one before it: (x, y, z in metres, roll in radians).
# Copied from the <origin> lines of the URDF (lesson B1). Pitch and yaw are 0 in all of them.
JOINTS = [
    ("joint_1", 0.0, 0.0, 0.15643, math.pi),
    ("joint_2", 0.0, 0.005375, -0.12838, H),
    ("joint_3", 0.0, -0.21038, -0.006375, -H),
    ("joint_4", 0.0, 0.006375, -0.21038, H),
    ("joint_5", 0.0, -0.20843, -0.006375, -H),
    ("joint_6", 0.0, 0.00017505, -0.10593, H),
    ("joint_7", 0.0, -0.10593, -0.00017505, -H),
]
# The fixed joint end_effector: the hand frame, 6.15 cm after joint_7, turned upside down (roll pi).
END_EFFECTOR = (0.0, 0.0, -0.061525, math.pi)


def translate(x, y, z):
    t = np.eye(4)
    t[:3, 3] = [x, y, z]
    return t


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]])


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])


q = [float(a) for a in sys.argv[1:8]]
pose = np.eye(4)  # the pose of base_link in itself: no movement
for (name, x, y, z, roll), angle in zip(JOINTS, q):
    # Go to the joint (offset, then its fixed turn), then turn by the joint angle about its z axis.
    pose = pose @ translate(x, y, z) @ rot_x(roll) @ rot_z(angle)
    print(f"{name} frame at  x = {pose[0, 3]:7.3f}  y = {pose[1, 3]:7.3f}  z = {pose[2, 3]:7.3f}")

x, y, z, roll = END_EFFECTOR
pose = pose @ translate(x, y, z) @ rot_x(roll)

# Roll, pitch, yaw of the hand (rotation about x, then y, then z of the fixed frame), as tf2_echo prints them.
r = pose[:3, :3]
roll = math.degrees(math.atan2(r[2, 1], r[2, 2]))
pitch = math.degrees(-math.asin(r[2, 0]))
yaw = math.degrees(math.atan2(r[1, 0], r[0, 0]))
print(f"end_effector_link: translation [{pose[0, 3]:.3f}, {pose[1, 3]:.3f}, {pose[2, 3]:.3f}]")
print(f"end_effector_link: RPY (degree) [{roll:.3f}, {pitch:.3f}, {yaw:.3f}]")
print("end_effector_link: matrix")
for row in pose:
    print("  " + " ".join(f"{v:7.3f}" for v in row))
