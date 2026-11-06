#!/usr/bin/env bash
# Checks that this machine can run the course. Run it before lesson A0 (and again if something misbehaves).
#   scripts/check_machine.sh            host checks, plus image checks if the image is built
#   IMAGE=name:tag scripts/check_machine.sh
#   scripts/check_machine.sh --local    for a local ROS 2 install (no Docker): checks Ubuntu 24.04 / Mint 22 and the installed ROS 2
# Exit code: 0 = ready (warnings allowed), 1 = at least one FAIL.
# PASS = fine, WARN = works but not recommended or optional, FAIL = the course will not work.
set -u

IMAGE="${IMAGE:-ros2-tutorial:jazzy}"
LOCAL=0; [ "${1:-}" = "--local" ] && LOCAL=1
MIN_CORES=4;  REC_CORES=8
MIN_RAM_GB=12; REC_RAM_GB=16
MIN_DISK_GB=30

fails=0; warns=0
pass() { printf '  [PASS] %s\n' "$*"; }
warn() { printf '  [WARN] %s\n' "$*"; warns=$((warns+1)); }
fail() { printf '  [FAIL] %s\n' "$*"; fails=$((fails+1)); }
section() { printf '\n%s\n' "$*"; }

section "Operating system"
if [ "$(uname -s)" = "Linux" ]; then
  . /etc/os-release 2>/dev/null
  pass "Linux (${PRETTY_NAME:-unknown distribution})"
  # The scripts use --network=host, which only shares the real host network on Linux.
else
  fail "Not Linux: the Docker scripts rely on host networking and X11, which need a Linux host."
fi

section "CPU, memory, disk"
cores=$(nproc 2>/dev/null || echo 0)
if   [ "$cores" -ge "$REC_CORES" ]; then pass "$cores CPU cores"
elif [ "$cores" -ge "$MIN_CORES" ]; then warn "$cores CPU cores ($REC_CORES recommended: the image build takes long, Gazebo is CPU-heavy)"
else fail "$cores CPU cores (need at least $MIN_CORES)"; fi

