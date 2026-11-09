"""Kinematics of the Kinova Gen3, shared by ik_gen3.py and null_motion.py.

fk(q): the 4x4 pose of end_effector_link in base_link (the same chain as fk_gen3 in lesson B2).
residual(q, target): how far the hand is from a target pose, as 6 numbers.
jacobian(q, target): how that residual changes when each of the 7 joints moves (6 x 7 matrix).
"""
import math

import numpy as np

H = math.pi / 2
# (x, y, z in metres, roll in radians) of each joint's origin, from the URDF (lesson B1), then of end_effector.
ORIGINS = [
    (0.0, 0.0, 0.15643, math.pi),
    (0.0, 0.005375, -0.12838, H),
    (0.0, -0.21038, -0.006375, -H),
    (0.0, 0.006375, -0.21038, H),
    (0.0, -0.20843, -0.006375, -H),
    (0.0, 0.00017505, -0.10593, H),
    (0.0, -0.10593, -0.00017505, -H),
]
END_EFFECTOR = (0.0, 0.0, -0.061525, math.pi)
# Joint limits of the URDF (lesson B1): joints 2, 4, 6 are limited, the others turn freely.
LIMIT = [math.inf, 2.24, math.inf, 2.57, math.inf, 2.09, math.inf]


def _pose(x, y, z, roll, angle=0.0):
    cr, sr, ca, sa = math.cos(roll), math.sin(roll), math.cos(angle), math.sin(angle)
    rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    rz = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])
    t = np.eye(4)
    t[:3, :3] = rx @ rz
    t[:3, 3] = [x, y, z]
    return t


def fk(q):
    t = np.eye(4)
    for (x, y, z, roll), angle in zip(ORIGINS, q):
        t = t @ _pose(x, y, z, roll, angle)
    return t @ _pose(*END_EFFECTOR)


def rotvec(r):
    """The rotation r as one vector: its axis, scaled by its angle (radians)."""
    angle = math.acos(max(-1.0, min(1.0, (np.trace(r) - 1) / 2)))
    w = np.array([r[2, 1] - r[1, 2], r[0, 2] - r[2, 0], r[1, 0] - r[0, 1]]) / 2
    if angle < 1e-9:
        return w
    return w / math.sin(angle) * angle


def residual(q, target):
    """Target minus current: 3 position numbers (m), then 3 numbers for the rotation that is still missing (rad)."""
    t = fk(q)
    return np.concatenate([target[:3, 3] - t[:3, 3], rotvec(target[:3, :3] @ t[:3, :3].T)])


def jacobian(q, target, eps=1e-6):
    """6 x 7: column j is how the residual changes when joint j moves by a small step (finite difference)."""
    r0 = residual(q, target)
    jac = np.zeros((6, 7))
    for j in range(7):
        q2 = np.array(q, dtype=float)
        q2[j] += eps
        jac[:, j] = (residual(q2, target) - r0) / eps
    return jac


def pose_from(xyz, rpy_deg):
    """A 4x4 pose from a position and roll, pitch, yaw in degrees (the way tf2_echo prints them)."""
    r, p, y = (math.radians(a) for a in rpy_deg)
    rx = np.array([[1, 0, 0], [0, math.cos(r), -math.sin(r)], [0, math.sin(r), math.cos(r)]])
    ry = np.array([[math.cos(p), 0, math.sin(p)], [0, 1, 0], [-math.sin(p), 0, math.cos(p)]])
    rz = np.array([[math.cos(y), -math.sin(y), 0], [math.sin(y), math.cos(y), 0], [0, 0, 1]])
    t = np.eye(4)
    t[:3, :3] = rz @ ry @ rx
    t[:3, 3] = xyz
    return t
