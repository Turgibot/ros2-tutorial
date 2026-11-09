#!/usr/bin/env python3
"""Run a plan, a list of symbolic actions separated by ';', one after the other, and stop at the first failure.

  run_plan.py "stack C D; stack B C"
"""
import sys

import rclpy
from a3_interfaces.action import Execute
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_msgs.msg import String


def main():
    if len(sys.argv) != 2:
        sys.exit('usage: run_plan.py "unstack B C; stack B D"')
    steps = [s.split() for s in sys.argv[1].split(";") if s.strip()]
    rclpy.init()
    node = Node("run_plan")
    towers = {}
    node.create_subscription(String, "/towers", lambda m: towers.update(text=m.data), 
                             QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
    client = ActionClient(node, Execute, "execute")
    if not client.wait_for_server(timeout_sec=10.0):
        sys.exit("no /execute server: is execute_server.py running?")
    ok = True
    for step in steps:
        goal = Execute.Goal(name=step[0], args=step[1:])
        print(f"> {' '.join(step)}")
        send = client.send_goal_async(goal, feedback_callback=lambda m: None)
        rclpy.spin_until_future_complete(node, send)
        done = send.result().get_result_async()
        rclpy.spin_until_future_complete(node, done)
        result = done.result().result
        print(f"  {'done' if result.success else 'FAILED: ' + result.message}")
        if not result.success:
            ok = False
            break
    for _ in range(20):                       # let the last /towers message arrive
        rclpy.spin_once(node, timeout_sec=0.1)
    print("towers: " + towers.get("text", "?"))
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
