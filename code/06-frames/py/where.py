#!/usr/bin/env python3
"""Once a second, asks TF where the frame `target` is, as seen from the frame `source`, and prints it."""
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener


class Where(Node):
    def __init__(self):
        super().__init__('where')
        self.declare_parameter('source', 'base')
        self.declare_parameter('target', 'marker')
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)  # fills the buffer from /tf and /tf_static
        self.create_timer(1.0, self.on_timer)

    def on_timer(self):
        source = self.get_parameter('source').value
        target = self.get_parameter('target').value
        try:
            # Time() means "the latest transform available"
            t = self.buffer.lookup_transform(source, target, Time())
        except TransformException as e:
            self.get_logger().warn(f'cannot get {target} in {source}: {e}')
            return
        p = t.transform.translation
        self.get_logger().info(f'{target} in {source}: x={p.x:.3f} y={p.y:.3f} z={p.z:.3f}')


def main():
    rclpy.init()
    rclpy.spin(Where())


if __name__ == '__main__':
    main()
