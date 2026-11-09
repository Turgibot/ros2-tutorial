#!/usr/bin/env python3
"""Turn the ground-truth block poses from Gazebo into TF frames: base_link -> block_A ... block_D.

The arm stands at the origin of the Gazebo world, so the world frame and the arm's base_link are the same place."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, TransformStamped
from tf2_ros import TransformBroadcaster


class BlockTf(Node):
    def __init__(self):
        super().__init__("block_tf")
        self.broadcaster = TransformBroadcaster(self)
        for k in "ABCD":
            self.create_subscription(PoseStamped, f"/model/block_{k}/pose",
                                     lambda msg, k=k: self.on_pose(k, msg), 10)

    def on_pose(self, k, msg):
        t = TransformStamped()
        t.header.stamp = msg.header.stamp              # simulated time, as in every other message
        t.header.frame_id = "base_link"
        t.child_frame_id = f"block_{k}"
        t.transform.translation.x = msg.pose.position.x
        t.transform.translation.y = msg.pose.position.y
        t.transform.translation.z = msg.pose.position.z
        t.transform.rotation = msg.pose.orientation
        self.broadcaster.sendTransform(t)


def main():
    rclpy.init()
    rclpy.spin(BlockTf())


if __name__ == "__main__":
    main()
