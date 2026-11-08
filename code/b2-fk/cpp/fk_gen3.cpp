// Forward kinematics of the Kinova Gen3 (7 joints): from seven joint angles to the pose of end_effector_link.
//   fk_gen3 Q1 Q2 Q3 Q4 Q5 Q6 Q7      joint angles in radians
// The pose is given in base_link, the same as: ros2 run tf2_ros tf2_echo base_link end_effector_link
#include <Eigen/Dense>
#include <cmath>
#include <cstdio>
#include <cstdlib>

using Eigen::Matrix4d;

namespace
{
const double H = M_PI / 2;

// Where each joint sits relative to the one before it: (x, y, z in metres, roll in radians).
// Copied from the <origin> lines of the URDF (lesson B1). Pitch and yaw are 0 in all of them.
struct JointOrigin { const char * name; double x, y, z, roll; };
const JointOrigin JOINTS[7] = {
  {"joint_1", 0.0, 0.0, 0.15643, M_PI},
  {"joint_2", 0.0, 0.005375, -0.12838, H},
  {"joint_3", 0.0, -0.21038, -0.006375, -H},
  {"joint_4", 0.0, 0.006375, -0.21038, H},
  {"joint_5", 0.0, -0.20843, -0.006375, -H},
  {"joint_6", 0.0, 0.00017505, -0.10593, H},
  {"joint_7", 0.0, -0.10593, -0.00017505, -H},
};
// The fixed joint end_effector: the hand frame, 6.15 cm after joint_7, turned upside down (roll pi).
const JointOrigin END_EFFECTOR = {"end_effector", 0.0, 0.0, -0.061525, M_PI};

Matrix4d translate(double x, double y, double z)
{
  Matrix4d t = Matrix4d::Identity();
  t(0, 3) = x; t(1, 3) = y; t(2, 3) = z;
  return t;
}

Matrix4d rot_x(double a)
{
  Matrix4d r = Matrix4d::Identity();
  r(1, 1) = std::cos(a); r(1, 2) = -std::sin(a);
  r(2, 1) = std::sin(a); r(2, 2) = std::cos(a);
  return r;
}

Matrix4d rot_z(double a)
{
  Matrix4d r = Matrix4d::Identity();
  r(0, 0) = std::cos(a); r(0, 1) = -std::sin(a);
  r(1, 0) = std::sin(a); r(1, 1) = std::cos(a);
  return r;
}
}  // namespace

int main(int argc, char ** argv)
{
  if (argc < 8) {
    std::fprintf(stderr, "usage: fk_gen3 Q1 Q2 Q3 Q4 Q5 Q6 Q7\n");
    return 1;
  }
  Matrix4d pose = Matrix4d::Identity();  // the pose of base_link in itself: no movement
  for (int i = 0; i < 7; ++i) {
    const JointOrigin & j = JOINTS[i];
    const double angle = std::atof(argv[i + 1]);
    // Go to the joint (offset, then its fixed turn), then turn by the joint angle about its z axis.
    pose = pose * translate(j.x, j.y, j.z) * rot_x(j.roll) * rot_z(angle);
    std::printf("%s frame at  x = %7.3f  y = %7.3f  z = %7.3f\n", j.name, pose(0, 3), pose(1, 3), pose(2, 3));
  }
  const JointOrigin & e = END_EFFECTOR;
  pose = pose * translate(e.x, e.y, e.z) * rot_x(e.roll);

  // Roll, pitch, yaw of the hand (rotation about x, then y, then z of the fixed frame), as tf2_echo prints them.
  const double rad = 180.0 / M_PI;
  const double roll = std::atan2(pose(2, 1), pose(2, 2)) * rad;
  const double pitch = -std::asin(pose(2, 0)) * rad;
  const double yaw = std::atan2(pose(1, 0), pose(0, 0)) * rad;
  std::printf("end_effector_link: translation [%.3f, %.3f, %.3f]\n", pose(0, 3), pose(1, 3), pose(2, 3));
  std::printf("end_effector_link: RPY (degree) [%.3f, %.3f, %.3f]\n", roll, pitch, yaw);
  std::printf("end_effector_link: matrix\n");
  for (int r = 0; r < 4; ++r) {
    std::printf("  %7.3f %7.3f %7.3f %7.3f\n", pose(r, 0), pose(r, 1), pose(r, 2), pose(r, 3));
  }
  return 0;
}
