#!/usr/bin/env python3
"""Prints every action that arrives on /action."""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.create_subscription(String, 'action', self.on_message, 10)

    def on_message(self, msg):
        self.get_logger().info(f'heard: {msg.data}')


def main():
    rclpy.init()
    rclpy.spin(Listener())


if __name__ == '__main__':
    main()
