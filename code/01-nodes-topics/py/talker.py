#!/usr/bin/env python3
"""Publishes a counter on /chatter twice a second."""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.pub = self.create_publisher(String, 'chatter', 10)
        self.count = 0
        self.create_timer(0.5, self.tick)   # call self.tick every 0.5 s

    def tick(self):
        msg = String()
        msg.data = f'hello {self.count}'
        self.pub.publish(msg)
        self.get_logger().info(f'sent: {msg.data}')
        self.count += 1


def main():
    rclpy.init()
    rclpy.spin(Talker())   # keep running and serving the timer until Ctrl+C


if __name__ == '__main__':
    main()
