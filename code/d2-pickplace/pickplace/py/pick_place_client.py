#!/usr/bin/env python3
"""Ask the pick_place server to move a block: pick_place_client.py BLOCK X Y Z   (z is the centre of the block)"""
import sys

import rclpy
from d2_interfaces.action import PickPlace
from rclpy.action import ActionClient
from rclpy.node import Node


def main():
    if len(sys.argv) != 5:
        sys.exit("usage: pick_place_client.py BLOCK X Y Z")
    rclpy.init()
    node = Node("pick_place_client")
    client = ActionClient(node, PickPlace, "pick_place")
    if not client.wait_for_server(timeout_sec=10.0):
        sys.exit("no /pick_place server: is pick_place_server.py running?")
    goal = PickPlace.Goal(block=sys.argv[1], x=float(sys.argv[2]), y=float(sys.argv[3]), z=float(sys.argv[4]))
    send = client.send_goal_async(goal, feedback_callback=lambda m: print("  ", m.feedback.stage))
    rclpy.spin_until_future_complete(node, send)
    done = send.result().get_result_async()
    rclpy.spin_until_future_complete(node, done)
    result = done.result().result
    print(("success: " if result.success else "FAILED: ") + result.message)
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
