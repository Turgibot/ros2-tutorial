# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Planning and environment stage. The repo holds `PLAN.md` (course outline, decisions, and the environment test results), `README.md`, `docker/` (Dockerfile and run script) and `scripts/check_machine.sh`. Lessons A0 to A6 are written (`lessons/`, `code/01-nodes-topics/`, `code/02-messages-services/`, `code/03-actions/`, `code/04-parameters-launch/`, `code/05-packages/`, `code/06-frames/`). There is no lint or test suite.

## What this is

A hands-on course for ROS 2 (Jazzy) and the Kinova Gen3 7-DoF arm, meant to be shared with colleagues. Simulation uses ROS 2 tools only (ros2_control mock components + RViz, Gazebo Harmonic via `ros_gz`); Isaac Sim was dropped from scope. `PLAN.md` is the source of truth for lesson order, scope and rules. Read it before adding content.

Layout:
- Environment toggle: A0 offers Docker (default) or a local install (Ubuntu 24.04 or Linux Mint 22 only). Wrap env-specific blocks in `<div class="env docker">` / `<div class="env local">` (or the class on a `p`, `pre`, `li`, `span`). `lesson.js` adds the Docker / Local install switch next to the Python/C++ one; CSS relabels the `container` badge as `terminal` in local mode. `scripts/check_machine.sh --local` checks a local install. Only A0 differs substantially; later lessons only wrap the "open a terminal" steps. The local install steps in A0 were NOT run on a machine with a local install (the author uses Docker): say so when editing.
- `lessons/`: the static website. `index.html` (contents), one file per lesson (`a0-environment.html`, `a1-nodes-topics.html` and `a2-messages-services.html`, `a3-actions.html`, `a4-parameters-launch.html` and `a5-packages-workspaces.html` and `a6-frames-tf2.html` exist so far), `assets/style.css`, `assets/lesson.js`, `img/` for screenshots. No build step, no external dependencies; preview by opening the file in a browser.
- `code/NN-name/`: runnable code for each lesson, with `py/` and `cpp/` (a colcon package) subfolders. Every lesson with code supports both languages: wrap language-specific blocks in `<div class="lang py">` / `<div class="lang cpp">` (or an inline `class="lang py"` span/code). `lesson.js` adds the Python/C++ switch to the header on pages that have `.lang` elements and remembers the choice. Run both variants before handing over.
- Parts: A (ROS 2 basics), B (Kinova Gen3, MoveIt 2), C (simulation with Gazebo), D (symbols to motion), E (optional: the GR-Blocks paper on robots)

Writing a lesson (follow `lessons/a0-environment.html` as the template):
- Command blocks are `<pre class="cmd"><code>...</code></pre>`; `lesson.js` adds the Copy button, so put only what the reader should paste in them (no `$` prompt). Output is `<pre class="out">`, which has no button. Escape `<`, `>`, `&` in HTML.
- ROS 2 work happens in a container shell: tell the reader to open a new terminal, run `docker/run_ros2.sh` (no arguments) and type the commands at that prompt. Do not write one-shot `docker/run_ros2.sh ros2 ...` commands in lessons. Use a new `host` block for the shell start, then `container` blocks.
- Mark where each command runs with `<span class="where host">host</span>` or `<span class="where box">container</span>`.
- Expected output and screenshots must come from real runs, not be written from memory. `scripts/screenshot_window.py <title-substring> <out.png>` saves one X window (not the desktop) as a PNG into `lessons/img/`. Say so to the user when a block was not run (A0: Docker install, `usermod`, NVIDIA toolkit, `git clone` of the public repo).
- Each lesson ends with a pager: link back to the contents, and a link to the next lesson once it exists (a dashed "coming soon" box until then; update the previous lesson's pager when adding a lesson, and the status in `index.html`).
- Check a page by rendering it with `google-chrome --headless=new --screenshot=...`.

Lesson rules: every lesson follows Goal / Concepts / Do it / Check / Exercise (answer at the bottom) / Recap. One new idea at a time, nothing used before it is taught, every number/formula shown. Pace is one lesson at a time: the author runs it and reports back before the next is written. Commands in a lesson must be run and verified before handing over.

## Running the environment

- `scripts/check_machine.sh`: checks the host (OS, CPU, RAM, disk, Docker, display/GPU, network) and, if the image exists, the image (Kinova packages, Gazebo, container-to-container DDS, an RViz window). Exit code 1 on any FAIL. Keep it in step with the Dockerfile and run script.
- `docker build -t ros2-tutorial:jazzy docker/`: builds the course image (ROS 2 Jazzy + Gazebo Harmonic + MoveIt 2 + `ros2_kortex` `jazzy` branch in `/opt/kortex_ws`). About 8.65 GB; the colcon step takes a few minutes.
- `docker/run_ros2.sh [cmd...]`: shell (or the given command, e.g. `docker/run_ros2.sh ros2 topic list`) in that image, host network, `ROS_DOMAIN_ID` (default 0), repo mounted read-write at `/workspace`, X display and NVIDIA GPU passed through when available. Sources both `/opt/ros/jazzy` and `/opt/kortex_ws`.

Non-obvious constraints (keep them when editing):
- `FASTDDS_BUILTIN_TRANSPORTS=UDPv4` and `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`: the default shared-memory transport cannot cross container boundaries (topics are listed but no data arrives).
- `packages.ros.org` answers on plain `http://` only.
- Gazebo sim: `ros2 launch kortex_bringup kortex_sim_control.launch.py sim_gazebo:=true gripper:=robotiq_2f_85 use_sim_time:=true launch_rviz:=false`. The `gripper` default is empty (no gripper), and the gripper action type is `ParallelGripperCommand`, not `GripperCommand`. The launch hardcodes the Gazebo GUI, so it needs a display. Details in PLAN.md, "Environment test results".
