// Ask the pick_place server to move a block: pick_place_client BLOCK X Y Z   (z is the centre of the block)
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <d2_interfaces/action/pick_place.hpp>
#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>

using PickPlace = d2_interfaces::action::PickPlace;
using namespace std::chrono_literals;

int main(int argc, char **argv) {
  if (argc != 5) {
    std::fprintf(stderr, "usage: pick_place_client BLOCK X Y Z\n");
    return 2;
  }
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("pick_place_client");
  auto client = rclcpp_action::create_client<PickPlace>(node, "pick_place");
  if (!client->wait_for_action_server(10s)) {
    std::fprintf(stderr, "no /pick_place server: is pick_place_server.py running?\n");
    return 1;
  }
  PickPlace::Goal goal;
  goal.block = argv[1];
  goal.x = std::atof(argv[2]);
  goal.y = std::atof(argv[3]);
  goal.z = std::atof(argv[4]);

  rclcpp_action::Client<PickPlace>::SendGoalOptions options;
  options.feedback_callback = [](auto, const std::shared_ptr<const PickPlace::Feedback> feedback) {
    std::printf("   %s\n", feedback->stage.c_str());
  };
  auto handle_future = client->async_send_goal(goal, options);
  if (rclcpp::spin_until_future_complete(node, handle_future) != rclcpp::FutureReturnCode::SUCCESS) return 1;
  auto handle = handle_future.get();
  if (!handle) {
    std::fprintf(stderr, "the goal was rejected\n");
    return 1;
  }
  auto result_future = client->async_get_result(handle);
  if (rclcpp::spin_until_future_complete(node, result_future) != rclcpp::FutureReturnCode::SUCCESS) return 1;
  const auto result = result_future.get().result;
  std::printf("%s%s\n", result->success ? "success: " : "FAILED: ", result->message.c_str());
  rclcpp::shutdown();
  return result->success ? 0 : 1;
}
