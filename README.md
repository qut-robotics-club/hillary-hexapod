# Hillary the Hexapod

Hillary is QUTRC's long-running hexapod project.

## Mobile Controller

Hillary's software currently hosts a web-app that you can use to control, and calibrate her servos to the correct positions.

Hillary's Raspberry Pi is configured to self-host a hotspot using https://github.com/qut-robotics-club/comitup, which allows you to connect to her as long as she is powered, no external wifi routers needed!

(However they can easily be used to control Hillary globally using https://ngrok.com/)

![robo-controller](/wiki/robo-controller.gif)

The 3D URDF (Unified Robot Description Format) model that you see above is currently ripped from https://github.com/eborghi10/Hexapod-ROS and does not properly represent Hillary in real life, but it's close enough for now.

Making a Solidworks assembly for Hillary needs to be done for more accurate simulation and calibration. Once a Solidworks assembly of Hillary is built, it can be exported to the URDF model that this software requires by installing the free URDF-exporter plugin http://wiki.ros.org/sw_urdf_exporter.

## Hexapod Kinematics

All hexapod kinematics (deciding what angles to move the joints to perform certain actions like walk, rotate and dance) are currently performed through a slightly-modified version of https://github.com/mithi/hexy.

Currently, servo calibration results are stored locally on the Pi, using a pickle file. Eventually, when ROS is integrated, this calibration will be stored as a "ROS parameter".

## Development Environment Setup

First you will want to have 3 things installed.

- [git](https://git-scm.com/download)
- [vscode](https://code.visualstudio.com/) (recommended)
- and [conda](https://docs.conda.io/en/latest/miniconda.html) (if installing on windows, selecting `ADD TO PATH (not recommended)`
  during the installation is actually recommended by us. Although it can cause issues, it makes everything else easier.)
  This install script is cross-platform, and should work on windows, mac or linux.
  All the aforementioned requirements are... required =)

Then run the cross-platform install script with python:

```bash
python install_dev.py
```

## Future Work: ROS Integration

Eventually, Hillary should utilize a more modular approach to kinematics and control using ROS as demonstrated in https://github.com/eborghi10/Hexapod-ROS.

This will enable members interested in experimenting with Hillary to swap out different software-subsystems at a whim and replace them with another one written in any chosen programming language (either with a local client library or by interfacing with the `rosbridge` websocket server).

For example, you could write a Lidar sensor processing algorithm in MATLAB that subscribes to [Lidar messages](https://docs.ros.org/api/sensor_msgs/html/msg/LaserScan.html) looking at the ground around the hexapod, publishing [tf2 Transforms](http://docs.ros.org/kinetic/api/tf2/html/classtf2_1_1Transform.html) for ideal foot placement.

Another engineer may then write a motion planner in Python utilizing [ROS Moveit](http://docs.ros.org/kinetic/api/moveit_tutorials/html/doc/move_group_python_interface/move_group_python_interface_tutorial.html) that performs out collision-free inverse-kinematics for the leg in question, publishing a [JointTrajectory](http://docs.ros.org/melodic/api/trajectory_msgs/html/msg/JointTrajectory.html).

A third engineer may then write a low-level hardware controller in C++ that utilizes [ROS Control](https://github.com/ros-controls/ros_control/wiki/hardware_interface) to interact with the MiniMaestro servo board over serial.

Another great advantage of using ROS is instantaneous integration with the [Gazebo Robot & Environment Simulator](http://gazebosim.org/) which will allow us to test and train Hillary's algorithms in simulated environments without having to worry about physical limitations (but ROS Control helps you model those as well!).

ROS and Gazebo were recently ported to Windows (early 2020). This means that Windows users can now use ROS for simulation and development as well without requiring linux emulation.

```

```
