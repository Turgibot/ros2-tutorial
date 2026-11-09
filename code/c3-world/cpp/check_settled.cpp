// Print the position of the four blocks once per second of simulated time, from the poses Gazebo publishes.
#include <cstdio>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <rclcpp/rclcpp.hpp>

class CheckSettled : public rclcpp::Node {
public:
  CheckSettled() : Node("check_settled") {
    for (char k : std::string("ABCD")) {
      subs_.push_back(create_subscription<geometry_msgs::msg::PoseStamped>(
          std::string("/model/block_") + k + "/pose", 10,
          [this, k](const geometry_msgs::msg::PoseStamped::SharedPtr msg) { on_pose(k, *msg); }));
    }
  }

private:
  void on_pose(char k, const geometry_msgs::msg::PoseStamped &msg) {
    pose_[k] = msg.pose.position;
    double t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9;
    if (pose_.size() == 4 && (last_print_ < 0 || t - last_print_ >= 1.0)) {
      last_print_ = t;
      std::string line;
      char buf[96];
      for (const auto &[b, p] : pose_) {
        std::snprintf(buf, sizeof buf, "   %c: %.4f %.4f %.4f", b, p.x, p.y, p.z);
        line += buf;
      }
      RCLCPP_INFO(get_logger(), "t = %5.1f s%s", t, line.c_str());
    }
  }

  std::vector<rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr> subs_;
  std::map<char, geometry_msgs::msg::Point> pose_;
  double last_print_ = -1.0;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CheckSettled>());
  rclcpp::shutdown();
  return 0;
}
