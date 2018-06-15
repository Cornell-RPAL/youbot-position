#!/usr/bin/env python2.7

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from youbot_position.srv import PositionControl, PositionControlResponse


class Controller(object):
  '''A position control service node'''

  def __init__(self):
    #, setpoint_topic='setpoint_x', control_topic='control_x'):
    # set called to False initially, and iniialize publishers that publish
    # intended setpoint and the desired velocity for the youBot.
    self.set_velocity = False
    self.setpoint_pub_x = rospy.Publisher('setpoint_x', Float64, queue_size=5, latch=True)
    self.setpoint_pub_y = rospy.Publisher('setpoint_y', Float64, queue_size=5, latch=True)
    self.velocity_pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
    #  NOTE: I'm storing the velocity as a field because that will make the restructuring easier
    # when the controller is responsible for both X and Y components of the velocity
    self.velocity = Twist()
    # Initialize subscriber that listens to output of PIDs
    self.control_sub_x = rospy.Subscriber('control_x', Float64, self.control_callback)
    self.control_sub_y = rospy.Subscriber('control_y', Float64, self.control_callback)
    # Initialize service that will accept requested positions and set PID setpoints to match
    self.control_service = rospy.Service('position_control', PositionControl,
                                         self.position_control_service)
    rospy.loginfo("Position control service running!")

  # Executes when service is set_velocity; also sets set_velocity to True
  def position_control_service(self, req):
    '''Callback receiving control service requests'''
    if req.stop:
      null_vector = Twist()
      self.velocity_pub.publish(null_vector)
      self.set_velocity = False
      return PositionControlResponse()

    rospy.loginfo("Received request: %s", req)
    self.setpoint_pub_x.publish(req.x)
    self.setpoint_pub_y.publish(req.y)
    self.set_velocity = True
    return PositionControlResponse()

  # Check if service has been set_velocity. If so, while listening to control_topic,
  # set our linear velocity to the data and publish our current velocity.
  def control_callback(self, control):
    '''Callback receiving PID control output'''
    if self.set_velocity:
      self.velocity.linear.x = control.x
      self.velocity.linear.y = control.y
      self.velocity_pub.publish(self.velocity)


# Spin on control_service so that if the service goes down, we stop. This is better than doing it on
# rospy itself because it's more specific (per
# http://wiki.ros.org/rospy/Overview/Services#A.28Waiting_for.29_shutdown)
if __name__ == "__main__":
  rospy.init_node('position_control')
  C = Controller()
  C.control_service.spin()
