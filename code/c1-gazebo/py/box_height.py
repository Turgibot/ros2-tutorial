#!/usr/bin/env python3
"""Watch the pose of the model "box" that Gazebo publishes (bridged to ROS as geometry_msgs/PoseStamped)
and print its height every 0.1 s of simulated time, and the moment it lands."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

GROUND_Z = 0.1        # the box is 0.2 m tall, so its centre is 0.1 m above the ground when it rests
START_Z = 1.0         # where the world file puts the box


class BoxHeight(Node):
    def __init__(self):
        super().__init__("box_height")
        self.last_print = -1.0
        self.landed = False
        self.create_subscription(PoseStamped, "/model/box/pose", self.on_pose, 10)

    def on_pose(self, msg):
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        z = msg.pose.position.z
        if t - self.last_print >= 0.1:
            self.last_print = t
            self.get_logger().info(f"t = {t:5.2f} s   z = {z:.3f} m")
        if not self.landed and z <= GROUND_Z + 0.001:
            self.landed = True
            self.get_logger().info(f"landed after {t:.3f} s of simulated time")


def main():
    rclpy.init()
    rclpy.spin(BoxHeight())


if __name__ == "__main__":
    main()
