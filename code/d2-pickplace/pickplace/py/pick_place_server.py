#!/usr/bin/env python3
"""Action server /pick_place: take one block from where it is and put it down somewhere else.

Goal: the block's letter and the place for its centre (x, y, z in base_link). The motion is always the same pattern:
open the gripper, go above the block, descend in a straight line, close the gripper, lift, move over the target at
a safe height, descend, let go, retreat. Every straight line is a list of joint positions computed with the
inverse kinematics of B3 (gen3.py), with joint 3 held at 2.5 rad so the arm keeps a tidy shape.

The simulated Robotiq gripper cannot hold a block in Gazebo (see lesson D2), so a block in the gripper is carried
by moving it with Gazebo's set_pose service at 50 Hz. The arm and the gripper really move; the grip is simulated."""
import threading
import time

import numpy as np
import rclpy
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory, ParallelGripperCommand
from d2_interfaces.action import PickPlace
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient, ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from ros_gz_interfaces.msg import Entity
from ros_gz_interfaces.srv import SetEntityPose
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectoryPoint

import gen3

JOINTS = [f"joint_{i}" for i in range(1, 8)]
BLOCKS = "ABCD"
POINTING_DOWN = [180, 0, 90]        # roll, pitch, yaw (degrees) of the hand: fingers along y, pointing down
Q3 = 2.5                            # joint 3 is held here: the arm has 7 joints for a 6-number pose
LIMIT = np.array([9, 2.24, 9, 2.57, 9, 2.09, 9])
# a known joint configuration of that shape, with the hand at (0.50, 0.002, 0.55): the start of every IK walk
READY_Q = np.array([0.2922, 0.5376, 2.5, -0.8983, 0.3191, -1.7866, 1.3632])
READY_POS = (0.5, 0.002, 0.55)

HOVER_Z = 0.58                      # height of the hand when moving over the table (m)
HAND_ABOVE_BLOCK = 0.135            # hand height minus block centre height when gripping (m)
SPEED = 0.15                        # hand speed on straight lines (m/s)
STEP = 0.01                         # distance between two points of a straight line (m)
GRIP_OPEN, GRIP_CLOSED = 0.0, 0.10  # knuckle angle: open; nearly closed on the block, the fingers still a few mm from it


def ik(q, pos):
    """Joint angles that put the hand at pos (pointing down), starting the search at q, with joint 3 fixed."""
    target = gen3.pose_from(pos, POINTING_DOWN)
    q = np.array(q, float)
    q[2] = Q3
    free = [0, 1, 3, 4, 5, 6]
    for _ in range(400):
        err = gen3.residual(q, target)
        if np.linalg.norm(err) < 1e-8:
            break
        jac = gen3.jacobian(q, target)[:, free]
        dq = -jac.T @ np.linalg.solve(jac @ jac.T + 0.01 ** 2 * np.eye(6), err)
        q[free] += np.clip(dq, -0.1, 0.1)
        q = np.clip(q, -LIMIT, LIMIT)
    if np.linalg.norm(gen3.residual(q, target)) > 1e-5:
        raise RuntimeError(f"the hand cannot reach {tuple(round(float(v), 3) for v in pos)} pointing down")
    return q


def line(q, start, end):
    """Joint positions along the straight line from start to end, one every STEP metres (the first is after start)."""
    start, end = np.array(start, float), np.array(end, float)
    n = max(1, int(np.ceil(np.linalg.norm(end - start) / STEP)))
    out = []
    for i in range(1, n + 1):
        q = ik(q, start + (end - start) * i / n)
        out.append(q)
    return out


