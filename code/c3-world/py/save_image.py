#!/usr/bin/env python3
"""Save one frame of a ROS 2 image topic as a PNG: save_image.py TOPIC OUT.png"""
import sys
import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class Saver(Node):
    def __init__(self, topic, out):
        super().__init__("save_image")
        self.out = out
        self.done = False
        self.create_subscription(Image, topic, self.on_image, 1)

    def on_image(self, msg):
        img = CvBridge().imgmsg_to_cv2(msg, "bgr8")
        cv2.imwrite(self.out, img)
        self.get_logger().info(f"saved {self.out}: {msg.width}x{msg.height}, {msg.encoding}")
        self.done = True


def main():
    rclpy.init()
    node = Saver(sys.argv[1], sys.argv[2])
    while rclpy.ok() and not node.done:
        rclpy.spin_once(node, timeout_sec=0.5)


if __name__ == "__main__":
    main()
