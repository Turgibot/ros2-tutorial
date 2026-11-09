exec > /workspace/.t_c3.out 2>&1
cd /workspace/code && source c2-sim/install/setup.bash
cd c3-world && source install/setup.bash
ros2 launch c3_world lab.launch.py > /tmp/l.log 2>&1 &
L=$!
sleep 10
F=$(ros2 pkg prefix c3_world)/share/c3_world/models/block_A/model.sdf
ros2 run ros_gz_sim create -file $F -name extra -x 0.6 -y -0.18 -z 0.42 2>&1 | tail -1
sleep 3
ros2 run ros_gz_sim create -file $F -name extra2 -x 0.6 -y -0.18 -z 0.47 2>&1 | tail -1
sleep 3; gz model -m extra -p | tail -2; gz model -m extra2 -p | tail -2
sleep 6; gz model -m extra2 -p | tail -2
timeout 3 ros2 topic echo /model/block_A/pose --once | grep -A4 "position"
kill $L; sleep 1; pkill -f "gz sim"; echo done
