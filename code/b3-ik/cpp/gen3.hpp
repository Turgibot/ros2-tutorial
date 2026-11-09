// Kinematics of the Kinova Gen3, shared by ik_gen3.cpp and null_motion.cpp.
//   fk(q): the 4x4 pose of end_effector_link in base_link (the same chain as fk_gen3 in lesson B2).
//   residual(q, target): how far the hand is from a target pose, as 6 numbers.
//   jacobian(q, target): how that residual changes when each of the 7 joints moves (6 x 7 matrix).
#pragma once
#include <Eigen/Dense>
#include <cmath>

namespace gen3
{
using Eigen::Matrix3d;
using Eigen::Matrix4d;
using Eigen::Vector3d;
using Eigen::VectorXd;
using Eigen::MatrixXd;

const double H = M_PI / 2;
// (x, y, z in metres, roll in radians) of each joint's origin, from the URDF (lesson B1), then of end_effector.
struct Origin { double x, y, z, roll; };
const Origin ORIGINS[7] = {
  {0.0, 0.0, 0.15643, M_PI},
  {0.0, 0.005375, -0.12838, H},
  {0.0, -0.21038, -0.006375, -H},
  {0.0, 0.006375, -0.21038, H},
  {0.0, -0.20843, -0.006375, -H},
  {0.0, 0.00017505, -0.10593, H},
  {0.0, -0.10593, -0.00017505, -H},
};
const Origin END_EFFECTOR = {0.0, 0.0, -0.061525, M_PI};
// Joint limits of the URDF (lesson B1): joints 2, 4, 6 are limited, the others turn freely.
const double LIMIT[7] = {INFINITY, 2.24, INFINITY, 2.57, INFINITY, 2.09, INFINITY};

inline Matrix4d pose(const Origin & o, double angle = 0.0)
{
  const double cr = std::cos(o.roll), sr = std::sin(o.roll), ca = std::cos(angle), sa = std::sin(angle);
  Matrix3d rx, rz;
  rx << 1, 0, 0, 0, cr, -sr, 0, sr, cr;
  rz << ca, -sa, 0, sa, ca, 0, 0, 0, 1;
  Matrix4d t = Matrix4d::Identity();
  t.topLeftCorner<3, 3>() = rx * rz;
  t.topRightCorner<3, 1>() = Vector3d(o.x, o.y, o.z);
  return t;
}

inline Matrix4d fk(const VectorXd & q)
{
  Matrix4d t = Matrix4d::Identity();
  for (int i = 0; i < 7; ++i) {
    t = t * pose(ORIGINS[i], q[i]);
  }
  return t * pose(END_EFFECTOR);
}

// The rotation r as one vector: its axis, scaled by its angle (radians).
inline Vector3d rotvec(const Matrix3d & r)
{
  const double angle = std::acos(std::max(-1.0, std::min(1.0, (r.trace() - 1) / 2)));
  const Vector3d w(r(2, 1) - r(1, 2), r(0, 2) - r(2, 0), r(1, 0) - r(0, 1));
  if (angle < 1e-9) {
    return w / 2;
  }
  return w / 2 / std::sin(angle) * angle;
}

// Target minus current: 3 position numbers (m), then 3 numbers for the rotation that is still missing (rad).
inline VectorXd residual(const VectorXd & q, const Matrix4d & target)
{
  const Matrix4d t = fk(q);
  VectorXd e(6);
  e.head<3>() = target.topRightCorner<3, 1>() - t.topRightCorner<3, 1>();
  e.tail<3>() = rotvec(target.topLeftCorner<3, 3>() * t.topLeftCorner<3, 3>().transpose());
  return e;
}

// 6 x 7: column j is how the residual changes when joint j moves by a small step (finite difference).
inline MatrixXd jacobian(const VectorXd & q, const Matrix4d & target, double eps = 1e-6)
{
  const VectorXd r0 = residual(q, target);
  MatrixXd jac(6, 7);
  for (int j = 0; j < 7; ++j) {
    VectorXd q2 = q;
    q2[j] += eps;
    jac.col(j) = (residual(q2, target) - r0) / eps;
  }
  return jac;
}

// A 4x4 pose from a position and roll, pitch, yaw in degrees (the way tf2_echo prints them).
inline Matrix4d pose_from(const Vector3d & xyz, double roll_deg, double pitch_deg, double yaw_deg)
{
  const double d = M_PI / 180.0;
  Matrix3d r = (Eigen::AngleAxisd(yaw_deg * d, Vector3d::UnitZ()) * Eigen::AngleAxisd(pitch_deg * d, Vector3d::UnitY()) *
    Eigen::AngleAxisd(roll_deg * d, Vector3d::UnitX())).toRotationMatrix();
  Matrix4d t = Matrix4d::Identity();
  t.topLeftCorner<3, 3>() = r;
  t.topRightCorner<3, 1>() = xyz;
  return t;
}
}  // namespace gen3
