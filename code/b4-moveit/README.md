# B4: MoveIt 2

Code for lesson B4 (`lessons/b4-moveit.html`). One colcon package, `b4_moveit`, with the same two programs in Python (`py/`) and C++ (`cpp/`). Both need MoveIt running (`kinova_gen3_7dof_robotiq_2f_85_moveit_config robot.launch.py`).

- `move_pose X Y Z ROLL PITCH YAW`: plan and move the hand to a pose (metres, degrees, frame `base_link`). Python sends a goal to the `/move_action` action; C++ uses `MoveGroupInterface`.
- `add_box NAME X Y Z SX SY SZ` / `add_box NAME remove`: put a box in the planning scene, or take it out.

Build and run: see the lesson.
