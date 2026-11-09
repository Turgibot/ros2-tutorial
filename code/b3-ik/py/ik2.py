#!/usr/bin/env python3
"""Inverse kinematics of a flat arm with two links, by geometry.

  ik2.py X Y [L1 L2]      hand position in metres, lengths in metres (default 0.4 and 0.3)

Prints the two joint settings (elbow one way and the other) that put the hand at (X, Y), in degrees.
"""
import math
import sys

x, y = (float(a) for a in sys.argv[1:3])
l1, l2 = (float(a) for a in sys.argv[3:5]) if len(sys.argv) >= 5 else (0.4, 0.3)

# Law of cosines in the triangle base - elbow - hand: it gives the angle at the elbow.
cos_theta2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
if abs(cos_theta2) > 1:
    print(f"unreachable: the hand can be between {abs(l1 - l2):.3f} and {l1 + l2:.3f} m from the base, "
          f"this point is {math.hypot(x, y):.3f} m away")
    sys.exit(1)

for sign, name in ((+1, "elbow down"), (-1, "elbow up  ")):
    theta2 = sign * math.acos(cos_theta2)
    # theta1: the direction of the hand, minus the angle that link 2 adds.
    theta1 = math.atan2(y, x) - math.atan2(l2 * math.sin(theta2), l1 + l2 * math.cos(theta2))
    print(f"{name}: theta1 = {math.degrees(theta1):8.3f}  theta2 = {math.degrees(theta2):8.3f}")