class PickPlaceServer(Node):
    def __init__(self):
        super().__init__("pick_place")
        group = ReentrantCallbackGroup()
        self.q = None                       # the 7 arm joints, from /joint_states
        self.block = {}                     # block letter -> (x, y, z), ground truth from Gazebo
        self.held = None                    # (letter, offset from the hand) while a block is in the gripper
        self.create_subscription(JointState, "/joint_states", self.on_joints, 10, callback_group=group)
        for k in BLOCKS:
            self.create_subscription(PoseStamped, f"/model/block_{k}/pose",
                                     lambda m, k=k: self.block.__setitem__(k, (m.pose.position.x, m.pose.position.y, m.pose.position.z)),
                                     10, callback_group=group)
        self.arm = ActionClient(self, FollowJointTrajectory, "/joint_trajectory_controller/follow_joint_trajectory",
                                callback_group=group)
        self.gripper = ActionClient(self, ParallelGripperCommand, "/robotiq_gripper_controller/gripper_cmd",
                                    callback_group=group)
        self.set_pose = self.create_client(SetEntityPose, "/world/lab/set_pose", callback_group=group)
        self.server = ActionServer(self, PickPlace, "pick_place", execute_callback=self.execute,
                                   callback_group=group)
        threading.Thread(target=self.carry_loop, daemon=True).start()
        self.get_logger().info("pick_place is ready")

    # ---- state ----------------------------------------------------------------------------------------------
    def on_joints(self, msg):
        pos = dict(zip(msg.name, msg.position))
        if all(j in pos for j in JOINTS):
            self.q = np.array([pos[j] for j in JOINTS])

    def hand(self):
        return gen3.fk(self.q)[:3, 3]

    # ---- the simulated grip -----------------------------------------------------------------------------------
    def move_block(self, letter, pos):
        req = SetEntityPose.Request()
        req.entity = Entity(name=f"block_{letter}", type=Entity.MODEL)
        req.pose.position.x, req.pose.position.y, req.pose.position.z = (float(v) for v in pos)
        req.pose.orientation.w = 1.0
        self.set_pose.call_async(req)

    def carry_loop(self):
        """While a block is held, put it at the hand plus the offset it had when it was grasped, 50 times a second."""
        while rclpy.ok():
            held = self.held
            if held is not None and self.q is not None:
                self.move_block(held[0], self.hand() + held[1])
            time.sleep(0.02)

    # ---- motion ---------------------------------------------------------------------------------------------
    def wait(self, future, what, timeout):
        t0 = time.time()
        while not future.done():
            if time.time() - t0 > timeout:
                raise RuntimeError(f"timeout: {what}")
            time.sleep(0.01)
        return future.result()

    def follow(self, qs, durations):
        """Send the joint positions qs, reached at the given times (s) after the start, and wait until done."""
        if not self.arm.wait_for_server(timeout_sec=5.0):
            raise RuntimeError("no joint_trajectory_controller action server")
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINTS
        for q, t in zip(qs, durations):
            point = JointTrajectoryPoint(positions=[float(v) for v in q])
            point.time_from_start = Duration(sec=int(t), nanosec=int((t % 1) * 1e9))
            goal.trajectory.points.append(point)
        handle = self.wait(self.arm.send_goal_async(goal), "arm goal accepted", 5)
        if not handle.accepted:
            raise RuntimeError("the arm refused the trajectory")
        result = self.wait(handle.get_result_async(), "arm trajectory", durations[-1] + 15)
        if result.result.error_code != 0:
            raise RuntimeError(f"trajectory failed: {result.result.error_string}")

    def straight(self, end):
        """Move the hand to `end` in a straight line at SPEED."""
        start = self.hand()
        qs = line(self.q, start, end)
        total = np.linalg.norm(np.array(end) - start)
        times = [0.3 + total * (i + 1) / len(qs) / SPEED for i in range(len(qs))]
        self.follow(qs, times)

    def jump(self, pos):
        """Move the hand to pos by the shortest way in joint space (used when the arm is not yet in the working
        shape, for example at the start, when it stands straight up)."""
        q = READY_Q.copy()
        for p in line(q, READY_POS, pos):          # walk from the ready pose to pos, so the shape stays tidy
            q = p
        delta = np.abs(q - self.q).max()
        self.follow([q], [max(3.0, delta / 0.4)])

    def check_reachable(self, *points):
        """Raise an error, before anything moves, if the hand cannot reach one of these places pointing down."""
        for pos in points:
            q = READY_Q.copy()
            for p in line(q, READY_POS, pos):
                q = p

    def go_above(self, x, y):
        near_hover = self.hand()[2] > HOVER_Z - 0.03 and abs(self.q[2] - Q3) < 0.05
        if near_hover:
            self.straight((x, y, HOVER_Z))
        else:
            self.jump((x, y, HOVER_Z))

    def grip(self, position):
        if not self.gripper.wait_for_server(timeout_sec=5.0):
            raise RuntimeError("no gripper action server")
        goal = ParallelGripperCommand.Goal()
        goal.command.name = ["robotiq_85_left_knuckle_joint"]
        goal.command.position = [float(position)]
        handle = self.wait(self.gripper.send_goal_async(goal), "gripper goal accepted", 5)
        self.wait(handle.get_result_async(), "gripper", 10)

    # ---- the action -------------------------------------------------------------------------------------------
    def execute(self, goal_handle):
        req = goal_handle.request
        feedback = PickPlace.Feedback()

        def stage(name):
            feedback.stage = name
            goal_handle.publish_feedback(feedback)
            self.get_logger().info(name)

        def fail(message):
            self.get_logger().error(message)
            goal_handle.abort()
            return PickPlace.Result(success=False, message=message)

        if req.block not in self.block or self.q is None:
            return fail(f"unknown block '{req.block}', or no joint states yet")
        bx, by, bz = self.block[req.block]
        try:
            # refuse at once, with the arm still, a request the hand cannot carry out
            self.check_reachable((bx, by, HOVER_Z), (bx, by, bz + HAND_ABOVE_BLOCK),
                                 (req.x, req.y, HOVER_Z), (req.x, req.y, req.z + HAND_ABOVE_BLOCK))
            stage("open")
            self.grip(GRIP_OPEN)
            stage("above")
            self.go_above(bx, by)
            stage("descend")
            self.straight((bx, by, bz + HAND_ABOVE_BLOCK))
            stage("grasp")
            self.grip(GRIP_CLOSED)
            self.held = (req.block, np.array(self.block[req.block]) - self.hand())     # the grip begins
            stage("lift")
            self.straight((bx, by, HOVER_Z))
            stage("transit")
            self.straight((req.x, req.y, HOVER_Z))
            stage("lower")
            self.straight((req.x, req.y, req.z + HAND_ABOVE_BLOCK))
            stage("release")
            self.held = None                                                               # the grip ends
            time.sleep(0.05)
            self.move_block(req.block, (req.x, req.y, req.z))
            self.grip(GRIP_OPEN)
            stage("retreat")
            self.straight((req.x, req.y, HOVER_Z))
        except Exception as error:                  # noqa: BLE001 (any failure ends the action the same way)
            if self.held is not None:               # failed with a block in the gripper: put it back where it was
                self.held = None
                time.sleep(0.05)
                self.move_block(req.block, (bx, by, bz))
            return fail(str(error))
        goal_handle.succeed()
        return PickPlace.Result(success=True, message=f"block {req.block} is at ({req.x:.3f}, {req.y:.3f}, {req.z:.3f})")


def main():
    rclpy.init()
    node = PickPlaceServer()
    executor = MultiThreadedExecutor(num_threads=6)
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
