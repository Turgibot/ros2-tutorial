exec > /workspace/.t_q.out 2>&1
G="ros2 action send_goal /joint_trajectory_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory"
J='joint_names: [joint_1, joint_2, joint_3, joint_4, joint_5, joint_6, joint_7]'
j1() { timeout 5 ros2 topic echo /joint_states --once --field position 2>&1 | grep -v lost | tr -d '\n' | cut -c1-80; echo; }
W='gz service -s /world/empty/control --reqtype gz.msgs.WorldControl --reptype gz.msgs.Boolean --timeout 2000 --req'
sleep 25
$W 'pause: true'
$G "{trajectory: {$J, points: [{positions: [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], time_from_start: {sec: 2}}]}}" > /tmp/g.txt &
sleep 2; j1
$W 'pause: true multi_step: 1000'; sleep 1; j1
$W 'pause: true multi_step: 1000'; sleep 1; j1
$W 'pause: true multi_step: 500'; sleep 1; j1
$W 'pause: false'; wait; cat /tmp/g.txt | grep -E "status"
echo done
