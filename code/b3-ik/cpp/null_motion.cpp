// Move the Gen3's joints while the hand stays where it is (the null space).
//   null_motion Q1 Q2 Q3 Q4 Q5 Q6 Q7 [STEPS]
// Starts from the joint angles Q1..Q7 (radians), holds the hand pose they give, and pushes joint 3 for STEPS steps
// (default 100). The push is projected onto the null space: only the part that does not move the hand is kept.
#include <cstdio>
#include <cstdlib>

#include "gen3.hpp"

static void show(int step, const Eigen::VectorXd & q)
{
  const Eigen::Vector3d p = gen3::fk(q).topRightCorner<3, 1>();
  std::printf("step %3d  q =", step);
  for (int i = 0; i < 7; ++i) std::printf(" %7.3f", q[i]);
  std::printf("   hand = [%.3f, %.3f, %.3f]\n", p[0], p[1], p[2]);
}

int main(int argc, char ** argv)
{
  if (argc < 8) {
    std::fprintf(stderr, "usage: null_motion Q1 Q2 Q3 Q4 Q5 Q6 Q7 [STEPS]\n");
    return 1;
  }
  Eigen::VectorXd q(7);
  for (int i = 0; i < 7; ++i) {
    q[i] = std::atof(argv[i + 1]);
  }
  const int steps = argc >= 9 ? std::atoi(argv[8]) : 100;
  const Eigen::Matrix4d target = gen3::fk(q);  // the hand pose to hold
  Eigen::VectorXd push = Eigen::VectorXd::Zero(7);
  push[2] = 0.01;                              // "please turn joint 3": 0.01 rad per step

  show(0, q);
  for (int step = 1; step <= steps; ++step) {
    const Eigen::MatrixXd jac = gen3::jacobian(q, target);
    const Eigen::MatrixXd jac_pinv = jac.completeOrthogonalDecomposition().pseudoInverse();  // 7 x 6
    const Eigen::MatrixXd null = Eigen::MatrixXd::Identity(7, 7) - jac_pinv * jac;           // 7 x 7
    q = q - jac_pinv * gen3::residual(q, target) + null * push;  // fix any drift, then move in the null space
    if (step % (steps / 4) == 0) {
      show(step, q);
    }
  }
  const Eigen::VectorXd err = gen3::residual(q, target);
  std::printf("hand pose error after %d steps: position %.1e m, rotation %.1e rad\n", steps, err.head<3>().norm(), err.tail<3>().norm());
  return 0;
}
