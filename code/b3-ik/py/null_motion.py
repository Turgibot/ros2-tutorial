#!/usr/bin/env python3
"""Move the Gen3's joints while the hand stays where it is (the null space).

  null_motion.py Q1 Q2 Q3 Q4 Q5 Q6 Q7 [STEPS]

Starts from the joint angles Q1..Q7 (radians), holds the hand pose they give, and pushes joint 3 for STEPS steps
(default 100). The push is projected onto the null space: only the part that does not move the hand is kept.
"""
import sys

import numpy as np

import gen3

q = np.array([float(a) for a in sys.argv[1:8]])
steps = int(sys.argv[8]) if len(sys.argv) >= 9 else 100
target = gen3.fk(q)              # the hand pose to hold
push = np.zeros(7)
push[2] = 0.01                   # "please turn joint 3": 0.01 rad per step


def show(step):
    pos = gen3.fk(q)[:3, 3]
    print(f"step {step:3d}  q = " + " ".join(f"{a:7.3f}" for a in q) + f"   hand = [{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}]")


show(0)
for step in range(1, steps + 1):
    jac = gen3.jacobian(q, target)
    jac_pinv = np.linalg.pinv(jac)                      # 7 x 6: the smallest joint change for a hand change
    null = np.eye(7) - jac_pinv @ jac                   # 7 x 7: keeps only motions that leave the hand alone
    q = q - jac_pinv @ gen3.residual(q, target) + null @ push   # fix any drift, then move in the null space
    if step % (steps // 4) == 0:
        show(step)

err = gen3.residual(q, target)
print(f"hand pose error after {steps} steps: position {np.linalg.norm(err[:3]):.1e} m, rotation {np.linalg.norm(err[3:]):.1e} rad")
