#!/usr/bin/env python3
"""Publishes a symbolic action (name and arguments) as text on /action. Its settings are parameters."""
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import String


class Announcer(Node):
    def __init__(self):
        super().__init__('announcer')
        # Declare each parameter with a default value (this also fixes its type).
        self.declare_parameter('name', 'pickup')
        self.declare_parameter('args', ['A'])
        self.declare_parameter('rate_hz', 1.0)

        self.pub = self.create_publisher(String, 'action', 10)
        self.timer = self.create_timer(1.0 / self.get_parameter('rate_hz').value, self.tick)
        self.add_on_set_parameters_callback(self.on_change)   # called before a new value is accepted

    def on_change(self, params):
        for p in params:
            if p.name == 'rate_hz':
                if p.value <= 0.0:
                    return SetParametersResult(successful=False, reason='rate_hz must be positive')
                self.destroy_timer(self.timer)   # restart the timer with the new period
                self.timer = self.create_timer(1.0 / p.value, self.tick)
        return SetParametersResult(successful=True)

    def tick(self):
        words = [self.get_parameter('name').value] + list(self.get_parameter('args').value)
        msg = String()
        msg.data = ' '.join(words)
        self.pub.publish(msg)
        self.get_logger().info(f'sent: {msg.data}')


def main():
    rclpy.init()
    rclpy.spin(Announcer())


if __name__ == '__main__':
    main()
