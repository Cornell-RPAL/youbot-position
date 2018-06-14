#!/usr/bin/env python2.7

import rospy
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
from youbot_position.srv import PositionControl, PositionControlResponse


class Controller(object):
  '''A position control service node'''

  def __init__(self, setpoint_topic='setpoint_x', control_topic='control_x'):
    # set called to False initially, and iniialize publishers that publish
    # intended setpoint and the desired velocity for the youBot.
    self.called = False
    self.setpoint_pub = rospy.Publisher(setpoint_topic, Float64, queue_size=5, latch=True)
    self.velocity_pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
    #  NOTE: I'm storing the velocity as a field because that will make the restructuring easier
    # when the controller is responsible for both X and Y components of the velocity
    self.velocity = Twist()
    # Initialize subscriber that listens to output of PIDs
    self.control_sub = rospy.Subscriber(control_topic, Float64, self.control_callback)
    # Initialize service that will accept requested positions and set PID setpoints to match
    self.control_service = rospy.Service('position_control', PositionControl,
                                         self.position_control_service)
    rospy.loginfo("Position control service running!")

  # Executes when service is called; also sets called to True
  def position_control_service(self, req):
    '''Callback receiving control service requests'''
    rospy.loginfo("Received request: %s", req)
    self.setpoint_pub.publish(req.x)
    self.called = True
    return PositionControlResponse()

  # Check if service has been called. If so, while listening to control_topic,
  # set our linear velocity to the data and publish our current velocity.
  def control_callback(self, control):
    '''Callback receiving PID control output'''
    if not self.called:
      return

    self.velocity.linear.x = control.data
    self.velocity_pub.publish(self.velocity)


# Spin on control_service so that if the service goes down, we stop. This is better than doing it on
# rospy itself because it's more specific (per
# http://wiki.ros.org/rospy/Overview/Services#A.28Waiting_for.29_shutdown)
if __name__ == "__main__":
  rospy.init_node('position_control')
  C = Controller()
  C.control_service.spin()