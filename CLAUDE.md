# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Planning and environment stage. The repo holds `PLAN.md` (course outline, decisions, and the environment test results), `README.md`, `docker/` (Dockerfile and run script) and `scripts/check_machine.sh`. There are no lessons yet, and no lint or test suite. `lessons/` and `code/` (below) do not exist yet.

## What this is

A hands-on course for ROS 2 (Jazzy) and the Kinova Gen3 7-DoF arm, meant to be shared with colleagues. Simulation uses ROS 2 tools only (ros2_control mock components + RViz, Gazebo Harmonic via `ros_gz`); Isaac Sim was dropped from scope. `PLAN.md` is the source of truth for lesson order, scope and rules. Read it before adding content.

Planned layout (from PLAN.md):
- `lessons/NN-name.html`: static, self-contained HTML lessons (no external dependencies)
- `code/NN-name/`: runnable code for each lesson
- Parts: A (ROS 2 basics), B (Kinova Gen3, MoveIt 2), C (simulation with Gazebo), D (symbols to motion), E (optional: the GR-Blocks paper on robots)

Lesson rules: every lesson follows Goal / Concepts / Do it / Check / Exercise (answer at the bottom) / Recap. One new idea at a time, nothing used before it is taught, every number/formula shown. Pace is one lesson at a time: the author runs it and reports back before the next is written. Commands in a lesson must be run and verified before handing over.

## Running the environment

- `scripts/check_machine.sh`: checks the host (OS, CPU, RAM, disk, Docker, display/GPU, network) and, if the image exists, the image (Kinova packages, Gazebo, container-to-container DDS, an RViz window). Exit code 1 on any FAIL. Keep it in step with the Dockerfile and run script.
- `docker build -t ros2-tutorial:jazzy docker/`: builds the course image (ROS 2 Jazzy + Gazebo Harmonic + MoveIt 2 + `ros2_kortex` `jazzy` branch in `/opt/kortex_ws`). About 8.65 GB; the colcon step takes a few minutes.
- `docker/run_ros2.sh [cmd...]`: shell (or the given command, e.g. `docker/run_ros2.sh ros2 topic list`) in that image, host network, `ROS_DOMAIN_ID` (default 0), repo mounted read-write at `/workspace`, X display and NVIDIA GPU passed through when available. Sources both `/opt/ros/jazzy` and `/opt/kortex_ws`.

Non-obvious constraints (keep them when editing):
- `FASTDDS_BUILTIN_TRANSPORTS=UDPv4` and `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`: the default shared-memory transport cannot cross container boundaries (topics are listed but no data arrives).
- `packages.ros.org` answers on plain `http://` only.
- Gazebo sim: `ros2 launch kortex_bringup kortex_sim_control.launch.py sim_gazebo:=true gripper:=robotiq_2f_85 use_sim_time:=true launch_rviz:=false`. The `gripper` default is empty (no gripper), and the gripper action type is `ParallelGripperCommand`, not `GripperCommand`. The launch hardcodes the Gazebo GUI, so it needs a display. Details in PLAN.md, "Environment test results".
