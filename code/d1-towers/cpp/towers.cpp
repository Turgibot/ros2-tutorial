// The world estimator: turn the block poses into towers.
// Reads /model/block_X/pose (ground truth from Gazebo) and publishes /towers (std_msgs/String), for example
// "A | B | DC": three towers, A alone, B alone, and C standing on D. A block in the air (held by the gripper)
// is reported on its own as "held: X".
#include <algorithm>
#include <array>
#include <cmath>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

const std::string BLOCKS = "ABCD";
const double SIZE = 0.05;      // a block is a 5 cm cube
const double TABLE_Z = 0.30;   // height of the table top
const double TOL_XY = 0.03;    // "directly above": centres closer than 3 cm in x and in y
const double TOL_Z = 0.01;     // heights are compared to within 1 cm

using Pos = std::array<double, 3>;

// The block that k stands on, or 0 (k is on the table, or in the air).
char below(const std::map<char, Pos> &pos, char k) {
  for (char j : BLOCKS) {
    if (j == k) continue;
    double dx = pos.at(k)[0] - pos.at(j)[0], dy = pos.at(k)[1] - pos.at(j)[1], dz = pos.at(k)[2] - pos.at(j)[2];
    if (std::fabs(dx) < TOL_XY && std::fabs(dy) < TOL_XY && std::fabs(dz - SIZE) < TOL_Z) return j;
  }
  return 0;
}

bool on_table(const std::map<char, Pos> &pos, char k) {
  return std::fabs(pos.at(k)[2] - (TABLE_Z + SIZE / 2)) < TOL_Z;
}

std::string describe(const std::map<char, Pos> &pos) {
  std::map<char, char> above;                      // who is on top of whom
  for (char k : BLOCKS) if (below(pos, k)) above[below(pos, k)] = k;
  std::vector<std::string> towers;
  std::string held;
  for (char k : BLOCKS) {
    if (below(pos, k)) continue;
    if (on_table(pos, k)) {                        // the bottom of a tower
      std::string chain(1, k);
      while (above.count(chain.back())) chain += above[chain.back()];
      towers.push_back(chain);
    } else {
      held += std::string(" ") + k;
    }
  }
  std::sort(towers.begin(), towers.end());
  std::string text;
  for (size_t i = 0; i < towers.size(); ++i) text += (i ? " | " : "") + towers[i];
  if (!held.empty()) text += "   held:" + held;
  return text;
}

class Towers : public rclcpp::Node {
public:
  Towers() : Node("towers") {
    // "transient local": a program that starts later still receives the last message at once
    pub_ = create_publisher<std_msgs::msg::String>("/towers", rclcpp::QoS(1).transient_local());
    for (char k : BLOCKS) {
      subs_.push_back(create_subscription<geometry_msgs::msg::PoseStamped>(
          std::string("/model/block_") + k + "/pose", 10,
          [this, k](const geometry_msgs::msg::PoseStamped::SharedPtr msg) { on_pose(k, *msg); }));
    }
  }

private:
  void on_pose(char k, const geometry_msgs::msg::PoseStamped &msg) {
    const auto &p = msg.pose.position;
    pos_[k] = {p.x, p.y, p.z};
    if (pos_.size() < BLOCKS.size()) return;
    std::string text = describe(pos_);
    if (text != last_) {                           // publish only when something changed
      last_ = text;
      std_msgs::msg::String out;
      out.data = text;
      pub_->publish(out);
      RCLCPP_INFO(get_logger(), "%s", text.c_str());
    }
  }

  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;
  std::vector<rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr> subs_;
  std::map<char, Pos> pos_;
  std::string last_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Towers>());
  rclcpp::shutdown();
  return 0;
}
