#!/usr/bin/env python3
"""Print the position of the four blocks once per second of simulated time, from the poses Gazebo publishes."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

BLOCKS = "ABCD"


class CheckSettled(Node):
    def __init__(self):
        super().__init__("check_settled")
        self.pose = {}
        self.last_print = None
        for k in BLOCKS:
            self.create_subscription(PoseStamped, f"/model/block_{k}/pose",
                                     lambda msg, k=k: self.on_pose(k, msg), 10)

    def on_pose(self, k, msg):
        self.pose[k] = msg.pose.position
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if len(self.pose) == len(BLOCKS) and (self.last_print is None or t - self.last_print >= 1.0):
            self.last_print = t
            cols = "   ".join(f"{b}: {p.x:.4f} {p.y:.4f} {p.z:.4f}" for b, p in sorted(self.pose.items()))
            self.get_logger().info(f"t = {t:5.1f} s   {cols}")


def main():
    rclpy.init()
    rclpy.spin(CheckSettled())


if __name__ == "__main__":
    main()
