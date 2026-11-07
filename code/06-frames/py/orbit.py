#!/usr/bin/env python3
"""Publishes a moving frame 'marker' that circles around the frame 'base' (radius 0.3 m, 0.5 rad/s, 0.2 m up)."""
import math

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class Orbit(Node):
    def __init__(self):
        super().__init__('orbit')
        self.broadcaster = TransformBroadcaster(self)
        self.start = self.get_clock().now()
        self.create_timer(0.05, self.on_timer)  # 20 times per second

    def on_timer(self):
        now = self.get_clock().now()
        angle = 0.5 * (now - self.start).nanoseconds * 1e-9  # 0.5 rad/s

        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = 'base'     # parent frame
        t.child_frame_id = 'marker'    # child frame: its pose is given in the parent
        t.transform.translation.x = 0.3 * math.cos(angle)
        t.transform.translation.y = 0.3 * math.sin(angle)
        t.transform.translation.z = 0.2
        # rotation about z by `angle`, as a quaternion (x, y, z, w) = (0, 0, sin(angle/2), cos(angle/2))
        t.transform.rotation.z = math.sin(angle / 2)
        t.transform.rotation.w = math.cos(angle / 2)
        self.broadcaster.sendTransform(t)


def main():
    rclpy.init()
    rclpy.spin(Orbit())


if __name__ == '__main__':
    main()
