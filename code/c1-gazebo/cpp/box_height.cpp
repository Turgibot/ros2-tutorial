// Watch the pose of the model "box" that Gazebo publishes (bridged to ROS as geometry_msgs/PoseStamped)
// and print its height every 0.1 s of simulated time, and the moment it lands.
#include <cstdio>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>

const double GROUND_Z = 0.1;   // the box is 0.2 m tall, so its centre is 0.1 m above the ground when it rests

class BoxHeight : public rclcpp::Node {
public:
  BoxHeight() : Node("box_height") {
    sub_ = create_subscription<geometry_msgs::msg::PoseStamped>(
        "/model/box/pose", 10,
        [this](const geometry_msgs::msg::PoseStamped::SharedPtr msg) { on_pose(*msg); });
  }

private:
  void on_pose(const geometry_msgs::msg::PoseStamped &msg) {
    double t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9;
    double z = msg.pose.position.z;
    if (t - last_print_ >= 0.1) {
      last_print_ = t;
      RCLCPP_INFO(get_logger(), "t = %5.2f s   z = %.3f m", t, z);
    }
    if (!landed_ && z <= GROUND_Z + 0.001) {
      landed_ = true;
      RCLCPP_INFO(get_logger(), "landed after %.3f s of simulated time", t);
    }
  }

  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr sub_;
  double last_print_ = -1.0;
  bool landed_ = false;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<BoxHeight>());
  rclcpp::shutdown();
  return 0;
}
