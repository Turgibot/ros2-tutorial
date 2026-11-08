# B2: forward kinematics

Code for lesson B2 (`lessons/b2-forward-kinematics.html`). One colcon package, `b2_fk`, with the same two programs in Python (`py/`) and C++ (`cpp/`). Neither uses ROS code: they only calculate.

- `fk2`: forward kinematics of a flat arm with two links (angles in degrees).
- `fk_gen3`: forward kinematics of the Kinova Gen3 (seven angles in radians), to compare with `tf2_echo`.

Build and run: see the lesson.
