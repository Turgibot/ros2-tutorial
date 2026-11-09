#!/usr/bin/env python3
"""Put a box into the planning scene: add_box NAME X Y Z SX SY SZ   or   add_box NAME remove"""
import sys

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject, PlanningScene
from moveit_msgs.srv import ApplyPlanningScene
from shape_msgs.msg import SolidPrimitive


def main():
    args = sys.argv[1:]
    if not (len(args) == 7 or (len(args) == 2 and args[1] == "remove")):
        sys.exit("usage: add_box NAME X Y Z SX SY SZ   |   add_box NAME remove")
    name = args[0]

    obj = CollisionObject()
    obj.header.frame_id = "base_link"
    obj.id = name
    if args[1] == "remove":
        obj.operation = CollisionObject.REMOVE
    else:
        x, y, z, sx, sy, sz = map(float, args[1:7])
        obj.primitives = [SolidPrimitive(type=SolidPrimitive.BOX, dimensions=[sx, sy, sz])]
        pose = Pose()
        pose.position.x, pose.position.y, pose.position.z = x, y, z
        pose.orientation.w = 1.0
        obj.primitive_poses = [pose]
        obj.operation = CollisionObject.ADD

    scene = PlanningScene()
    scene.is_diff = True                    # change the scene, do not replace it
    scene.world.collision_objects = [obj]

    rclpy.init()
    node = Node("add_box")
    client = node.create_client(ApplyPlanningScene, "apply_planning_scene")
    if not client.wait_for_service(timeout_sec=10.0):
        sys.exit("no /apply_planning_scene: is move_group running?")
    future = client.call_async(ApplyPlanningScene.Request(scene=scene))
    rclpy.spin_until_future_complete(node, future)
    print("scene updated" if future.result().success else "scene update failed")
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
