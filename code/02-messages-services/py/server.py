#!/usr/bin/env python3
"""Service /check_action: says whether a symbolic action is well formed."""
import rclpy
from rclpy.node import Node
from a2_interfaces.srv import CheckAction

ARGUMENTS = {'pickup': 1, 'putdown': 1, 'stack': 2, 'unstack': 2}   # action -> how many blocks it needs


class Checker(Node):
    def __init__(self):
        super().__init__('checker')
        self.create_service(CheckAction, 'check_action', self.on_request)

    def on_request(self, request, response):
        name, args = request.action.name, request.action.args
        if name not in ARGUMENTS:
            response.valid, response.reason = False, f"unknown action '{name}'"
        elif len(args) != ARGUMENTS[name]:
            response.valid, response.reason = False, f'{name} needs {ARGUMENTS[name]} blocks, got {len(args)}'
        else:
            response.valid, response.reason = True, 'ok'
        self.get_logger().info(f'checked {name} {list(args)}: {response.reason}')
        return response


def main():
    rclpy.init()
    rclpy.spin(Checker())


if __name__ == '__main__':
    main()
