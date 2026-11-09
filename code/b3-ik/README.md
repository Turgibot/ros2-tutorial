# B3: inverse kinematics and the null space

Code for lesson B3 (`lessons/b3-inverse-kinematics.html`). One colcon package, `b3_ik`, with the same three programs in Python (`py/`) and C++ (`cpp/`). None uses ROS code: they only calculate.

- `ik2`: inverse kinematics of a flat two-link arm, by geometry (both solutions).
- `ik_gen3`: numerical inverse kinematics of the Kinova Gen3 (damped least squares) from a target pose and a starting guess.
- `null_motion`: moves the joints of the Gen3 while the hand stays still (null-space motion).
- `py/gen3.py`, `cpp/gen3.hpp`: the forward kinematics of lesson B2 plus the Jacobian, shared by the two Gen3 programs.

Build and run: see the lesson.
