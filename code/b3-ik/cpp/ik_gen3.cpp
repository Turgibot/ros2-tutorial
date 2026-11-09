// Inverse kinematics of the Kinova Gen3: find joint angles that put end_effector_link at a target pose.
//   ik_gen3 X Y Z ROLL PITCH YAW Q1 Q2 Q3 Q4 Q5 Q6 Q7
// The target is a position in metres and roll, pitch, yaw in degrees (in base_link, as tf2_echo prints them).
// Q1..Q7 (radians) is where the search starts. Different starts can end in different solutions.
#include <algorithm>
#include <cstdio>
#include <cstdlib>

#include "gen3.hpp"

int main(int argc, char ** argv)
{
  if (argc < 14) {
    std::fprintf(stderr, "usage: ik_gen3 X Y Z ROLL PITCH YAW Q1 Q2 Q3 Q4 Q5 Q6 Q7\n");
    return 1;
  }
  double a[13];
  for (int i = 0; i < 13; ++i) {
    a[i] = std::atof(argv[i + 1]);
  }
  const Eigen::Matrix4d target = gen3::pose_from(Eigen::Vector3d(a[0], a[1], a[2]), a[3], a[4], a[5]);
  Eigen::VectorXd q(7);
  for (int i = 0; i < 7; ++i) {
    q[i] = a[6 + i];
  }

  const double LAMBDA = 0.01;   // damping: keeps the steps small when the arm is nearly stretched out
  const double MAX_STEP = 0.3;  // largest change of one joint in one iteration (rad)

  int iteration = 1;
  for (; iteration <= 200; ++iteration) {
    const Eigen::VectorXd err = gen3::residual(q, target);
    if (err.head<3>().norm() < 1e-6 && err.tail<3>().norm() < 1e-6) {
      break;
    }
    const Eigen::MatrixXd jac = gen3::jacobian(q, target);
    // Damped least squares: the smallest joint change that cancels the error.
    const Eigen::MatrixXd m = jac * jac.transpose() + LAMBDA * LAMBDA * Eigen::MatrixXd::Identity(6, 6);
    Eigen::VectorXd dq = -jac.transpose() * m.ldlt().solve(err);
    for (int i = 0; i < 7; ++i) {
      q[i] += std::max(-MAX_STEP, std::min(MAX_STEP, dq[i]));
      q[i] = std::max(-gen3::LIMIT[i], std::min(gen3::LIMIT[i], q[i]));  // stay inside the joint limits
    }
  }
  iteration = std::min(iteration, 200);

  const Eigen::VectorXd err = gen3::residual(q, target);
  std::printf("iterations: %d\n", iteration);
  std::printf("joints (rad):");
  for (int i = 0; i < 7; ++i) std::printf(" %.4f", q[i]);
  std::printf("\njoints (deg):");
  for (int i = 0; i < 7; ++i) std::printf(" %.1f", q[i] * 180.0 / M_PI);
  std::printf("\nposition error: %.2e m   rotation error: %.2e rad\n", err.head<3>().norm(), err.tail<3>().norm());
  return 0;
}
