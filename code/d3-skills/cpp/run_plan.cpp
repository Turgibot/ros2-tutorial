// Run a plan, a list of symbolic actions separated by ';', one after the other, and stop at the first failure.
//   run_plan "stack C D; stack B C"
#include <chrono>
#include <cstdio>
#include <memory>
#include <sstream>
#include <string>
#include <vector>
#include <a3_interfaces/action/execute.hpp>
#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <std_msgs/msg/string.hpp>

using Execute = a3_interfaces::action::Execute;
using namespace std::chrono_literals;

static std::vector<std::string> split(const std::string &text, char sep) {
  std::vector<std::string> out;
  std::stringstream stream(text);
  std::string item;
  while (std::getline(stream, item, sep)) out.push_back(item);
  return out;
}

int main(int argc, char **argv) {
  if (argc != 2) {
    std::fprintf(stderr, "usage: run_plan \"unstack B C; stack B D\"\n");
    return 2;
  }
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("run_plan");
  std::string towers = "?";
  auto sub = node->create_subscription<std_msgs::msg::String>(
      "/towers", rclcpp::QoS(1).transient_local(),
      [&towers](const std_msgs::msg::String::SharedPtr msg) { towers = msg->data; });
  auto client = rclcpp_action::create_client<Execute>(node, "execute");
  if (!client->wait_for_action_server(10s)) {
    std::fprintf(stderr, "no /execute server: is execute_server.py running?\n");
    return 1;
  }
  bool ok = true;
  for (const auto &text : split(argv[1], ';')) {
    std::vector<std::string> words;
    std::stringstream stream(text);
    std::string word;
    while (stream >> word) words.push_back(word);
    if (words.empty()) continue;
    Execute::Goal goal;
    goal.name = words[0];
    goal.args.assign(words.begin() + 1, words.end());
    std::printf("> %s\n", [&] { std::string t = goal.name; for (const auto &a : goal.args) t += " " + a; return t; }().c_str());
    auto handle_future = client->async_send_goal(goal);
    if (rclcpp::spin_until_future_complete(node, handle_future) != rclcpp::FutureReturnCode::SUCCESS) return 1;
    auto result_future = client->async_get_result(handle_future.get());
    if (rclcpp::spin_until_future_complete(node, result_future) != rclcpp::FutureReturnCode::SUCCESS) return 1;
    const auto result = result_future.get().result;
    std::printf("  %s%s\n", result->success ? "done" : "FAILED: ", result->success ? "" : result->message.c_str());
    if (!result->success) { ok = false; break; }
  }
  rclcpp::spin_some(node);
  std::printf("towers: %s\n", towers.c_str());
  rclcpp::shutdown();
  return ok ? 0 : 1;
}
