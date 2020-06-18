## Dependencies

```bash
sudo apt-get install ros-melodic-gazebo-ros-pkgs ros-melodic-gazebo-ros-control
sudo apt install ros-melodic-controller-manager
```

## Commands

```bash
roslaunch rl-car-ros gazebo.launch
roslaunch rl-car-ros mybot_control.launch
```

After this, perform a quick ```rostopic list```. You should be able to see ```/cmd_vel``` and ```/mybot/laser/scan``` topics. Both use standard message types. 
