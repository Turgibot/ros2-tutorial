// Forward kinematics of a flat arm with two links.
//   fk2 THETA1 THETA2 [L1 L2]      angles in degrees, lengths in metres (default 0.4 and 0.3)
// Prints where the elbow and the hand are, and which way the hand points.
#include <cmath>
#include <cstdio>
#include <cstdlib>

int main(int argc, char ** argv)
{
  if (argc < 3) {
    std::fprintf(stderr, "usage: fk2 THETA1 THETA2 [L1 L2]\n");
    return 1;
  }
  const double deg = M_PI / 180.0;
  const double theta1 = std::atof(argv[1]) * deg;
  const double theta2 = std::atof(argv[2]) * deg;
  const double l1 = argc >= 5 ? std::atof(argv[3]) : 0.4;
  const double l2 = argc >= 5 ? std::atof(argv[4]) : 0.3;

  // The elbow is l1 away from the base, in the direction theta1.
  const double elbow_x = l1 * std::cos(theta1);
  const double elbow_y = l1 * std::sin(theta1);

  // The second link points in the direction theta1 + theta2 (the angles add up).
  const double hand_x = elbow_x + l2 * std::cos(theta1 + theta2);
  const double hand_y = elbow_y + l2 * std::sin(theta1 + theta2);

  std::printf("elbow: x = %.4f  y = %.4f\n", elbow_x, elbow_y);
  std::printf("hand:  x = %.4f  y = %.4f  pointing %.1f degrees\n", hand_x, hand_y, (theta1 + theta2) / deg);
  return 0;
}
