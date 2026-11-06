#!/usr/bin/env python3
"""Sends one goal to /execute and prints feedback and result, for example: python3 client.py unstack F W"""
import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from a3_interfaces.action import Execute


def main():
    rclpy.init()
    node = Node('robot_client')
    client = ActionClient(node, Execute, 'execute')
    client.wait_for_server()

    goal = Execute.Goal()
    goal.name = sys.argv[1]
    goal.args = sys.argv[2:]

    # 1. send the goal; the feedback callback runs for every feedback message
    send_future = client.send_goal_async(
        goal, feedback_callback=lambda msg: print(f'feedback: {msg.feedback.phase} ({msg.feedback.progress:.2f})'))
    rclpy.spin_until_future_complete(node, send_future)
    goal_handle = send_future.result()
    if not goal_handle.accepted:
        print('goal rejected')
        return

    # 2. wait for the result
    result_future = goal_handle.get_result_async()
    rclpy.spin_until_future_complete(node, result_future)
    result = result_future.result().result
    print(f'result: success={result.success} message={result.message}')
    rclpy.shutdown()


if __name__ == '__main__':
    main()
