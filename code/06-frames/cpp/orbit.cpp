// Publishes a moving frame "marker" that circles around the frame "base" (radius 0.3 m, 0.5 rad/s, 0.2 m up).
#include <chrono>
#include <cmath>
#include <memory>

#include "geometry_msgs/msg/transform_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/transform_broadcaster.h"

using namespace std::chrono_literals;

class Orbit : public rclcpp::Node
{
public:
  Orbit() : Node("orbit")
  {
    broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);
    start_ = now();
    timer_ = create_wall_timer(50ms, [this]() { on_timer(); });  // 20 times per second
  }

private:
  void on_timer()
  {
    const auto stamp = now();
    const double angle = 0.5 * (stamp - start_).seconds();  // 0.5 rad/s

    geometry_msgs::msg::TransformStamped t;
    t.header.stamp = stamp;
    t.header.frame_id = "base";     // parent frame
    t.child_frame_id = "marker";    // child frame: its pose is given in the parent
    t.transform.translation.x = 0.3 * std::cos(angle);
    t.transform.translation.y = 0.3 * std::sin(angle);
    t.transform.translation.z = 0.2;
    // rotation about z by `angle`, as a quaternion (x, y, z, w) = (0, 0, sin(angle/2), cos(angle/2))
    t.transform.rotation.z = std::sin(angle / 2);
    t.transform.rotation.w = std::cos(angle / 2);
    broadcaster_->sendTransform(t);
  }

  std::unique_ptr<tf2_ros::TransformBroadcaster> broadcaster_;
  rclcpp::Time start_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Orbit>());
  rclcpp::shutdown();
  return 0;
}
