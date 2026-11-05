# ros2-tutorial: plan

A hands-on course for people new to ROS 2, Isaac Sim and the Kinova Gen3 arm, meant to be shared with colleagues.

## Decisions
- Scope: general ROS 2, with two Kinova Gen3 (7-DoF) arms in Isaac Sim as the capstone. The GR-Blocks paper
  (goal recognition + helpful R_ing) becomes an optional last part, not the spine.
- Format: static, self-contained HTML lessons (like GR-Blocks): `lessons/NN-name.html`, runnable code in `code/NN-name/`.
- Setup: ROS 2 Jazzy in Docker, Isaac Sim 6.1 in Docker, both on the host network with the same `ROS_DOMAIN_ID`.
- Perception: ground-truth poses from the simulator. Real arms later through the same ROS interfaces.

## Lesson shape (every lesson)
1. Goal  2. Concepts (only the new ones, with a picture)  3. Do it (commands + expected output)
4. Check (I run it before handing over)  5. Exercise (answer at the bottom)  6. Recap
Rules: one new idea at a time; nothing used before it is taught; every number/formula shown.

## Lessons
**Part A, ROS 2 basics (before any robot), milestone 0**
- A0 Containers for this project: what Docker gives us, the two containers (ROS 2 Jazzy, Isaac Sim), how they talk
  (host network, same `ROS_DOMAIN_ID`, UDP transport), where files live (mounted repo, caches), how to enter, stop
  and rebuild them. Checked with `ros2 topic echo /clock` against Isaac.
- A1 Nodes and topics: a talker/listener in Python; `ros2 node/topic list/echo`.
- A2 Messages and services: custom message for a symbolic action (`unstack F W`); a service call.
- A3 Actions: long-running goals with feedback and cancel (what a pick-and-place will be).
- A4 Parameters and launch files; packages, `colcon build`, workspaces.
- A5 Frames and TF2: what a coordinate frame is, `base_link`, tool frame, viewing in RViz.
- A6 ros2_control in one lesson: controllers, joint states, command interfaces (concept only).

**Part B, the Kinova Gen3, milestone 1**
- B1 The arm: 7 joints, redundancy, joint limits, gripper; read the URDF and see it in RViz.
- B2 Forward kinematics by hand for a 2-link case, then the Gen3 in TF; what "end effector pose" means.
- B3 Inverse kinematics and why 7 DoF has many solutions (the null space).
- B4 MoveIt 2: planning groups, planning scene, collision objects; plan and execute with fake hardware.
- B5 Two arms in one scene: two groups, namespaces, a shared collision world.

**Part C, Isaac Sim, milestone 2**
- C1 The Isaac GUI: stage, USD, prims, physics, play/stop.
- C2 Import the Gen3 (URDF -> USD), joints and drives, the gripper.
- C3 Build the table and lettered blocks (reuse `isaac/`), friction and mass for stable grasps.
- C4 The ROS 2 bridge and Action Graphs: `/clock`, `/joint_states`, joint commands, camera/pose topics.
- C5 Drive the simulated arm from MoveIt 2 through ros2_control.

**Part D, from symbols to motion, milestone 3**
- D1 Block poses -> towers: the world estimator and how a tower is read from heights.
- D2 A pick-and-place action server: approach, grasp, lift, place; waypoints and Cartesian paths.
- D3 Symbolic action -> motion: `unstack X Y`, `stack`, `putdown` as skills.

**Part E, the paper on robots, milestones 4 to 6**
- E1 Wrap the recognizer as a ROS 2 node; read the live posterior in RViz or a plot.
- E2 R_ed executes a whole word plan end to end.
- E3 R_ing: helper planner node (paper policy), then safe exposure.
- E4 Two arms at once: collision avoidance between them.
- E5 Handover and stacked-pair lifts.
- E6 Towards the real arms: what changes (hardware interface, safety limits, calibration).

Part E (the GR-Blocks paper on robots) is optional and lives at the end.

Pace: one lesson at a time; the author runs it and reports back before the next is written.
