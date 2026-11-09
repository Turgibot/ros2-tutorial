// Turn the ground-truth block poses from Gazebo into TF frames: base_link -> block_A ... block_D.
// The arm stands at the origin of the Gazebo world, so the world frame and the arm's base_link are the same place.
#include <memory>
#include <string>
#include <vector>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <rclcpp/rclcpp.hpp>
#include <tf2_ros/transform_broadcaster.h>

class BlockTf : public rclcpp::Node {
public:
  BlockTf() : Node("block_tf"), broadcaster_(this) {
    for (char k : std::string("ABCD")) {
      subs_.push_back(create_subscription<geometry_msgs::msg::PoseStamped>(
          std::string("/model/block_") + k + "/pose", 10,
          [this, k](const geometry_msgs::msg::PoseStamped::SharedPtr msg) { on_pose(k, *msg); }));
    }
  }

private:
  void on_pose(char k, const geometry_msgs::msg::PoseStamped &msg) {
    geometry_msgs::msg::TransformStamped t;
    t.header.stamp = msg.header.stamp;               // simulated time, as in every other message
    t.header.frame_id = "base_link";
    t.child_frame_id = std::string("block_") + k;
    t.transform.translation.x = msg.pose.position.x;
    t.transform.translation.y = msg.pose.position.y;
    t.transform.translation.z = msg.pose.position.z;
    t.transform.rotation = msg.pose.orientation;
    broadcaster_.sendTransform(t);
  }

  tf2_ros::TransformBroadcaster broadcaster_;
  std::vector<rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr> subs_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<BlockTf>());
  rclcpp::shutdown();
  return 0;
}
