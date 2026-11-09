exec > /workspace/.t_sim.out 2>&1
cd /workspace/code/c2-sim && source install/setup.bash
exec ros2 launch c2_sim sim.launch.py gui:=false
