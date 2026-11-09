#!/usr/bin/env python3
"""Action server /execute: the symbolic actions of the blocks world, carried out by the arm.

It speaks the Execute action of lesson A3 (name + args), so the clients of A3 work with it. Three skills:

  unstack X Y   X is on top of Y: put X on the table
  stack X Y     X is alone on the table, Y is the top of a tower: put X on Y
  putdown X     X is on top of a tower: put X on the table

Each skill first checks its conditions against the symbolic state (/towers, lesson D1) and refuses if they do not
hold. Then it works out where the block must go and asks /pick_place (lesson D2) to move it."""
import time

import rclpy
from a3_interfaces.action import Execute
from d2_interfaces.action import PickPlace
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient, ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_msgs.msg import String

BLOCKS = "ABCD"
SIZE = 0.05
ON_TABLE_Z = 0.325                       # centre of a block on the table
SLOT_X = 0.5
SLOTS_Y = [-0.18, -0.06, 0.06, 0.18]     # the four places on the table where a block can be put down
MAX_HEIGHT = 3                           # the hand cannot reach the fourth level (lesson D2)
STAGES = ["open", "above", "descend", "grasp", "lift", "transit", "lower", "release", "retreat"]


def parse(text):
    """'A | CB | D   held: B' -> (['A', 'CB', 'D'], ['B']): the towers bottom to top, and the blocks in the air."""
    towers_part, _, held_part = text.partition("held:")
    towers = [t.strip() for t in towers_part.split("|") if t.strip()]
    return towers, held_part.split()


class Skills(Node):
    def __init__(self):
        super().__init__("skills")
        group = ReentrantCallbackGroup()
        self.towers, self.held = [], []
        self.pos = {}
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.create_subscription(String, "/towers", self.on_towers, latched, callback_group=group)
        for k in BLOCKS:
            self.create_subscription(PoseStamped, f"/model/block_{k}/pose",
                                     lambda m, k=k: self.pos.__setitem__(k, (m.pose.position.x, m.pose.position.y, m.pose.position.z)),
                                     10, callback_group=group)
        self.pick_place = ActionClient(self, PickPlace, "pick_place", callback_group=group)
        self.server = ActionServer(self, Execute, "execute", execute_callback=self.execute, callback_group=group)
        self.get_logger().info("skills are ready: unstack X Y, stack X Y, putdown X")

    def on_towers(self, msg):
        self.towers, self.held = parse(msg.data)

    # ---- the conditions and the target of each skill ----------------------------------------------------------
    def tower_of(self, block):
        return next((t for t in self.towers if block in t), None)

    def free_slot(self, near_y):
        """The place on the table, free of blocks, that is closest to y = near_y."""
        free = [y for y in SLOTS_Y
                if all(abs(self.pos[b][1] - y) > 0.04 or abs(self.pos[b][0] - SLOT_X) > 0.04 for b in BLOCKS)]
        if not free:
            raise ValueError("there is no free place on the table")
        return min(free, key=lambda y: abs(y - near_y))

    def plan(self, name, args):
        """Check the conditions and return (block, x, y, z) for the pick-and-place, or raise ValueError."""
        if self.held:
            raise ValueError(f"block {self.held[0]} is in the air: wait until the arm is still")
        if name == "unstack" and len(args) == 2:
            x, y = args
            tower = self.tower_of(x)
            if tower is None or y not in tower:
                raise ValueError(f"unstack {x} {y}: unknown block, or the blocks are not in a tower")
            if tower.find(x) != tower.find(y) + 1 or not tower.endswith(x):
                raise ValueError(f"unstack {x} {y}: {x} is not the top block directly on {y} (towers: {' | '.join(self.towers)})")
            return x, SLOT_X, self.free_slot(self.pos[x][1]), ON_TABLE_Z
        if name == "putdown" and len(args) == 1:
            x = args[0]
            tower = self.tower_of(x)
            if tower is None:
                raise ValueError(f"putdown {x}: unknown block")
            if tower == x:
                raise ValueError(f"putdown {x}: {x} is already on the table")
            if not tower.endswith(x):
                raise ValueError(f"putdown {x}: {x} is not at the top of its tower (towers: {' | '.join(self.towers)})")
            return x, SLOT_X, self.free_slot(self.pos[x][1]), ON_TABLE_Z
        if name == "stack" and len(args) == 2:
            x, y = args
            if x == y or x not in BLOCKS or y not in BLOCKS:
                raise ValueError(f"stack {x} {y}: two different blocks of {BLOCKS} are needed")
            if self.tower_of(x) != x:
                raise ValueError(f"stack {x} {y}: {x} must be alone on the table (towers: {' | '.join(self.towers)})")
            tower = self.tower_of(y)
            if not tower.endswith(y):
                raise ValueError(f"stack {x} {y}: {y} is not clear, there is a block on it (towers: {' | '.join(self.towers)})")
            if len(tower) >= MAX_HEIGHT:
                raise ValueError(f"stack {x} {y}: the tower would be higher than {MAX_HEIGHT} blocks")
            px, py, pz = self.pos[y]
            return x, px, py, pz + SIZE
        raise ValueError(f"'{name} {' '.join(args)}' is not a skill: use unstack X Y, stack X Y or putdown X")

    # ---- the action -------------------------------------------------------------------------------------------
    def execute(self, goal_handle):
        name, args = goal_handle.request.name, list(goal_handle.request.args)
        text = f"{name} {' '.join(args)}"
        self.get_logger().info(f"execute: {text}")

        def finish(ok, message):
            (goal_handle.succeed if ok else goal_handle.abort)()
            self.get_logger().info(message)
            return Execute.Result(success=ok, message=message)

        try:
            block, x, y, z = self.plan(name, args)
        except ValueError as error:
            return finish(False, str(error))
        if not self.pick_place.wait_for_server(timeout_sec=5.0):
            return finish(False, "no /pick_place server")

        def relay(msg):                      # feedback of PickPlace -> feedback of Execute
            stage = msg.feedback.stage
            progress = (STAGES.index(stage) + 1) / len(STAGES) if stage in STAGES else 0.0
            goal_handle.publish_feedback(Execute.Feedback(phase=stage, progress=progress))

        send = self.pick_place.send_goal_async(PickPlace.Goal(block=block, x=x, y=y, z=z), feedback_callback=relay)
        while not send.done():                   # the executor's other threads complete the future
            time.sleep(0.01)
        handle = send.result()
        if not handle.accepted:
            return finish(False, "/pick_place refused the goal")
        done = handle.get_result_async()
        while not done.done():
            time.sleep(0.05)
        result = done.result().result
        return finish(result.success, f"{text}: done" if result.success else f"{text}: {result.message}")


def main():
    rclpy.init()
    node = Skills()
    executor = MultiThreadedExecutor(num_threads=6)
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
