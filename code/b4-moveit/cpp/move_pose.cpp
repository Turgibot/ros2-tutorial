// Ask MoveIt to move the hand to a pose: move_pose X Y Z ROLL PITCH YAW  (metres, degrees)
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <thread>

#include <geometry_msgs/msg/pose.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <rclcpp/rclcpp.hpp>
#include <tf2/LinearMath/Quaternion.h>

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  if (argc != 7) {
    std::fprintf(stderr, "usage: move_pose X Y Z ROLL PITCH YAW   (metres, degrees)\n");
    return 2;
  }
  const double x = std::atof(argv[1]), y = std::atof(argv[2]), z = std::atof(argv[3]);
  const double deg = M_PI / 180.0;
  tf2::Quaternion q;
  q.setRPY(std::atof(argv[4]) * deg, std::atof(argv[5]) * deg, std::atof(argv[6]) * deg);

  auto node = std::make_shared<rclcpp::Node>("move_pose");
  // MoveGroupInterface needs the node to be spinning, so spin it in a thread
  rclcpp::executors::SingleThreadedExecutor executor;
  executor.add_node(node);
  std::thread spinner([&executor]() { executor.spin(); });

  moveit::planning_interface::MoveGroupInterface group(node, "manipulator");
  group.setEndEffectorLink("end_effector_link");
  group.setPoseReferenceFrame("base_link");
  group.setNumPlanningAttempts(5);
  group.setPlanningTime(5.0);
  group.setMaxVelocityScalingFactor(0.3);
  group.setMaxAccelerationScalingFactor(0.3);

  geometry_msgs::msg::Pose target;
  target.position.x = x;
  target.position.y = y;
  target.position.z = z;
  target.orientation.x = q.x();
  target.orientation.y = q.y();
  target.orientation.z = q.z();
  target.orientation.w = q.w();
  group.setPoseTarget(target);

  moveit::planning_interface::MoveGroupInterface::Plan plan;
  const auto planned = group.plan(plan);
  int status = 1;
  if (planned == moveit::core::MoveItErrorCode::SUCCESS) {
    const auto& pts = plan.trajectory.joint_trajectory.points;
    const auto& last = pts.back().time_from_start;
    const auto executed = group.execute(plan);
    std::printf("result: %s\n", executed == moveit::core::MoveItErrorCode::SUCCESS ? "SUCCESS" : "EXECUTION FAILED");
    std::printf("trajectory: %zu points, %.2f s\n", pts.size(), last.sec + last.nanosec * 1e-9);
    status = executed == moveit::core::MoveItErrorCode::SUCCESS ? 0 : 1;
  } else {
    std::printf("result: PLANNING FAILED (error code %d)\n", planned.val);
  }
  executor.cancel();
  spinner.join();
  rclcpp::shutdown();
  return status;
}
