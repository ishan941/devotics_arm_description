# source /opt/ros/jazzy/setup.bash && source /home/ishan/ros2_ws/install/setup.bash
# ros2 launch devotics_arm_description arm_v0_control.launch.py rviz:=true


source /opt/ros/jazzy/setup.bash && source /home/ishan/ros2_ws/install/setup.bash


echo "Pick and place sequence started"
# ask if interactice, once or loop 
read mode
if [ "$mode" == "interactive" ]; then
    ros2 run devotics_arm_description arm_v0_stack_palletizer.py --mode interactive
elif [ "$mode" == "once" ]; then
    ros2 run devotics_arm_description arm_v0_stack_palletizer.py --mode once
elif [ "$mode" == "loop" ]; then
    read num_loops
    ros2 run devotics_arm_description arm_v0_stack_palletizer.py --mode loop --num-loops $num_loops
fi