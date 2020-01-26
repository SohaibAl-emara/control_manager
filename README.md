# ROS Node controlles the mode of driving
You can run this node to send ackermann msgs.
It also allows you to switch between the driving modes:
1- Manual control using keyboard
2- Semi Autonmous node where you can control steering/speed only
3- Fully autonmous

Steps to Run:
1- clone the repo into your workspace
```Bash
$ cd 
$ cd catkin_ws/src/
$ git clone https://github.com/SohaibAl-emara/3D_Lidar_Curb_Detection.git
```
2- build the code
```Bash
$ cd 
$ cd catkin_ws/
$ catkin_make
```
3- run rosmaster
```BASH
$ roscore
```

4- in a different terminal, play the rosbag 
```BASH
$ cd 
$ rosrun control_manager control_node.py 
```
TODO:
[]MANUAL CONTROL USING JOYSTICK