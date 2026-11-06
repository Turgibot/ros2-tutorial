// Sends one goal to /execute and prints feedback and result, for example: ros2 run a3_actions client unstack F W
#include <cstdio>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "a3_interfaces/action/execute.hpp"

using Execute = a3_interfaces::action::Execute;
using GoalHandle = rclcpp_action::ClientGoalHandle<Execute>;

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("robot_client");
  auto client = rclcpp_action::create_client<Execute>(node, "execute");
  if (!client->wait_for_action_server(std::chrono::seconds(10))) {
    RCLCPP_ERROR(node->get_logger(), "no action server /execute");
    return 1;
  }

  Execute::Goal goal;
  goal.name = argv[1];
  for (int i = 2; i < argc; ++i) {
    goal.args.push_back(argv[i]);
  }

  // The callbacks: the feedback callback runs for every feedback message,
  // the result callback once, when the goal ends.
  rclcpp_action::Client<Execute>::SendGoalOptions options;
  options.feedback_callback =
    [](GoalHandle::SharedPtr, const std::shared_ptr<const Execute::Feedback> feedback) {
      std::printf("feedback: %s (%.2f)\n", feedback->phase.c_str(), feedback->progress);
    };
  options.result_callback = [](const GoalHandle::WrappedResult & wrapped) {
    std::printf("result: success=%s message=%s\n", wrapped.result->success ? "True" : "False",
      wrapped.result->message.c_str());
  };

  // 1. send the goal
  auto goal_future = client->async_send_goal(goal, options);
  rclcpp::spin_until_future_complete(node, goal_future);
  auto goal_handle = goal_future.get();
  if (!goal_handle) {
    std::printf("goal rejected\n");
    return 1;
  }

  // 2. wait for the result (its callback prints it)
  auto result_future = client->async_get_result(goal_handle);
  rclcpp::spin_until_future_complete(node, result_future);
  rclcpp::shutdown();
  return 0;
}
