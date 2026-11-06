#!/usr/bin/env python3
"""Action server /execute: pretends to carry out a symbolic action in four phases (1 s each)."""
import time

import rclpy
from rclpy.action import ActionServer, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from a3_interfaces.action import Execute

PHASES = ['approach', 'grasp', 'lift', 'place']


class Robot(Node):
    def __init__(self):
        super().__init__('robot')
        # Reentrant group + multi-threaded executor: a cancel request must be handled
        # while execute() is still running.
        ActionServer(self, Execute, 'execute',
                     execute_callback=self.execute,
                     cancel_callback=lambda goal_handle: CancelResponse.ACCEPT,
                     callback_group=ReentrantCallbackGroup())

    def execute(self, goal_handle):
        action = f'{goal_handle.request.name} {" ".join(goal_handle.request.args)}'
        self.get_logger().info(f'executing: {action}')
        feedback = Execute.Feedback()
        for i, phase in enumerate(PHASES):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info(f'canceled before {phase}')
                return Execute.Result(success=False, message=f'canceled before {phase}')
            time.sleep(1.0)   # the "work"
            feedback.phase = phase
            feedback.progress = (i + 1) / len(PHASES)
            goal_handle.publish_feedback(feedback)
        goal_handle.succeed()
        self.get_logger().info(f'done: {action}')
        return Execute.Result(success=True, message=f'{action}: done')


def main():
    rclpy.init()
    executor = MultiThreadedExecutor()
    executor.add_node(Robot())
    executor.spin()


if __name__ == '__main__':
    main()
