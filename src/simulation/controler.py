#!/usr/bin/env python2
from numpy import *
import matplotlib.pyplot as plt
import numpy as np
from numpy import cos,sin

import rospy
from std_msgs.msg import String
from std_msgs.msg import Float32
from geometry_msgs.msg import Vector3
from geometry_msgs.msg import Point

def sawtooth(x):
    return (x+np.pi)%(2*np.pi)-np.pi   # or equivalently   2*arctan(tan(x/2))

##############################################################################################
#      Controle
##############################################################################################

def controle(x, q):

	r = 2 #5
	zeta = pi/4

	x=x.flatten()
	theta=x[2]

	m = array([[x[0]], [x[1]]])
	e = linalg.det(hstack(((b-a)/linalg.norm(b-a), m-a)))
	#print(e)
	phi = arctan2(b[1,0]-a[1,0], b[0,0]-a[0,0])

	if abs(e) > r:
	    q = sign(e)

	thetabar = phi - arctan(e/r)

	if (cos(psi-thetabar)+cos(zeta))<0:
	    thetabar = pi+psi-zeta*q

	deltar = 2/pi*arctan(tan(0.5*(theta-thetabar)))
	deltamax = pi/4*(cos(psi-thetabar)+1)
	rospy.loginfo((sawtooth(psi-theta)/2,pi/4*(cos(psi-thetabar)+1)))
	u = array([[deltar],[deltamax]])
	return u, q

##############################################################################################
#      ROS
##############################################################################################

def sub_xy(data):
	global pos_x, pos_y, delta_s
	#rospy.loginfo("Pos x : %s, Pos y : %s",data.x, data.y)
	pos_x = data.x
	pos_y = data.y
	delta_s = data.z

def sub_wind_direction(data):
	global psi
	psi = data.data

def sub_wind_force(data):
	global awind
	awind = data.data

def sub_theta(data):
	global theta
	#rospy.loginfo("Imu heading %s ",data.orientation.x)
	theta = data.x

##############################################################################################
#      Main
##############################################################################################

pos_x, pos_y = 0, 0
awind, psi = 0, 0
theta = 0
delta_s = 0

if __name__ == '__main__':

	a = array([[-75],[40]])   
	b = array([[175],[-40]])
	q = 1
	rospy.init_node('controler')
	rospy.Subscriber("simu_send_theta", Vector3, sub_theta)
	rospy.Subscriber("simu_send_xy", Point, sub_xy)
	rospy.Subscriber("simu_send_wind_direction", Float32, sub_wind_direction)
	rospy.Subscriber("simu_send_wind_force", Float32, sub_wind_force)

	pub_send_u_rudder = rospy.Publisher('control_send_u_rudder', Float32, queue_size=10)
	pub_send_u_sail   = rospy.Publisher('control_send_u_sail', Float32, queue_size=10)
	u_rudder_msg = Float32()
	u_sail_msg   = Float32()
	while not rospy.is_shutdown():
		x = array([[pos_x,pos_y,theta]]).T

		fut_x = x + 4*array([[np.cos(theta),np.sin(theta),0]]).T
		u, q  = controle(fut_x,q)

		u_rudder_msg.data = u[0,0]
		u_sail_msg.data = u[1,0]
		pub_send_u_rudder.publish(u_rudder_msg)
		pub_send_u_sail.publish(u_sail_msg)