ram_gb=$(awk '/MemTotal/ {printf "%d", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo 0)
if   [ "$ram_gb" -ge "$REC_RAM_GB" ]; then pass "${ram_gb} GB RAM"
elif [ "$ram_gb" -ge "$MIN_RAM_GB" ]; then warn "${ram_gb} GB RAM ($REC_RAM_GB recommended; the build may need fewer parallel workers)"
else fail "${ram_gb} GB RAM (need at least $MIN_RAM_GB)"; fi

if [ "$LOCAL" = 1 ]; then
  disk_root="$HOME"; disk_what="in your home folder"
else
  disk_root=$(docker info --format '{{.DockerRootDir}}' 2>/dev/null || echo /var/lib/docker)
  [ -d "$disk_root" ] || disk_root=/
  disk_what="where Docker stores images"
fi
disk_gb=$(df --output=avail -BG "$disk_root" 2>/dev/null | tail -1 | tr -dc '0-9')
if [ "${disk_gb:-0}" -ge "$MIN_DISK_GB" ]; then pass "${disk_gb} GB free $disk_what"
else fail "${disk_gb:-0} GB free $disk_what (need at least $MIN_DISK_GB: ROS 2, Gazebo and the Kinova build, or the Docker image and its build layers)"; fi

if [ "$LOCAL" = 0 ]; then
section "Docker"
if ! command -v docker >/dev/null; then
  fail "docker is not installed (see lesson A0)"
elif ! docker info >/dev/null 2>&1; then
  fail "docker is installed but 'docker info' fails: is the daemon running, and are you in the 'docker' group?"
else
  pass "docker works ($(docker version --format '{{.Server.Version}}' 2>/dev/null))"
  if docker buildx version >/dev/null 2>&1; then pass "docker buildx available"; else warn "docker buildx not found (the build still works, more slowly)"; fi
fi
fi

section "Graphics (RViz and Gazebo windows)"
if [ -n "${XDG_SESSION_TYPE:-}" ] && [ "$XDG_SESSION_TYPE" = "wayland" ] && [ -z "${DISPLAY:-}" ]; then
  fail "Wayland session without XWayland: no \$DISPLAY"
elif [ -z "${DISPLAY:-}" ]; then
  fail "\$DISPLAY is not set: run this from a desktop terminal, not a plain SSH session"
else
  pass "\$DISPLAY=$DISPLAY (session: ${XDG_SESSION_TYPE:-unknown})"
  command -v xauth >/dev/null && pass "xauth installed" || fail "xauth not installed (sudo apt install xauth)"
  [ -d /tmp/.X11-unix ] && pass "/tmp/.X11-unix present" || fail "/tmp/.X11-unix missing"
fi

if command -v nvidia-smi >/dev/null && nvidia-smi -L >/dev/null 2>&1; then
  pass "NVIDIA GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
  if [ "$LOCAL" = 1 ]; then :
  elif docker info 2>/dev/null | grep -qi nvidia; then pass "NVIDIA container runtime registered with Docker"
  else warn "NVIDIA container runtime not registered: containers cannot use the GPU (install nvidia-container-toolkit)"; fi
else
  warn "No NVIDIA GPU found: Gazebo falls back to software rendering (slow, but the course still works)"
fi

section "Network"
# The ROS package server only answers on plain http, and only for real repository paths.
for url in $([ "$LOCAL" = 0 ] && echo https://registry-1.docker.io/v2/) https://github.com http://packages.ros.org/ros2/ubuntu/dists/noble/InRelease; do
  code=$(curl -s -m 8 -o /dev/null -w '%{http_code}' -I "$url")
  # 401 from the Docker registry means "reachable, login required"
  if [ "$code" = "200" ] || [ "$code" = "301" ] || [ "$code" = "302" ] || [ "$code" = "401" ]; then pass "can reach $url"
  else fail "cannot reach $url (HTTP $code; needed to build the image)"; fi
done

if [ "$LOCAL" = 1 ]; then
section "Local ROS 2 install"
. /etc/os-release 2>/dev/null
if [ "${UBUNTU_CODENAME:-${VERSION_CODENAME:-}}" = "noble" ]; then pass "Ubuntu 24.04 base (${PRETTY_NAME:-unknown})"
else fail "not Ubuntu 24.04 or Linux Mint 22 (${PRETTY_NAME:-unknown}): ROS 2 Jazzy binaries need 'noble'"; fi
if [ -f /opt/ros/jazzy/setup.bash ]; then
  pass "ROS 2 Jazzy is installed in /opt/ros/jazzy"
  kws="${KORTEX_WS:-$HOME/kortex_ws}"
  lrun() { bash -c "source /opt/ros/jazzy/setup.bash; [ -f $kws/install/setup.bash ] && source $kws/install/setup.bash; export ROS_DOMAIN_ID=77 RMW_IMPLEMENTATION=rmw_fastrtps_cpp; $1"; }
  if lrun 'ros2 pkg prefix kortex_bringup' >/dev/null 2>&1; then pass "Kinova packages are built ($kws)"
  else fail "Kinova packages not found: build them as in lesson A0 (expected in $kws, or set KORTEX_WS)"; fi
  if lrun 'ros2 pkg prefix gz_ros2_control && gz sim --versions' >/dev/null 2>&1; then pass "Gazebo and gz_ros2_control are installed"
  else fail "Gazebo or gz_ros2_control missing: run the rosdep step of lesson A0 again"; fi
  # Two separate programs must exchange data.
  lrun "ros2 topic pub -r 5 /check_machine std_msgs/msg/String '{data: hello}'" >/dev/null 2>&1 & pubpid=$!
  sleep 3
  if lrun 'timeout 15 ros2 topic echo /check_machine --once' 2>/dev/null | grep -q hello; then pass "two ROS 2 programs exchange topic data"
  else fail "topic data did not arrive between two programs (check ROS_DOMAIN_ID and the firewall)"; fi
  pkill -P "$pubpid" 2>/dev/null; kill "$pubpid" 2>/dev/null
  if [ -n "${DISPLAY:-}" ]; then
    lrun 'timeout 15 rviz2' >/dev/null 2>&1; rc=$?
    if [ "$rc" -eq 124 ]; then pass "RViz opens a window"
    else fail "RViz could not start (exit code $rc): check DISPLAY and your graphics driver"; fi
  else
    warn "no display: skipped the RViz window test"
  fi
else
  fail "ROS 2 Jazzy is not installed (/opt/ros/jazzy missing): follow lesson A0, local install"
fi
else
section "Course image ($IMAGE)"
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  warn "image not built yet: run 'docker build -t $IMAGE docker/' (lesson A0), then run this script again"
else
  pass "image present ($(docker images "$IMAGE" --format '{{.Size}}' | head -1))"
  run() { docker run --rm --network=host -e ROS_DOMAIN_ID=77 -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
            -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 "$IMAGE" bash -c "source /opt/ros/jazzy/setup.bash; source /opt/kortex_ws/install/setup.bash; $1"; }
  if run 'ros2 pkg prefix kortex_bringup && ros2 pkg prefix kortex_moveit_config' >/dev/null 2>&1 \
     || run 'ros2 pkg prefix kortex_bringup' >/dev/null 2>&1; then pass "Kinova packages are in the image"
  else fail "Kinova packages not found in the image: rebuild it"; fi
  if run 'ros2 pkg prefix gz_ros2_control && gz sim --versions' >/dev/null 2>&1; then pass "Gazebo and gz_ros2_control are in the image"
  else fail "Gazebo or gz_ros2_control missing from the image: rebuild it"; fi

  # Two separate containers must exchange data: this is what fails if shared memory is used instead of UDP.
  cid=$(docker run -d --rm --network=host -e ROS_DOMAIN_ID=77 -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
          -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 "$IMAGE" bash -c \
          "source /opt/ros/jazzy/setup.bash; ros2 topic pub -r 5 /check_machine std_msgs/msg/String '{data: hello}'" 2>/dev/null)
  sleep 3
  if run 'timeout 15 ros2 topic echo /check_machine --once' 2>/dev/null | grep -q hello; then pass "two containers exchange topic data (UDP transport)"
  else fail "topic data did not cross between two containers (check firewall, ROS_DOMAIN_ID, FASTDDS_BUILTIN_TRANSPORTS)"; fi
  [ -n "$cid" ] && docker kill "$cid" >/dev/null 2>&1

  # A window must open from inside a container (needs X access and OpenGL): run rviz2 for 15 s.
  # Exit code 124 means it was still running when the timeout stopped it, i.e. it started fine.
  if [ -n "${DISPLAY:-}" ] && command -v xauth >/dev/null; then
    xa=$(mktemp); : > "$xa"
    xauth nlist "$DISPLAY" 2>/dev/null | sed -e 's/^..../ffff/' | xauth -f "$xa" nmerge - 2>/dev/null; chmod 644 "$xa"
    gpu=(); docker info 2>/dev/null | grep -qi nvidia && gpu=(--gpus all -e NVIDIA_DRIVER_CAPABILITIES=all)
    docker run --rm "${gpu[@]}" -e DISPLAY="$DISPLAY" -e XAUTHORITY=/tmp/.xauth \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v "$xa":/tmp/.xauth:ro "$IMAGE" bash -c \
        'source /opt/ros/jazzy/setup.bash; timeout 15 rviz2' >/dev/null 2>&1
    rc=$?
    if [ "$rc" -eq 124 ]; then pass "RViz opens a window from inside the container"
    else fail "RViz could not start from the container (exit code $rc): check DISPLAY, xauth and the GPU options"; fi
    rm -f "$xa"
  else
    warn "no display: skipped the RViz window test"
  fi
fi
fi

section "Summary"
printf '  %d failure(s), %d warning(s)\n' "$fails" "$warns"
if [ "$fails" -eq 0 ]; then echo "  This machine can run the course."; else echo "  Fix the FAIL lines above before continuing."; fi
[ "$fails" -eq 0 ]
