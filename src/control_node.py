#!/usr/bin/env python
import rospy
from ackermann_msgs.msg import AckermannDriveStamped
from sensor_msgs.msg import Joy
from pynput import keyboard
import time

class msg_manager:
    # 1 -> manually joystick   2 -> manually keyboard  3-> semi sim_autonmous   4-> full autonmous
    def __init__(self, steering_mode = 1, force_stop = 0, msg_full_auto = AckermannDriveStamped(),
                msg_semi_auto = AckermannDriveStamped(),msg_manual = AckermannDriveStamped(),
                default_left = 2, default_right = -2, speed = 0, steering_angle = 0, speed_multipyer = 1):
        self.steering_mode = steering_mode
        self.force_stop = force_stop
        self.msg_full_auto = msg_full_auto
        self.msg_semi_auto = msg_semi_auto
        self.msg_manual = msg_manual
        self.default_speed = rospy.get_param("sim_speed", 2)
        rospy.logwarn('sim_speed = ' + str(self.default_speed))
        self.default_left = default_left
        self.default_right = default_right
        self.speed = speed
        self.steering_angle = steering_angle
        self.speed_multipyer= speed_multipyer


    def pid_callback(self, data):
        # full autonmous
        if self.steering_mode == 3:
            self.msg_full_auto = data
        # semi autonmous
        elif self.steering_mode == 2:
            pass
            # self.msg_semi_auto = data
            # self.msg_semi_auto.drive.speed = self.speed

    def on_press_key(self, key):
        try:
            # space changes steering mode
            if key == keyboard.Key.space:
                if self.steering_mode == 1:
                    rospy.loginfo('MANUAL mode keyboard')
                    self.steering_mode = 2

                elif self.steering_mode == 2:
                    rospy.loginfo('sim_autonmous mode')
                    self.steering_mode = 3

                elif self.steering_mode == 3:
                    rospy.loginfo('FULL_autonmous mode')
                    self.steering_mode = 4

                elif self.steering_mode == 4:
                    rospy.loginfo('MANUAL mode joystick')
                    self.steering_mode = 1

            if(key.char == 'r'):
                if(self.force_stop == 1):
                    self.speed = self.default_speed/2
            elif (key.char == 'e'):
                self.speed = -self.default_speed/2

            elif(key.char == 'a'):
                if(self.force_stop == 1):
                    self.steering_angle = self.default_left
                    #self.speed = 0
                else:
                    #rospy.loginfo('left')
                    self.speed = self.default_speed/2
                    self.steering_angle = self.default_left
            elif(key.char =='d'):
                if(self.force_stop == 1):
                    self.steering_angle = self.default_right
                    #self.speed = 0
                else:
                    #rospy.loginfo('right')
                    self.speed = self.default_speed/2
                    self.steering_angle = self.default_right
            elif(key.char == 'w'):
                if(self.force_stop == 1):
                    self.steering_angle = self.default_left*2
                    #self.speed = 0
                else:
                    #rospy.loginfo('forward')
                    self.speed = self.default_speed
                    self.steering_angle = 0
            elif(key.char == 's'):
                if(self.force_stop == 1):
                    self.steering_angle = self.default_right*2
                    #self.speed = 0
                else:
                    #rospy.loginfo('backwards')
                    self.speed = - self.default_speed
                    self.steering_angle = 0

        except AttributeError:
            pass


    def on_release_key(self, key):
        try:
            if key.char == 'w' or key.char == 's' or key.char == 'd' or key.char == 'a' or  key.char == 'r' or key.char == 'e' or key.char == 'f' or key == keyboard.Key.space:
                self.speed = 0
                self.steering_angle = 0
            elif key == keyboard.Key.esc:
                rospy.signal_shutdown('closed by Esc')
                # Stop listener
                return False
        except AttributeError:
            pass

    def joy_callback (self, data):
        try:
            if data.buttons[0] == 1: # breaking
                self.speed = 0
                self.steering_angle = 0
                # this can be breaking by putting the motor on revers
            if data.axes[5] == -1 :
                if data.buttons[0] == 0 :
                    self.speed = data.axes[1]*self.speed_multipyer + 0
                    self.steering_angle = data.axes[2]*self.speed_multipyer + 0

                if (data.buttons[4]== 1 ): # speed up
                    self.speed_multipyer = self.speed_multipyer +1
                    if self.speed_multipyer > 5:
                        self.speed_multipyer = 5
                    time.sleep(0.1)

                if (data.buttons[5] == 1): # speed down
                    self.speed_multipyer = self.speed_multipyer - 1
                    if self.speed_multipyer < 1 :
                        self.speed_multipyer = 1
                    time.sleep(0.1)

            else :
                self.speed = 0
                self.steering_angle = 0
            # control mode
            if data.buttons[3] == 1 :
                if self.steering_mode == 1:
                    rospy.loginfo('MANUAL mode keyboard')
                    self.steering_mode = 2

                elif self.steering_mode == 2:
                    rospy.loginfo('sim_autonmous mode')
                    self.steering_mode = 3

                elif self.steering_mode == 3:
                    rospy.loginfo('FULL_autonmous mode')
                    self.steering_mode = 4

                elif self.steering_mode == 4:
                    rospy.loginfo('MANUAL mode joystick')
                    self.steering_mode = 1

            # if (data.buttons[0]== 1) :
            #     #breaking using breaking system
            #

        except AttributeError:
                pass



    def publish(self, pub):
        #rospy.loginfo("publish")
        if self.steering_mode == 1 or self.steering_mode == 2:
            self.msg_manual.drive.speed = self.speed
            self.msg_manual.drive.steering_angle = self.steering_angle
            self.msg_manual.drive.acceleration = 1
            self.msg_manual.drive.steering_angle_velocity = 10
            pub.publish(self.msg_manual)

        elif self.steering_mode == 3:
            pub.publish(self.msg_semi_auto)

        elif self.steering_mode == 4:
            pub.publish(self.msg_full_auto)

## main
if __name__ == '__main__':
    rospy.init_node('control_mode', anonymous=True)
    manager = msg_manager()
    pub = rospy.Publisher('/rbcar_robot_control/command', AckermannDriveStamped, queue_size=1)
    rospy.Subscriber('/joy', Joy, manager.joy_callback, queue_size=1)

    listener = keyboard.Listener(
                on_press_key=manager.on_press_key,
                on_release_key=manager.on_release_key)
    listener.start()
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        manager.publish(pub)
        rate.sleep()

    rospy.signal_shutdown("manually closed")
