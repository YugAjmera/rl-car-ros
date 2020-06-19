#!/usr/bin/env python
import rospy

from nav_msgs.msg import Odometry

def callback(msg):
	print int(msg.pose.pose.position.x * 10)
	print int(msg.pose.pose.position.y * 10)
	print "-----------------------"

rospy.init_node('Sub_Node')
sub = rospy.Subscriber('/odom', Odometry, callback)
rospy.spin()
