# Control a Cobot using a virtual reality controller.

The aim of this project is to connect a VR system to a robot that enables users to control 
the robot arm by moving their own arms and grip items using a gripper end effector. 
The end goal is to be able to perform a variety of tasks using the VR controller and different end effector. 

## Setup ROS environment

First to make this project work you need to setup the ROS Melodic environment on a Ubuntu 18.04 OS. To create the appropriate environment follow the tutorial on the official ROS [website](http://wiki.ros.org/melodic/Installation/Ubuntu) 

## Installing dependecies for the Sawyer robot

This project will use a Sawyer Robot of Rethink Robotics. We need to connect the Sawyer Robot by following the tutorial on the Rethink Robotics [website](https://www.rethinkrobotics.com/)  create the `catkin_ws` folder and the require dependencies indiquated in the website.

## Connection bewteen master computer and robots

To establish a connection between the robot and the master you need a router and connect your device with a static IP address. To setup your ROS environment with the robot you need to:
 
- add to the `~/.bashrc` file the following line 
> export ROS_MASTER_URI=http://Your_Master_IP:11311

> export ROS_IP=Sawyer_IP

- change the `intera.sh` file accordingly to the tutorial

Check the SDK version on the Sawyer robot and your master computer. We advise to update to the version 5.3.0 or up both of them to be sure not to have version collision.

## Initialize the robot

to initialize the Sawyer robot functions execute the following commands.
```bash
cd ~/catkin_ws
./intera.sh
rosrun intera_interface enable_robot.py -e
```
## Other Dependencies

To be able to run this project you will need to install the Driver to make the razer hydra work. 

```bash
cd ~/catkin_ws/src
git clone https://github.com/ros-drivers/razer_hydra
sudo cp razer_hydra/config/99-hydra-indigo.rules /etc/udev/rules.d/
```
then reboot your Ubuntu to make reload the udev rules

you can then test if the package work properly by doing the following commands.

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
roslaunch razer_hydra hydra_rviz.launch
```
If the controller are connected, it will open the RViz software with the tf representation of the controller position from the base. Make sure the ROS Master work properly or this will not work.

## Run the VR command 

To control the robot with the controllers you need to run in one terminal the following command

```bash
roslaunch sawyer_VR_controller main.launch
```
this should run three different process