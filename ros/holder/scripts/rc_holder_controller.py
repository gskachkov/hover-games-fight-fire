#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image, Joy
from subprocess import Popen
import mavros
from mavros_msgs.msg import RCIn
import os

packageHolded = True
joyPub = True
switch_on = True
switch_off = True


def getJoyMessage(on, off):
    msg = Joy()
    msg.axes = [0, 0, 0, 0, 0, 0]
    msg.buttons = [on, off, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    return msg

# Listen to RC and publish event - start listen DNN (drone movements according to video)
# If px4 contrller from redtail	run it subscribed to event in /joy topic
# https://github.com/gskachkov/redtail/blob/master/ros/packages/px4_controller/src/px4_controller.cpp#L548
# So we send message to run DNN
# https://github.com/gskachkov/redtail/blob/master/ros/packages/px4_controller/src/px4_controller.cpp#L252
# and px4 controller start send message to px4 to change position in space according to iamges
def callbackRCIn(data):
    global joyPub
    global switch_on
    global switch_off

    if data.channels[9] != 1024 and switch_on:
        joyMsg = getJoyMessage(1, 0)        
        joyPub.publish(joyMsg)
        switch_on = False
        switch_off = True
        rospy.loginfo(rospy.get_caller_id() + ' - start dnn ')
    elif data.channels[9] == 1024 and switch_off:
        joyMsg = getJoyMessage(0, 1)
        joyPub.publish(joyMsg)
        switch_off = False
        switch_on = True
        rospy.loginfo(rospy.get_caller_id() + ' - stop dnn ')

# Open holder if we receive message that PX4 controlled dected person.
# /object_dnn/network/output
# field 'data' will contain array with length more that 0 
def callbackDnn(data):
    global packageHolded
    if len(data.data) > 1 and packageHolded:
        rospy.loginfo(rospy.get_caller_id() + 'I see person first time and droping package')
        packageHolded = False
        # Set correct path to python module to run servo and holder 
        Popen(["python3", "/home/alex/holder/ServoKit/open_holder.py"], close_fds=True)


def listener():
    global joyPub
    rospy.init_node('holder_contoller_node')
    rospy.loginfo(rospy.get_caller_id() + "start holder controller")
    mavros.set_namespace('mavros')

    joyPub = rospy.Publisher('/joy', Joy, queue_size=1)

    # Subscribe to messages from remote controller
    rospy.Subscriber(mavros.get_topic('rc/in'), RCIn, callbackRCIn)
    # Subscribe to messages from object detection node
    rospy.Subscriber('/object_dnn/network/output', Image, callbackDnn)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    listener()
