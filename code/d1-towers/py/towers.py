#!/usr/bin/env python3
"""The world estimator: turn the block poses into towers.

Reads /model/block_X/pose (ground truth from Gazebo) and publishes /towers (std_msgs/String), for example
"A | B | DC": three towers, A alone, B alone, and C standing on D. A block in the air (held by the gripper)
is reported on its own as "held: X"."""
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String

BLOCKS = "ABCD"
SIZE = 0.05              # a block is a 5 cm cube
TABLE_Z = 0.30           # height of the table top
TOL_XY = 0.03            # "directly above": centres closer than 3 cm in x and in y
TOL_Z = 0.01             # heights are compared to within 1 cm


class Towers(Node):
    def __init__(self):
        super().__init__("towers")
        self.pos = {}
        self.last = None
        # "transient local": a program that starts later still receives the last message at once
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.pub = self.create_publisher(String, "/towers", latched)
        for k in BLOCKS:
            self.create_subscription(PoseStamped, f"/model/block_{k}/pose",
                                     lambda msg, k=k: self.on_pose(k, msg), 10)

    def on_pose(self, k, msg):
        p = msg.pose.position
        self.pos[k] = (p.x, p.y, p.z)
        if len(self.pos) < len(BLOCKS):
            return
        text = describe(self.pos)
        if text != self.last:                  # publish only when something changed
            self.last = text
            self.pub.publish(String(data=text))
            self.get_logger().info(text)


def below(pos, k):
    """The block that k stands on, or None (k is on the table, or in the air)."""
    for j in BLOCKS:
        if j != k:
            dx, dy, dz = (pos[k][i] - pos[j][i] for i in range(3))
            if abs(dx) < TOL_XY and abs(dy) < TOL_XY and abs(dz - SIZE) < TOL_Z:
                return j
    return None


def on_table(pos, k):
    return abs(pos[k][2] - (TABLE_Z + SIZE / 2)) < TOL_Z


def describe(pos):
    above = {below(pos, k): k for k in BLOCKS if below(pos, k)}      # who is on top of whom
    towers, held = [], []
    for k in BLOCKS:
        if below(pos, k) is None:
            if on_table(pos, k):               # the bottom of a tower
                chain = k
                while chain[-1] in above:
                    chain += above[chain[-1]]
                towers.append(chain)
            else:
                held.append(k)
    text = " | ".join(sorted(towers))
    if held:
        text += "   held: " + " ".join(held)
    return text


def main():
    rclpy.init()
    rclpy.spin(Towers())


if __name__ == "__main__":
    main()
