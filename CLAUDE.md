# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Planning stage. The repo holds only `PLAN.md` (course outline and decisions), `README.md`, and a Docker launch script. There is no build system, linter, or test suite yet. `lessons/` and `code/` (below) do not exist yet.

## What this is

A hands-on course for ROS 2 (Jazzy) and the Kinova Gen3 7-DoF arm, meant to be shared with colleagues. Simulation uses ROS 2 tools only (ros2_control mock components + RViz, Gazebo Harmonic via `ros_gz`); Isaac Sim was dropped from scope. `PLAN.md` is the source of truth for lesson order, scope and rules. Read it before adding content.

Planned layout (from PLAN.md):
- `lessons/NN-name.html`: static, self-contained HTML lessons (no external dependencies)
- `code/NN-name/`: runnable code for each lesson
- Parts: A (ROS 2 basics), B (Kinova Gen3, MoveIt 2), C (simulation with Gazebo), D (symbols to motion), E (optional: the GR-Blocks paper on robots)

Lesson rules: every lesson follows Goal / Concepts / Do it / Check / Exercise (answer at the bottom) / Recap. One new idea at a time, nothing used before it is taught, every number/formula shown. Pace is one lesson at a time: the author runs it and reports back before the next is written. Commands in a lesson must be run and verified before handing over.

## Running the environment

`docker/run_ros2.sh [cmd...]` opens a shell (or runs the given command, e.g. `docker/run_ros2.sh ros2 topic list`) in `ros:jazzy-ros-base` on the host network, with `ROS_DOMAIN_ID` (default 0) and the repo mounted read-write at `/workspace`.

Non-obvious constraints in the script (keep them when editing):
- `FASTDDS_BUILTIN_TRANSPORTS=UDPv4` and `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`: the default shared-memory transport cannot cross container boundaries (topics are listed but no data arrives).
- The script does not yet pass an X display, so GUI tools (RViz, Gazebo) will need that added when the lessons reach them.
