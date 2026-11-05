#!/usr/bin/env bash
# Open a shell in the course container (ROS 2 Jazzy + Kinova workspace + Gazebo + MoveIt), repo mounted at /workspace.
# With arguments, runs them as a command instead (e.g. docker/run_ros2.sh ros2 topic list).
# Build the image first: docker build -t ros2-tutorial:jazzy docker/    Check the machine: scripts/check_machine.sh
set -euo pipefail

IMAGE="${IMAGE:-ros2-tutorial:jazzy}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOMAIN="${ROS_DOMAIN_ID:-0}"

if [ "$#" -eq 0 ]; then CMD=(bash); else CMD=("$@"); fi
TTY=(); if [ -t 0 ]; then TTY=(-it); fi   # only ask for a terminal when there is one

# GUI tools (RViz, Gazebo): share the X display through a copy of your X authorization (no `xhost +`).
GUI=()
if [ -n "${DISPLAY:-}" ] && command -v xauth >/dev/null; then
  XAUTH="$(mktemp)"; chmod 644 "$XAUTH"
  xauth nlist "$DISPLAY" 2>/dev/null | sed -e 's/^..../ffff/' | xauth -f "$XAUTH" nmerge - 2>/dev/null || true
  GUI=(-e DISPLAY="$DISPLAY" -e XAUTHORITY=/tmp/.xauth -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v "$XAUTH":/tmp/.xauth:ro)
fi
# Use the NVIDIA GPU when Docker has the runtime for it; otherwise rendering falls back to software.
GPU=(); if docker info 2>/dev/null | grep -qi nvidia; then GPU=(--gpus all -e NVIDIA_DRIVER_CAPABILITIES=all); fi

# FASTDDS_BUILTIN_TRANSPORTS=UDPv4: the default shared-memory transport cannot cross container boundaries
# (topics are listed but no data arrives), so force UDP.
# Run as your own user, so files created in /workspace (builds, new packages) belong to you, not to root.
# HOME=/tmp gives ROS and Gazebo a writable home (logs, caches); it is discarded with the container.
exec docker run "${TTY[@]}" --rm --network=host "${GUI[@]}" "${GPU[@]}" \
  --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -e ROS_DOMAIN_ID="$DOMAIN" \
  -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
  -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
  -v "$REPO":/workspace -w /workspace \
  "$IMAGE" bash -c 'source /opt/ros/jazzy/setup.bash && source /opt/kortex_ws/install/setup.bash && exec "$@"' _ "${CMD[@]}"
