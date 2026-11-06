# ros2-tutorial: plan

A hands-on course for people new to ROS 2 and the Kinova Gen3 arm, meant to be shared with colleagues.

## Decisions
- Scope: general ROS 2, with two Kinova Gen3 (7-DoF) arms in a ROS 2 simulation as the capstone. The GR-Blocks paper
  (goal recognition + helpful R_ing) becomes an optional last part, not the spine.
- Format: a static website in `lessons/` (open `lessons/index.html`, or host the folder anywhere). One HTML file per
  lesson (`a0-environment.html`, ...), each linking to the previous and next lesson, with shared `assets/style.css`
  and `assets/lesson.js` (copy button on every command block) and screenshots in `img/`. No build step, no external
  dependencies. Runnable code in `code/NN-name/`.
- From scratch: the course covers every step needed to reproduce the setup on a clean machine (install Docker, build
  the image, build the Kinova workspace, run the sim). Nothing is assumed, and every setup problem we hit is documented
  with its fix.
- Setup: one Docker image, `ros2-tutorial:jazzy`, built from `docker/Dockerfile`: ROS 2 Jazzy, Gazebo Harmonic, MoveIt 2
  and the Kinova `ros2_kortex` workspace (`jazzy` branch, built from source). Host network, `ROS_DOMAIN_ID`.
- Kinova software: `ros2_kortex` (`kortex_description`, `kortex_bringup`, `kortex_moveit_config`, `kortex_driver`).
  The same launch files and controllers (`joint_trajectory_controller`, `twist_controller`, Robotiq `gripper_cmd`)
  serve mock hardware, Gazebo and the real arm; this is the basis of the digital twin.
- Goal: a digital twin close to the real arm, able to run alongside it and behave the same. Sim and real are compared
  by recording `/joint_states` from both. Open questions are listed under "Digital twin" below.
- Simulation: ROS 2 tools only, no Isaac Sim. Fake hardware (`ros2_control` mock components) with RViz for the arm alone,
  Gazebo (Harmonic, via `ros_gz`) for physics, blocks and grasping.
- Perception: ground-truth poses from the simulator. Real arms later through the same ROS interfaces.

## Lesson shape (every lesson)
1. Goal  2. Concepts (only the new ones, with a picture)  3. Do it (commands + expected output)
4. Check (I run it before handing over)  5. Exercise (answer at the bottom)  6. Recap
Rules: one new idea at a time; nothing used before it is taught; every number/formula shown.

## Lessons
**Part A, ROS 2 basics (before any robot), milestone 0**
- A0 The container for this project: first run `scripts/check_machine.sh` (checks OS, CPU, RAM, disk, Docker, display/GPU,
  network, and, once the image exists, that the Kinova packages, Gazebo, container-to-container DDS and an RViz window
  all work). Then install Docker, read and build `docker/Dockerfile`, run the container, enter and stop it. Where files live (mounted repo), how GUI tools (RViz, Gazebo) reach the display, and why the network
  settings (host network, `ROS_DOMAIN_ID`, UDP transport) matter once several containers or machines are involved.
  Checked by running two shells in the container and seeing `ros2 topic list`.
- A1 Nodes and topics: a talker/listener in Python; `ros2 node/topic list/echo`.
- A2 Messages and services: custom message for a symbolic action (`unstack F W`); a service call.
- A3 Actions: long-running goals with feedback and cancel (what a pick-and-place will be).
- A4 Parameters and launch files.
- A5 Packages and workspaces: `package.xml`, `CMakeLists.txt`/`setup.py`, `colcon build`, overlays, sourcing order.
- A6 Frames and TF2: what a coordinate frame is, `base_link`, tool frame, viewing in RViz.
- A7 ros2_control in one lesson: controllers, joint states, command interfaces (concept only).

**Part B, the Kinova Gen3, milestone 1**
- B0 Setup of the Kinova workspace: what `ros2_kortex` is, how the Dockerfile builds it (`vcs import`, `rosdep install`,
  `colcon build`), the packages it contains, and how to rebuild one package. Known problems and fixes: `kortex_api`
  Jazzy binaries are not released (build from source); protobuf mismatch with Gazebo (build in two steps); limit
  `--parallel-workers` to avoid running out of memory. Checked with `ros2 launch kortex_description view_robot.launch.py`.
  (Measured: the full workspace is 76 packages, about 3.5 minutes to compile on 32 cores; the image is 8.65 GB.)
- B1 The arm: 7 joints, redundancy, joint limits, gripper; read the URDF (`dof:=7`, `gripper:=robotiq_2f_85`) and see it in RViz.
- B2 Forward kinematics by hand for a 2-link case, then the Gen3 in TF; what "end effector pose" means.
- B3 Inverse kinematics and why 7 DoF has many solutions (the null space).
- B4 MoveIt 2: planning groups, planning scene, collision objects; plan and execute with fake hardware
  (`use_fake_hardware:=true`, the shipped `kinova_gen3_7dof_robotiq_2f_85_moveit_config`).
