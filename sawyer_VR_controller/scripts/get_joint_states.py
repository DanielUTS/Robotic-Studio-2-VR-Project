#! /usr/bin/env python

## \file
# \brief This file demonstrates the usage of ROS to subscribe to joint state messages and publish the joint positions and velocities in a Float32MultiArray message.

import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32MultiArray

## \brief Callback function for the joint states.
#
# \param msg The joint state message.
def callback_joints(msg):
    pos = msg.position
    vel = msg.velocity

    rospy.loginfo(pos)
    state_msg = Float32MultiArray()
    state_msg.data = pos + vel
    pub.publish(state_msg)

if __name__ == '__main__':
    rospy.init_node('listener_node')

    sub = rospy.Subscriber('robot/joint_states', JointState, callback_joints)

    pub = rospy.Publisher('state_listener', Float32MultiArray, queue_size=1)

    loop_rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        loop_rate.sleep()
