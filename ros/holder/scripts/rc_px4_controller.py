#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image, Joy
from subprocess import Popen
import mavros
from mavros_msgs.msg import RCIn
import os


run_px4_contoller = True

# If we receive value in channel 8 we run px4 contoller 
def callbackRCIn(data):
    global run_px4_contoller

    if data.channels[8] != 1024 and run_px4_contoller:
        rospy.loginfo(rospy.get_caller_id() + 'I run run_px4_contoller ')
        run_px4_contoller = False
        os.system('rosrun px4_controller px4_controller_node _altitude_gain:=0 _linear_speed=3 _joy_type:="shield" _obj_det_limit:=0.3')


def listener():
    global joyPub
    rospy.init_node('px4_contoller_node')
    rospy.loginfo(rospy.get_caller_id() + "Start work")
    mavros.set_namespace('mavros')

    # Subscribe to messages from remote controller
    rospy.Subscriber(mavros.get_topic('rc/in'), RCIn, callbackRCIn)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    listener()
