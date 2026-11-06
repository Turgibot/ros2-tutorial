// Publishes a symbolic action (name and arguments) as text on /action. Its settings are parameters.
#include <chrono>
#include <memory>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using OnSetParametersCallbackHandle = rclcpp::node_interfaces::OnSetParametersCallbackHandle;

class Announcer : public rclcpp::Node
{
public:
  Announcer() : Node("announcer")
  {
    // Declare each parameter with a default value (this also fixes its type).
    declare_parameter("name", "pickup");
    declare_parameter("args", std::vector<std::string>{"A"});
    declare_parameter("rate_hz", 1.0);

    pub_ = create_publisher<std_msgs::msg::String>("action", 10);
    start_timer(get_parameter("rate_hz").as_double());
    // Called before a new value is accepted.
    // Keep the handle in a member, or the callback is removed.
    callback_handle_ = add_on_set_parameters_callback(
      [this](const std::vector<rclcpp::Parameter> & params) {
        rcl_interfaces::msg::SetParametersResult result;
        result.successful = true;
        for (const auto & p : params) {
          if (p.get_name() == "rate_hz") {
            if (p.as_double() <= 0.0) {
              result.successful = false;
              result.reason = "rate_hz must be positive";
            } else {
              start_timer(p.as_double());   // restart with the new period
            }
          }
        }
        return result;
      });
  }

private:
  void start_timer(double rate_hz)
  {
    timer_ = create_wall_timer(
      std::chrono::duration<double>(1.0 / rate_hz), [this]() { tick(); });
  }

  void tick()
  {
    std_msgs::msg::String msg;
    msg.data = get_parameter("name").as_string();
    // Copy the list into a variable first:
    // get_parameter returns a temporary object.
    std::vector<std::string> args = get_parameter("args").as_string_array();
    for (const auto & arg : args) {
      msg.data += " " + arg;
    }
    pub_->publish(msg);
    RCLCPP_INFO(get_logger(), "sent: %s", msg.data.c_str());
  }

  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;
  rclcpp::TimerBase::SharedPtr timer_;
  OnSetParametersCallbackHandle::SharedPtr callback_handle_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Announcer>());
  rclcpp::shutdown();
  return 0;
}
