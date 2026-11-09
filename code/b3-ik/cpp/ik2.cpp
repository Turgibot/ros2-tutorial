// Inverse kinematics of a flat arm with two links, by geometry.
//   ik2 X Y [L1 L2]      hand position in metres, lengths in metres (default 0.4 and 0.3)
// Prints the two joint settings (elbow one way and the other) that put the hand at (X, Y), in degrees.
#include <cmath>
#include <cstdio>
#include <cstdlib>

int main(int argc, char ** argv)
{
  if (argc < 3) {
    std::fprintf(stderr, "usage: ik2 X Y [L1 L2]\n");
    return 1;
  }
  const double x = std::atof(argv[1]);
  const double y = std::atof(argv[2]);
  const double l1 = argc >= 5 ? std::atof(argv[3]) : 0.4;
  const double l2 = argc >= 5 ? std::atof(argv[4]) : 0.3;
  const double deg = 180.0 / M_PI;

  // Law of cosines in the triangle base - elbow - hand: it gives the angle at the elbow.
  const double cos_theta2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2);
  if (std::fabs(cos_theta2) > 1) {
    std::printf("unreachable: the hand can be between %.3f and %.3f m from the base, this point is %.3f m away\n",
                std::fabs(l1 - l2), l1 + l2, std::hypot(x, y));
    return 1;
  }
  const char * names[2] = {"elbow down", "elbow up  "};
  for (int i = 0; i < 2; ++i) {
    const double theta2 = (i == 0 ? 1 : -1) * std::acos(cos_theta2);
    // theta1: the direction of the hand, minus the angle that link 2 adds.
    const double theta1 = std::atan2(y, x) - std::atan2(l2 * std::sin(theta2), l1 + l2 * std::cos(theta2));
    std::printf("%s: theta1 = %8.3f  theta2 = %8.3f\n", names[i], theta1 * deg, theta2 * deg);
  }
  return 0;
}
