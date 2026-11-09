// Put a box into the planning scene: add_box NAME X Y Z SX SY SZ   or   add_box NAME remove
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <string>
#include <thread>
#include <vector>

#include <geometry_msgs/msg/pose.hpp>
#include <moveit/planning_scene_interface/planning_scene_interface.hpp>
#include <moveit_msgs/msg/collision_object.hpp>
#include <rclcpp/rclcpp.hpp>
#include <shape_msgs/msg/solid_primitive.hpp>

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  const bool remove = argc == 3 && std::strcmp(argv[2], "remove") == 0;
  if (!(argc == 8 || remove)) {
    std::fprintf(stderr, "usage: add_box NAME X Y Z SX SY SZ   |   add_box NAME remove\n");
    return 2;
  }
  const std::string name = argv[1];

  auto node = std::make_shared<rclcpp::Node>("add_box");
  rclcpp::executors::SingleThreadedExecutor executor;
  executor.add_node(node);
  std::thread spinner([&executor]() { executor.spin(); });

  moveit::planning_interface::PlanningSceneInterface scene;
  bool ok = true;
  if (remove) {
    scene.removeCollisionObjects({name});
  } else {
    moveit_msgs::msg::CollisionObject obj;
    obj.header.frame_id = "base_link";
    obj.id = name;
    shape_msgs::msg::SolidPrimitive box;
    box.type = box.BOX;
    box.dimensions = {std::atof(argv[5]), std::atof(argv[6]), std::atof(argv[7])};
    geometry_msgs::msg::Pose pose;
    pose.position.x = std::atof(argv[2]);
    pose.position.y = std::atof(argv[3]);
    pose.position.z = std::atof(argv[4]);
    pose.orientation.w = 1.0;
    obj.primitives.push_back(box);
    obj.primitive_poses.push_back(pose);
    obj.operation = obj.ADD;
    ok = scene.applyCollisionObjects({obj});
  }
  std::printf(ok ? "scene updated\n" : "scene update failed\n");
  executor.cancel();
  spinner.join();
  rclcpp::shutdown();
  return ok ? 0 : 1;
}
