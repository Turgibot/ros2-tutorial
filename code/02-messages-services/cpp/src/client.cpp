// Asks /check_action about one action, for example: ros2 run a2_services client unstack F W
#include <chrono>
#include <iostream>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "a2_interfaces/srv/check_action.hpp"

using CheckAction = a2_interfaces::srv::CheckAction;
using namespace std::chrono_literals;

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("checker_client");
  auto client = node->create_client<CheckAction>("check_action");
  while (!client->wait_for_service(1s)) {
    if (!rclcpp::ok()) {   // Ctrl+C while waiting: stop instead of looping forever
      return 1;
    }
    RCLCPP_INFO(node->get_logger(), "waiting for the service...");
  }

  auto request = std::make_shared<CheckAction::Request>();
  request->action.name = argv[1];
  for (int i = 2; i < argc; ++i) {
    request->action.args.push_back(argv[i]);
  }

  auto future = client->async_send_request(request);
  rclcpp::spin_until_future_complete(node, future);
  auto response = future.get();
  std::cout << "valid=" << (response->valid ? "True" : "False") << " reason=" << response->reason << std::endl;
  rclcpp::shutdown();
  return 0;
}
