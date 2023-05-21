#!/usr/bin/env python

## \file
# \brief This file demonstrates the usage of MoveIt for controlling a robot arm using Hydra input in a ROS project.

import tf
import rospy
import sys
import moveit_commander
import numpy as np
from geometry_msgs.msg import Pose, Point, Quaternion
from intera_core_msgs.msg import EndpointState
from trajectory_msgs.msg import JointTrajectoryPoint
import moveit_msgs.msg
from razer_hydra.msg import Hydra

## \brief Class for controlling the robot arm using Hydra input.
class HydraCtrl:
	def __init__(self):
		## \var xyz
		# \brief Position of the Hydra input.
		self.xyz = None

		## \var rotation
		# \brief Rotation of the Hydra input.
		self.rotation = None

		## \var joy
		# \brief Joy values of the Hydra input.
		self.joy = [0, 0]

		## \var buttons
		# \brief Button values of the Hydra input.
		self.buttons = [0, 0, 0, 0, 0, 0, 0]

		## \var trigger
		# \brief Trigger value of the Hydra input.
		self.trigger = 0

		## \var state
		# \brief State of the Hydra input.
		self.state = False

		## \var diff_pose
		# \brief Difference pose calculated from the Hydra input.
		self.diff_pose = Pose()

		## \var scale
		# \brief Scaling factor for the difference pose.
		self.scale = 0.5

		## \var key
		# \brief Key value for controlling the behavior.
		self.key = True


	## \brief Callback function for the Hydra input.
	#
	# \param msg The Hydra input message.
	def hydra_callback(self, msg):
		paddle = msg.paddles[0]
		self.xyz = paddle.transform.translation
		self.rotation = paddle.transform.rotation
		self.buttons = paddle.buttons
		self.joy = paddle.joy
		self.trigger = paddle.trigger
		if self.key:
			print("key")
			self.pressed = True
			self.state = True
			self.diff_pose.position.x += (self.joy[1]) * 0.001
			self.diff_pose.position.y += (self.joy[0]) * 0.001
			self.diff_pose.position.z -= (self.buttons[1] + self.buttons[2]) * 0.01
		else:
			if self.buttons[0] ^ self.state:
				self.state = not self.state
				self.ori_xyz = self.xyz
				self.ori_rot = self.rotation
			if self.state:
				diff_rot = self.sub_rot()
				diff_xyz = Point(
					self.xyz.x - self.ori_xyz.x,
					self.xyz.y - self.ori_xyz.y,
					self.xyz.z - self.ori_xyz.z
				)
				self.diff_pose = Pose(diff_xyz, diff_rot)

	## \brief Calculates the difference rotation between the current rotation and the original rotation.
	#
	# \return The difference rotation.
	def sub_rot(self):
		# (C_x, C_y, C_z, C_w) * (-S_x, -S_y, -S_z, S_w)
		q1 = np.array([self.rotation.x, self.rotation.y, self.rotation.z, self.rotation.w])
		q2 = np.array([self.ori_rot.x, self.ori_rot.y, self.ori_rot.z, self.ori_rot.w])

		# Invert the second quaternion
		q2_inv = np.array([-self.ori_rot.x, -self.ori_rot.y, -self.ori_rot.z, self.ori_rot.w])

		# Perform quaternion subtraction
		result = np.multiply(q1, q2_inv)

		# Normalize the result to ensure it remains a unit quaternion
		result /= np.linalg.norm(result)

		# Create a new Quaternion object to store the result
		result_quaternion = Quaternion()
		result_quaternion.x = result[0]
		result_quaternion.y = result[1]
		result_quaternion.z = result[2]
		result_quaternion.w = result[3]
		return self.rotation

	## \brief Callback function for the arm pose.
	#
	# \param msg The arm pose message.
	def callback_arm_pose(self, msg):
		print("test in")

		current_pose = msg.pose
		if self.state:
			rospy.loginfo("pressed")

			print(current_pose.position.x, current_pose.position.y, current_pose.position.z)
			goal_pose = add_pose(current_pose, self.diff_pose, self.scale)
			print(self.diff_pose.position.x, self.diff_pose.position.y, self.diff_pose.position.z)
			if self.diff_pose.position.x != 0 or self.diff_pose.position.y != 0 or self.diff_pose.position.z != 0:
				# Set target pose and plan
				self.group.set_pose_target(goal_pose)
				plan = self.group.plan()

				if plan.joint_trajectory.points:
					rospy.logerr("Executing plan")
					# Execute the plan
					self.group.execute(plan, wait=True)
				else:
					rospy.logerr("Failed to find a valid plan")

## \brief Adds two poses together.
#
# \param pose1 The first pose.
# \param pose2 The second pose.
# \param scale The scaling factor for the second pose.
# \return The sum of the two poses.
def add_pose(pose1, pose2, scale):
	result_pose = Pose()
	result_pose.position = Point(
		pose1.position.x + pose2.position.x * scale,
		pose1.position.y + pose2.position.y * scale,
		pose1.position.z + pose2.position.z * scale
	)

	result_pose.orientation = Quaternion(
		pose1.orientation.x,
		pose1.orientation.y,
		pose1.orientation.z,
		pose1.orientation.w
	)
	return result_pose

## \brief The main function.
def main():
	# Initialize the moveit_commander
	moveit_commander.roscpp_initialize(sys.argv)
	rospy.init_node('sawyer_hydra_follow_moveit')

	# Subscribe to the 'hydra_calib' topic
	hydra = HydraCtrl()
	sub1 = rospy.Subscriber("hydra_calib", Hydra, hydra.hydra_callback)

	sub2 = rospy.Subscriber("robot/limb/right/endpoint_state", EndpointState, hydra.callback_arm_pose)

	# Initialize the robot and MoveGroupCommander for the arm
	hydra.robot = moveit_commander.RobotCommander()
	hydra.group = moveit_commander.MoveGroupCommander("right_arm")
	hydra.group.set_max_acceleration_scaling_factor(0.3)
	hydra.group.set_max_velocity_scaling_factor(0.8)

	rate = rospy.Rate(10)  # 10 Hz update rate

	rate.sleep()

	rospy.spin()

if __name__ == '__main__':
	try:
		main()
	except rospy.ROSInterruptException:
		pass
