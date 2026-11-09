#!/usr/bin/env python3
"""Inverse kinematics of the Kinova Gen3: find joint angles that put end_effector_link at a target pose.

  ik_gen3.py X Y Z ROLL PITCH YAW Q1 Q2 Q3 Q4 Q5 Q6 Q7

The target is a position in metres and roll, pitch, yaw in degrees (in base_link, as tf2_echo prints them).
Q1..Q7 (radians) is where the search starts. Different starts can end in different solutions.
"""
import math
import sys

import numpy as np

import gen3

args = [float(a) for a in sys.argv[1:14]]
target = gen3.pose_from(args[0:3], args[3:6])
q = np.array(args[6:13])

LAMBDA = 0.01      # damping: keeps the steps small when the arm is nearly stretched out
MAX_STEP = 0.3     # largest change of one joint in one iteration (rad)

for iteration in range(1, 201):
    err = gen3.residual(q, target)
    if np.linalg.norm(err[:3]) < 1e-6 and np.linalg.norm(err[3:]) < 1e-6:
        break
    jac = gen3.jacobian(q, target)
    # Damped least squares: the smallest joint change that cancels the error.
    dq = -jac.T @ np.linalg.solve(jac @ jac.T + LAMBDA ** 2 * np.eye(6), err)
    q = q + np.clip(dq, -MAX_STEP, MAX_STEP)
    q = np.clip(q, -np.array(gen3.LIMIT), np.array(gen3.LIMIT))  # stay inside the joint limits

err = gen3.residual(q, target)
print(f"iterations: {iteration}")
print("joints (rad): " + " ".join(f"{a:.4f}" for a in q))
print("joints (deg): " + " ".join(f"{math.degrees(a):.1f}" for a in q))
print(f"position error: {np.linalg.norm(err[:3]):.2e} m   rotation error: {np.linalg.norm(err[3:]):.2e} rad")