- B5 Two arms in one scene: two groups, namespaces, a shared collision world (`kortex_dual_robots.xacro`, joint-name
  `prefix`; controller YAMLs and MoveIt config need hand editing, to be checked).

**Part C, Simulation with ROS 2 tools, milestone 2**
- C1 Gazebo basics: worlds, SDF, models, physics, play/pause; the `ros_gz` bridge and `/clock`.
- C2 Put the Gen3 in Gazebo (`kortex_sim_control.launch.py sim_gazebo:=true`), joints and the gripper, `gz_ros2_control`.
  The sim launch defaults to NO gripper: pass `gripper:=robotiq_2f_85` (the upstream README says otherwise). The
  gripper action is `control_msgs/action/ParallelGripperCommand` (the upstream README shows the old `GripperCommand`).
  See "Environment test results".
- C3 Build the table and lettered blocks in SDF; friction and mass for stable grasps.
- C4 Sensors and state over ROS: `/joint_states`, ground-truth block poses, a camera topic.
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

## Digital twin (open questions)
- `ros2_kortex` gives three backends behind the same controller names: mock hardware, Gazebo, the real driver
  (`robot_ip:=192.168.1.10`). Dynamics, latency and gripper behaviour still differ between them.
- Wrist camera in Gazebo: `/wrist_mounted_camera/{image,depth_image,points,camera_info}` exist on the Gazebo and ROS
  sides, but no image arrived within 40 s. Cause not found yet (render engine in the container? sensor needs a
  subscriber? a world without the sensor plugin?). Must be solved before any vision work.
- Mimic joints: only `robotiq_85_left_knuckle_joint` appears in `/joint_states`; the other finger joints are not
  reported. Whether blocks can be grasped is untested (upstream gz-sim issue 1684).
- MoveIt upstream recommends Cyclone DDS; our scripts force Fast DDS. Test which works, and for sim plus real together.
- Two-arm MoveIt config: only the dual-robot xacro exists upstream.
- Decide: does the twin follow the real arm's `/joint_states`, or run the same commands in parallel?
- Compare sim and real by recording `/joint_states` from both and plotting the difference.

## Environment test results
Tested 2026-11-05 on Ubuntu 24.04, 32 cores, 60 GB RAM, RTX 5080, Docker 29.1.3. Image built from `docker/Dockerfile`
(`ros2_kortex` `jazzy` branch, commit 462dab9; `ros2_robotiq_gripper` a74d007). Sim run with
`ros2 launch kortex_bringup kortex_sim_control.launch.py sim_gazebo:=true gripper:=robotiq_2f_85 use_sim_time:=true launch_rviz:=false`,
Gazebo GUI on the host display, Fast DDS over UDP, `ROS_DOMAIN_ID` 42 to 44.

Works:
- The image builds with no failures (76 packages). The protobuf two-step build was not needed.
- `scripts/check_machine.sh` passes on this machine, including container-to-container topic exchange and an RViz window.
- Gen3 7-DoF + Robotiq 2F-85 spawns in Gazebo. Active controllers: `joint_trajectory_controller`,
  `joint_state_broadcaster`, `robotiq_gripper_controller`. `/clock`, `/joint_states`, `/tf` (from `robot_state_publisher`) publish.
- Arm: a `FollowJointTrajectory` goal to `[0.5, 0.3, 0, -1.0, 0, 0.5, 0]` over 4 s succeeded; `joint_1` ended at 0.49999.
- Gripper: `ParallelGripperCommand` goals to 0.0, 0.8, 0.0 all succeeded and the knuckle joint followed (0.721 at start, then 0.0, 0.799, 0.0).

Problems and surprises:
- With default arguments the sim has no gripper, and the gripper controller fails to activate
  (`command interface 'robotiq_85_left_knuckle_joint/position' is not available`). Fix: `gripper:=robotiq_2f_85`.
- The README's gripper command (`control_msgs/action/GripperCommand`) fails with "rcl node's context is invalid";
  the server speaks `ParallelGripperCommand` with a `sensor_msgs/JointState` goal:
  `ros2 action send_goal /robotiq_gripper_controller/gripper_cmd control_msgs/action/ParallelGripperCommand "{command: {name: [robotiq_85_left_knuckle_joint], position: [0.0]}}"`.
- The gripper starts at 0.72 rad (almost closed) in Gazebo.
- `kortex_sim_control.launch.py` hardcodes the Gazebo GUI (`gz_args` has no `-s`), so a headless run needs a display.
- `tf2_echo base_link tool_frame` reported the frames as missing; probably because it ran without `use_sim_time`
  (not verified).
- Wrist camera: no image data (see Digital twin).

Not tested yet: MoveIt 2 (mock and Gazebo), RViz with the sim, the real driver, two arms, grasping a block, Cyclone DDS,
`ros2_kortex` `main` branch.
