#!/usr/bin/env python3
"""Asks /check_action about one action, for example: python3 client.py unstack F W"""
import sys
import rclpy
from rclpy.node import Node
from a2_interfaces.srv import CheckAction


def main():
    rclpy.init()
    node = Node('checker_client')
    client = node.create_client(CheckAction, 'check_action')
    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('waiting for the service...')

    request = CheckAction.Request()
    request.action.name = sys.argv[1]
    request.action.args = sys.argv[2:]

    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)
    response = future.result()
    print(f'valid={response.valid} reason={response.reason}')
    rclpy.shutdown()


if __name__ == '__main__':
    main()
