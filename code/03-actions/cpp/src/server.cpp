// Action server /execute: pretends to carry out a symbolic action in four phases (1 s each).
#include <memory>
#include <string>
#include <thread>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "a3_interfaces/action/execute.hpp"

using Execute = a3_interfaces::action::Execute;
using GoalHandle = rclcpp_action::ServerGoalHandle<Execute>;
using namespace std::chrono_literals;

const std::vector<std::string> PHASES = {"approach", "grasp", "lift", "place"};

class Robot : public rclcpp::Node
{
public:
  Robot() : Node("robot")
  {
    using namespace std::placeholders;
    server_ = rclcpp_action::create_server<Execute>(
      this, "execute",
      [](const rclcpp_action::GoalUUID &, std::shared_ptr<const Execute::Goal>) {
        return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;   // accept every goal
      },
      [](const std::shared_ptr<GoalHandle>) {
        return rclcpp_action::CancelResponse::ACCEPT;             // accept every cancel request
      },
      [this](const std::shared_ptr<GoalHandle> goal_handle) {
        // Run on a separate thread, so this callback returns at once and the node keeps
        // handling other requests (such as a cancel) while the action runs.
        std::thread([this, goal_handle]() { execute(goal_handle); }).detach();
      });
  }

private:
  void execute(const std::shared_ptr<GoalHandle> goal_handle)
  {
    std::string action = goal_handle->get_goal()->name;
    for (const auto & arg : goal_handle->get_goal()->args) {
      action += " " + arg;
    }
    RCLCPP_INFO(get_logger(), "executing: %s", action.c_str());

    auto feedback = std::make_shared<Execute::Feedback>();
    auto result = std::make_shared<Execute::Result>();
    for (size_t i = 0; i < PHASES.size(); ++i) {
      if (goal_handle->is_canceling()) {
        result->success = false;
        result->message = "canceled before " + PHASES[i];
        goal_handle->canceled(result);
        RCLCPP_INFO(get_logger(), "canceled before %s", PHASES[i].c_str());
        return;
      }
      std::this_thread::sleep_for(1s);   // the "work"
      feedback->phase = PHASES[i];
      feedback->progress = static_cast<float>(i + 1) / PHASES.size();
      goal_handle->publish_feedback(feedback);
    }
    result->success = true;
    result->message = action + ": done";
    goal_handle->succeed(result);
    RCLCPP_INFO(get_logger(), "done: %s", action.c_str());
  }

  rclcpp_action::Server<Execute>::SharedPtr server_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Robot>());
  rclcpp::shutdown();
  return 0;
}
