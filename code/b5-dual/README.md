# B5: two arms in one scene

Code for lesson B5 (`lessons/b5-two-arms.html`). One colcon package, `b5_dual`:

- `config/`: the two-arm robot description (`dual.urdf.xacro`) and MoveIt configuration (SRDF, kinematics, joint limits, OMPL, controllers). All but the first are generated from the single-arm files by `scripts/make_config.py` (already run).
- `launch/dual.launch.py`: two fake Gen3 arms, `ros2_control`, MoveIt and RViz.
- `move_arm left|right X Y Z ROLL PITCH YAW` (Python in `py/`, C++ in `cpp/`): plan and move one hand to a pose in the frame `world`.

Build and run: see the lesson.
