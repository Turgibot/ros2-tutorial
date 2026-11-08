#!/usr/bin/env python3
"""Forward kinematics of a flat arm with two links.

  fk2.py THETA1 THETA2 [L1 L2]      angles in degrees, lengths in metres (default 0.4 and 0.3)

Prints where the elbow and the hand are, and which way the hand points.
"""
import math
import sys

theta1, theta2 = (math.radians(float(a)) for a in sys.argv[1:3])
l1, l2 = (float(a) for a in sys.argv[3:5]) if len(sys.argv) >= 5 else (0.4, 0.3)

# The elbow is l1 away from the base, in the direction theta1.
elbow_x = l1 * math.cos(theta1)
elbow_y = l1 * math.sin(theta1)

# The second link points in the direction theta1 + theta2 (the angles add up).
hand_x = elbow_x + l2 * math.cos(theta1 + theta2)
hand_y = elbow_y + l2 * math.sin(theta1 + theta2)

print(f"elbow: x = {elbow_x:.4f}  y = {elbow_y:.4f}")
print(f"hand:  x = {hand_x:.4f}  y = {hand_y:.4f}  pointing {math.degrees(theta1 + theta2):.1f} degrees")
