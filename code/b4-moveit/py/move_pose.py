#!/usr/bin/env python3
"""Ask MoveIt to move the hand to a pose: move_pose X Y Z ROLL PITCH YAW  (metres, degrees)."""
import math
import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import Pose
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (BoundingVolume, Constraints, MoveItErrorCodes,
                             OrientationConstraint, PositionConstraint)
from shape_msgs.msg import SolidPrimitive

GROUP = "manipulator"
BASE = "base_link"
TIP = "end_effector_link"


def quaternion_from_rpy(roll, pitch, yaw):
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    return (sr * cp * cy - cr * sp * sy,   # x
            cr * sp * cy + sr * cp * sy,   # y
            cr * cp * sy - sr * sp * cy,   # z
            cr * cp * cy + sr * sp * sy)   # w


def error_name(code):
    for name in dir(MoveItErrorCodes):
        if name.isupper() and getattr(MoveItErrorCodes, name) == code:
            return name
    return str(code)


def main():
    if len(sys.argv) != 7:
        sys.exit("usage: move_pose X Y Z ROLL PITCH YAW   (metres, degrees)")
    x, y, z = map(float, sys.argv[1:4])
    roll, pitch, yaw = (math.radians(float(a)) for a in sys.argv[4:7])

    rclpy.init()
    node = Node("move_pose")
    client = ActionClient(node, MoveGroup, "move_action")
    if not client.wait_for_server(timeout_sec=10.0):
        sys.exit("no /move_action: is move_group running?")

    target = Pose()
    target.position.x, target.position.y, target.position.z = x, y, z
    qx, qy, qz, qw = quaternion_from_rpy(roll, pitch, yaw)
    target.orientation.x, target.orientation.y = qx, qy
    target.orientation.z, target.orientation.w = qz, qw

    # position: the hand origin must lie inside a 1 mm sphere around the target
    sphere = SolidPrimitive(type=SolidPrimitive.SPHERE, dimensions=[0.001])
    position = PositionConstraint()
    position.header.frame_id = BASE
    position.link_name = TIP
    position.constraint_region = BoundingVolume(primitives=[sphere], primitive_poses=[target])
    position.weight = 1.0
    # orientation: each axis within 0.01 rad of the target
    orientation = OrientationConstraint()
    orientation.header.frame_id = BASE
    orientation.link_name = TIP
    orientation.orientation = target.orientation
    orientation.absolute_x_axis_tolerance = 0.01
    orientation.absolute_y_axis_tolerance = 0.01
    orientation.absolute_z_axis_tolerance = 0.01
    orientation.weight = 1.0

    goal = MoveGroup.Goal()
    goal.request.group_name = GROUP
    goal.request.num_planning_attempts = 5
    goal.request.allowed_planning_time = 5.0
    goal.request.max_velocity_scaling_factor = 0.3
    goal.request.max_acceleration_scaling_factor = 0.3
    goal.request.goal_constraints = [Constraints(position_constraints=[position],
                                                 orientation_constraints=[orientation])]
    goal.planning_options.plan_only = False   # plan AND execute

    send = client.send_goal_async(goal)
    rclpy.spin_until_future_complete(node, send)
    handle = send.result()
    if not handle.accepted:
        sys.exit("goal rejected")
    done = handle.get_result_async()
    rclpy.spin_until_future_complete(node, done)
    result = done.result().result
    print(f"result: {error_name(result.error_code.val)}")
    points = result.planned_trajectory.joint_trajectory.points
    if points:
        last = points[-1]
        print(f"trajectory: {len(points)} points, {last.time_from_start.sec + last.time_from_start.nanosec * 1e-9:.2f} s")
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if result.error_code.val == MoveItErrorCodes.SUCCESS else 1)


if __name__ == "__main__":
    main()
