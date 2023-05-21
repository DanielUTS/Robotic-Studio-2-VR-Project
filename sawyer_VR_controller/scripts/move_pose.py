#!/usr/bin/env python

## \file
# \brief This file demonstrates the usage of MoveIt for trajectory planning and execution in a ROS project.

import sys
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from trajectory_msgs.msg import JointTrajectoryPoint

## \brief Concatenates multiple trajectories into a single composite trajectory.
#
# \param trajectories A list of trajectories to concatenate.
# \return The composite trajectory of all the points.
def concatenate_trajectories(trajectories):
    composite_traj = moveit_msgs.msg.RobotTrajectory()
    composite_traj.joint_trajectory.joint_names = trajectories[0].joint_trajectory.joint_names

    for traj in trajectories:
        time_offset = rospy.Duration(0) if len(composite_traj.joint_trajectory.points) == 0 else composite_traj.joint_trajectory.points[-1].time_from_start

        for point in traj.joint_trajectory.points:
            new_point = JointTrajectoryPoint()
            print(point.positions)
            new_point.positions = point.positions
            new_point.velocities = point.velocities if point.velocities else []
            new_point.accelerations = point.accelerations if point.accelerations else []
            new_point.time_from_start = point.time_from_start + time_offset
            composite_traj.joint_trajectory.points.append(new_point)

    return composite_traj

# Initialize ROS node and MoveIt commander
moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node('move_group_python_interface_tutorial', anonymous=True)
robot = moveit_commander.RobotCommander()
scene = moveit_commander.PlanningSceneInterface()
group = moveit_commander.MoveGroupCommander("right_arm")
group.set_max_velocity_scaling_factor(0.2)
group.set_max_acceleration_scaling_factor(0.6)
display_trajectory_publisher = rospy.Publisher('/move_group/display_planned_path', moveit_msgs.msg.DisplayTrajectory, queue_size=1)

# Set the goal tolerance to avoid collision and singularities
group.set_goal_tolerance(0.05)

# list of singularities for each type of them
singularities = [
    [0.3, -1.2, 0.8, 0.5, 1.2, -2.5, 2.5],  # Joint Limit Singularity
    [1.2, 0.7, 2.8, 0.0, 0.0, 0.0, 1.5],    # Wrist Singularity
    [0.5, 1.5, -0.8, 0.0, 1.8, 0.3, 0.9],    # Elbow Singularity
    [1.8, -0.5, 0.9, 0.7, 1.2, 1.5, -1.4],   # Shoulder Singularity
    [0.9, 0.4, 1.2, -0.5, 1.8, 0.9, 1.2],    # Reach Singularity
    [0.6, 0.4, 0.8, 1.2, -1.5, 1.0, -0.9]    # Jacobian Singularity
]

plans = []
for singularity in singularities:
    group.set_joint_value_target(singularity)
    plan = group.plan()
    plans.append(plan)

composite_traj = concatenate_trajectories(plans)
group.execute(composite_traj)

# Define the target position in 3D space
target_pose = geometry_msgs.msg.Pose()
target_pose.position.x = 0.5
target_pose.position.y = 0.0
target_pose.position.z = 0.5
group.set_pose_target(target_pose)

# Define and execute the plan to reach the target position
plan = group.plan()
group.execute(plan, wait=True)
rospy.sleep(1)

# Shutdown the MoveIt commander
moveit_commander.roscpp_shutdown()
