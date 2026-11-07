// Once a second, asks TF where the frame `target` is, as seen from the frame `source`, and prints it.
#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "tf2/exceptions.h"
#include "tf2/time.h"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_listener.h"

using namespace std::chrono_literals;

class Where : public rclcpp::Node
{
public:
  Where() : Node("where")
  {
    declare_parameter("source", "base");
    declare_parameter("target", "marker");
    buffer_ = std::make_unique<tf2_ros::Buffer>(get_clock());
    listener_ = std::make_unique<tf2_ros::TransformListener>(*buffer_);  // fills the buffer from /tf and /tf_static
    timer_ = create_wall_timer(1s, [this]() { on_timer(); });
  }

private:
  void on_timer()
  {
    const std::string source = get_parameter("source").as_string();
    const std::string target = get_parameter("target").as_string();
    try {
      // tf2::TimePointZero means "the latest transform available"
      const auto t = buffer_->lookupTransform(source, target, tf2::TimePointZero);
      const auto & p = t.transform.translation;
      RCLCPP_INFO(
        get_logger(), "%s in %s: x=%.3f y=%.3f z=%.3f", target.c_str(), source.c_str(),
        p.x, p.y, p.z);
    } catch (const tf2::TransformException & e) {
      RCLCPP_WARN(
        get_logger(), "cannot get %s in %s: %s", target.c_str(), source.c_str(), e.what());
    }
  }

  std::unique_ptr<tf2_ros::Buffer> buffer_;
  std::unique_ptr<tf2_ros::TransformListener> listener_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Where>());
  rclcpp::shutdown();
  return 0;
}
