// Service /check_action: says whether a symbolic action is well formed.
#include <map>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "a2_interfaces/srv/check_action.hpp"

using CheckAction = a2_interfaces::srv::CheckAction;

// action -> how many blocks it needs
const std::map<std::string, size_t> ARGUMENTS = {{"pickup", 1}, {"putdown", 1}, {"stack", 2}, {"unstack", 2}};

class Checker : public rclcpp::Node
{
public:
  Checker() : Node("checker")
  {
    service_ = create_service<CheckAction>(
      "check_action",
      [this](const std::shared_ptr<CheckAction::Request> request, std::shared_ptr<CheckAction::Response> response) {
        on_request(request, response);
      });
  }

private:
  void on_request(const std::shared_ptr<CheckAction::Request> request, std::shared_ptr<CheckAction::Response> response)
  {
    const std::string & name = request->action.name;
    const size_t count = request->action.args.size();
    auto rule = ARGUMENTS.find(name);
    if (rule == ARGUMENTS.end()) {
      response->valid = false;
      response->reason = "unknown action '" + name + "'";
    } else if (count != rule->second) {
      response->valid = false;
      response->reason = name + " needs " + std::to_string(rule->second) + " blocks, got " + std::to_string(count);
    } else {
      response->valid = true;
      response->reason = "ok";
    }
    RCLCPP_INFO(get_logger(), "checked %s (%zu blocks): %s", name.c_str(), count, response->reason.c_str());
  }

  rclcpp::Service<CheckAction>::SharedPtr service_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Checker>());
  rclcpp::shutdown();
  return 0;
}
