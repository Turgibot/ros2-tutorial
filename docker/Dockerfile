# The course image: ROS 2 Jazzy + Gazebo Harmonic + MoveIt 2 + the Kinova ros2_kortex workspace, built from source.
# Build:  docker build -t ros2-tutorial:jazzy docker/
FROM ros:jazzy-ros-base
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
      git python3-vcstool python3-colcon-common-extensions python3-rosdep build-essential \
    && rm -rf /var/lib/apt/lists/*

# Kinova workspace. KORTEX_REF is the ros2_kortex branch/tag/commit to build.
ARG KORTEX_REF=jazzy
ENV KORTEX_WS=/opt/kortex_ws
WORKDIR $KORTEX_WS
RUN git clone --branch "$KORTEX_REF" https://github.com/Kinovarobotics/ros2_kortex.git src/ros2_kortex \
    && for f in ros2_kortex.jazzy.repos ros2_kortex-not-released.jazzy.repos simulation.jazzy.repos; do \
         vcs import src --skip-existing --input "src/ros2_kortex/$f"; done

# System dependencies (Gazebo Harmonic, MoveIt 2, ros2_control, ...) resolved from the package.xml files.
RUN apt-get update && rosdep update --rosdistro jazzy \
    && rosdep install --ignore-src --from-paths src -y -r \
    && rm -rf /var/lib/apt/lists/*

# Few parallel workers: the default can exhaust memory.
RUN source /opt/ros/jazzy/setup.bash \
    && colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release --parallel-workers 6

WORKDIR /workspace
