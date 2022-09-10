import threading
import pygame
import PyQt5.QtWidgets as qtw
import sys
import math
import client
from client import Client
import threadcom
import socket 
from PyQt5.QtGui import  QImage,QPixmap

import queue
q=queue.Queue()




class joystick():

    def __init__(self): 
        # super().__init__()
        self.rc_channel_values=[1500 for _ in range(9)]   #initial thrusters PWMS 
        self.initial_servo_us=1500                        #initial servo us
       
        #joystick axes
        self.forward_backwards_axis=1
        self.right_left_axis=0
        self.up_down_axis=3
      
        #joystick hats
        self.pitch_up=(0,1)
        self.pitch_down=(0,-1)
        self.yaw_right=(1,0)
        self.yaw_left=(-1,0)
       
        #joystick buttons
        self.btn_gripper1=4
        self.btn_gripper2=5
        self.btn_led=6
        self.btn_servo_up=3
        self.btn_servo_down=0
        self.btn_speed_up=5
        self.btn_arm_disarm=7
        self.btn_alt_hold=0
        self.btn_stabilize=1
        self.btn_manual=2
        
      
        #interval of error
        self.error=0.4
       
        #flags
        self.flag_led=0
        self.flag_gripper1=1
        self.flag_gripper2=1
        self.servo_flag=0
        self.flag_yaw_right=0
        self.flag_yaw_left=0
        self.flag_pitch=0
        self.flag_forward=0
        self.flag_lateral=0
        self.flag_throttle=0
        self.flag_speed_up=0
        self.flag_servo=0
        self.flag_arm=0
        self.flag_forward_arrow=0
        self.flag_backward_arrow=0
        self.flag_up_arrow=0
        self.flag_down_arrow=0
        self.flag_right_arrow=0
        self.flag_left_arrow=0
      
        #ranges 
        self.max_slow_speed=1650
        self.min_slow_speed=1350
        self.max_PWM=1800             #maximum :safety of thrusters
        self.min_PWM=1200
        self.max_us=1900              #max angle of servo
        self.min_us=1100
        self.pwm_pitch_yaw=150         ###1500 +or- 150  ???
       
        #mapping
        self.b=1500                            #(min pwm +max pwm)/2
        self.a1=self.max_PWM-1500              #mapping high speed
        self.a2=self.max_slow_speed-1500       #mapping low speed
        
        #GUI_guage
        self.guage_value=0
        self.flt_array=[1500,1500,1500] #forward lateral and throttle pwms
        
        events_thread=threading.Thread(target=self.events)
        events_thread.start()
        


    def events(self):

        while True:

            for event in pygame.event.get():
                print(event)  # < -- to check where are we?!

                #axes (forward,lateral,throttle)
                if hasattr(event,'axis'):
                    if event.axis== self.forward_backwards_axis:

                        if event.value < self.error and event.value > -self.error:         #error interval

                            self.flag_forward=0
                            self.rc_channel_values=self.forward(self.rc_channel_values,1500)

                            if (self.flag_forward_arrow==1):
                               # mw.forward_arrow_off()
                                self.flag_forward_arrow=0

                            if (self.flag_backward_arrow==1):
                                #mw.backward_arrow_off()
                                self.flag_backward_arrow=0
                                                        
                        else:
                            self.flag_forward=1
                            self.event_forward_value=event.value  

                            if self.flag_speed_up%2==1: ##high speed
                                self.a=self.a1                                  
                            else:                       ##low speed
                                self.a=self.a2
                            #mapping pwm                            
                            self.PWM=-self.a*self.event_forward_value+self.b
                            self.PWM=int(self.PWM)
                            self.rc_channel_values=self.forward(self.rc_channel_values,self.PWM)
                            if self.PWM>1500:
                                self.flag_forward_arrow=1
                            else:
                                #mw.backward_arrow_on()
                                self.flag_backward_arrow=1
                            #print("forward",self.PWM)

                    if event.axis== self.right_left_axis:
                        if event.value < self.error and event.value > -self.error:          #error interval
                            
                            self.rc_channel_values=self.lateral(self.rc_channel_values,1500)
                            self.flag_lateral=0
                            if (self.flag_right_arrow==1):
                                #mw.right_arrow_off()
                                self.flag_right_arrow=0
                            if (self.flag_left_arrow==1):
                               # mw.left_arrow_off()
                                self.flag_left_arrow=0
                           

                        else:
                            self.flag_lateral=1
                            self.event_lateral_value=event.value
                            
                            if self.flag_speed_up%2==1:   #high speed                                
                                self.a=self.a1                                
                            else:                         #low speed
                                self.a=self.a2
                            #mapping pwm                        
                            self.PWM=self.a*self.event_lateral_value+self.b
                            self.PWM=int(self.PWM)
                            self.rc_channel_values=self.lateral(self.rc_channel_values,self.PWM)
                            if (self.PWM<1500):
                               # mw.left_arrow_on()
                               q.put("left")
                               self.flag_left_arrow=1
                            else:
                                #mw.right_arrow_on()
                                q.put("right")
                                self.flag_right_arrow=1
                            #print("lateral",self.PWM)

                        
                    if event.axis== self.up_down_axis:
                        if event.value < self.error and event.value > -self.error:       #error interval   
                            
                            self.rc_channel_values=self.throttle(self.rc_channel_values,1500)
                            self.flag_throttle=0
                            
                            if (self.flag_down_arrow==1):
                               # mw.down_arrow_off()
                                self.flag_down_arrow=0
                            if (self.flag_up_arrow==1):
                                #mw.up_arrow_off()
                                self.flag_up_arrow=0
                            
                            
                        else:
                            self.flag_throttle=1
                            self.event_throttle_value=event.value
                            
                            if self.flag_speed_up%2==1:             #high speed
                                self.a=self.a1
                            else:                                   #low speed
                                self.a=self.a2
       
                            self.PWM=-self.a*self.event_throttle_value+self.b
                            self.PWM=int(self.PWM)
                            
                            self.rc_channel_values=self.throttle(self.rc_channel_values,self.PWM)
                            if (self.PWM<1500):
                                #mw.down_arrow_on()
                                self.flag_down_arrow=1
                            else:
                               # mw.up_arrow_on()
                                self.flag_up_arrow=1
                            
                            #print(self.rc_channel_values,self.guage_value)
                            #print("throttle",self.PWM)

                            
                #buttons(servo up,servo down,speeding up,arming & disarming,leds on & off)
                if hasattr(event,'button'):

                    # if event.button==self.btn_servo_up:
                        
                    #         if self.servo_flag==0:  
                    #             self.servo_flag=1
                    #             thread_servo_up=threading.Thread(target=self.servo_up)
                    #             thread_servo_up.start()
                    #         else:
                    #             self.servo_flag=0

                    # if event.button==self.btn_servo_down:
                    #         if self.servo_flag==0:
                    #             self.servo_flag=1
                    #             thread_servo_up=threading.Thread(target=self.servo_down)
                    #             thread_servo_up.start()
                    #         else:
                    #             self.servo_flag=0

                    if event.button==self.btn_speed_up:
                        self.flag_speed_up+=1
                        if self.flag_speed_up%2==1:  #high speed
                            self.a=self.a1
                        else:                    #low speed       
                            self.a=self.a2 

                        if self.flag_forward==1:
                            #mapping pwm
                            self.PWM=-self.a*self.event_forward_value+self.b
                            self.PWM=int(self.PWM)
                            self.rc_channel_values=self.forward(self.rc_channel_values,self.PWM)
                          
                            #print("forward",self.PWM)

                        if self.flag_lateral==1:
                            #mapping pwm
                            self.PWM=self.a*self.event_lateral_value+self.b
                            self.PWM=int(self.PWM)
                            self.rc_channel_values=self.lateral(self.rc_channel_values,self.PWM)
                            #print("lateral",self.PWM)

                        if self.flag_throttle==1:
                            #mapping pwm
                            self.PWM=-self.a*self.event_throttle_value+self.b
                            self.PWM=int(self.PWM)
                            self.rc_channel_values=self.throttle(self.rc_channel_values,self.PWM)
                            #print("throttle",self.PWM)

                    if event.button==self.btn_arm_disarm:
                        self.flag_arm+=0.5
                        if self.flag_arm%2==1:
                            self.arm()
                            
                        elif self.flag_arm%2==0:
                            self.disarm()
                            
                    if event.button==self.btn_led:
                        self.flag_led+=0.5
                        if self.flag_led%2==1:
                            self.led_on()
                           # mw.leds_on()
                            self.flag_led=1
                        elif self.flag_led%2==0:
                            self.led_off()
                            #mw.leds_off()
                            self.flag_led=0
                    
                    if event.button==self.btn_gripper1:
                        self.flag_gripper1+=0.5
                        if self.flag_gripper1%2==1:
                            self.open_gripper1()
                            #mw.open_gripper()
                            self.flag_gripper1=1
                        elif self.flag_gripper1 %2==0: 
                            self.close_gripper1()
                            #mw.close_gripper()
                            self.flag_gripper1=0
                    
                    if event.button==self.btn_gripper2:
                        self.flag_gripper2+=0.5
                        if self.flag_gripper2%2==1:
                            self.open_gripper2()
                            #mw.open_gripper()
                            self.flag_gripper2=1
                        elif self.flag_gripper2%2==0:
                            self.close_gripper2()
                            #mw.close_gripper()
                            self.flag_gripper2=0

                    # if event.button==self.btn_led:
                    #     self.flag_led+=0.5
                    #     if self.flag_led%2==1:
                            
                    #         self.led_on()
                    #         #mw.open_gripper()
                    #         self.flag_led=1
                    #     elif self.flag_led%2==0:
                    #         self.led_off()
                    #         #mw.close_gripper()
                    #         self.flag_led=0
                        
                    if event.button==self.btn_alt_hold:
                        self.alt_hold()
                    
                    if event.button==self.btn_manual:
                        self.manual()

                    if event.button==self.btn_stabilize:
                        self.stabilize()


                #hats (pitch,yaw)
                if hasattr(event,"hat"):
            
                    if event.value == self.pitch_up:

                        self.flag_pitch=1 
                        self.rc_channel_values=self.pitch(self.rc_channel_values,1500+self.pwm_pitch_yaw)
                      
                    if event.value == self.pitch_down:
                                
                        self.flag_pitch=1
                        self.rc_channel_values=self.pitch(self.rc_channel_values,1500-self.pwm_pitch_yaw)
                        
                    if event.value == self.yaw_right:

                        self.flag_yaw_right=1
                        self.rc_channel_values=self.yaw(self.rc_channel_values,1500+self.pwm_pitch_yaw)
                        #mw.cw_arrow_on()
                        
                    if event.value == self.yaw_left:

                        self.flag_yaw_left=1
                        self.rc_channel_values=self.yaw(self.rc_channel_values,1500-self.pwm_pitch_yaw)
                        #mw.ccw_arrow_on()
                        
                    if event.value == (0,0):
                        if self.flag_pitch==1:
                            self.flag_pitch=0
                            self.rc_channel_values=self.pitch(self.rc_channel_values,1500)
                            
                        else:
                            self.flag_yaw_right=0
                            self.flag_yaw_left=0
                            self.rc_channel_values=self.yaw(self.rc_channel_values,1500)
                            #mw.cw_arrow_off()
                            #mw.ccw_arrow_off()
                           

    # def servo_up(self):
        
    #     while self.servo_flag==1 and self.initial_servo_us<self.max_us:    #condition fails when reaching max_us or button not clicked 
            
    #                 self.initial_servo_us+=3
    #                 msg="se"+str(self.initial_servo_us)
    #                 clientO.sender(msg) #####################################
    #                 print("servo up")

    #     print("servo stable") 

    # def servo_down(self):

    #     while self.servo_flag ==0 and self.initial_servo_us>self.min_us:     #condition fails when reaching max_us or button not clicked 
            
    #                 self.initial_servo_us-=3
    #                 # ROV.set_servo_pwm(self.initial_servo_us)
    #                 msg="se"+str(self.initial_servo_us)
    #                 clientO.sender(msg)
    #                 print ("servo down")
    #     # thread_servo_down.join()
    #     print("servo stable")



    #prepare the message to be sent to the server
    def convert_to_string(self,command,array):

        msg=command
        for i in range (9):
            msg+=str(array[i])

        return msg

    #calculating current speed (guage) GUI   
    def average_value(self,array):

        active_channels=0
        average=0
        for i in array:
            if (i!=1500):
                active_channels+=1
        if active_channels==1:
            for i in array:
                if (i!=1500):
                    return abs(i-1500)
        elif active_channels==2:
            for i in array:
                if (i!=1500):
                    average+=abs(i-1500)**2
            return math.sqrt (average)
        else:
            for  i in array:
                average+=abs(i-1500)**3
            return average**(float(1)/3)



    def pitch ( self,channel_values,PWM=1500 ):
        channel_values[0]=PWM
        msg=self.convert_to_string("rc",channel_values)
        clientO.sender(msg)
        q.put("pitch")
        return channel_values

    def roll ( self,channel_values,PWM=1500 ):

        channel_values[1]=PWM
        q.put("roll")
        msg=self.convert_to_string("rc",channel_values)
        clientO.sender(msg)
        return channel_values
    
    def throttle ( self,channel_values,PWM=1500 ):
        if(PWM>1500):
            q.put("up")
        else:

            q.put("down")
        channel_values[2]=PWM
        msg=self.convert_to_string("rc",channel_values)
        self.flt_array=[self.rc_channel_values[2],self.rc_channel_values[4],self.rc_channel_values[5]]
        self.guage_value=self.average_value(self.flt_array)
       # mw.agw.update_value(self.guage_value)
        clientO.sender(msg)
        return channel_values

    def yaw ( self,channel_values,PWM=1500 ):
        q.put("yaw")
        channel_values[3]=PWM
        msg=self.convert_to_string("rc",channel_values)
        clientO.sender(msg)
        return channel_values

    def forward ( self,channel_values,PWM=1500 ):
        
        channel_values[4]=PWM
        self.flt_array=[self.rc_channel_values[2],self.rc_channel_values[4],self.rc_channel_values[5]]
        self.guage_value=self.average_value(self.flt_array)
        #mw.agw.update_value(self.guage_value)
        msg=self.convert_to_string("rc",channel_values)
        clientO.sender(msg)
        return channel_values

    def lateral ( self,channel_values,PWM=1500 ):
        
        channel_values[5]=PWM
        self.flt_array=[self.rc_channel_values[2],self.rc_channel_values[4],self.rc_channel_values[5]]
        self.guage_value=self.average_value(self.flt_array)
        #mw.agw.update_value(self.guage_value)
        msg=self.convert_to_string("rc",channel_values)
        # print(channel_values)
        clientO.sender(msg)

        return channel_values

    def init_thrusters(self):
        
        msg="in"
        msg=msg.ljust(38)
        clientO.sender(msg)

    # def set_servo_default(self):

    #     msg="se1500"
    #     msg=msg.ljust(38)
    #     clientO.sender(msg)

    def arm(self):
        msg="ar"
        msg=msg.ljust(38)
        clientO.sender(msg)

    def disarm(self):
        msg="dr"
        msg=msg.ljust(38)
        clientO.sender(msg)

    def led_on(self):
        
        msg="ln"
        msg=msg.ljust(38)
        clientO.sender(msg)
  
    def led_off(self):

        msg="lf"
        msg=msg.ljust(38)
        clientO.sender(msg)

    def open_gripper1(self):
        msg="og"
        msg=msg.ljust(38)
        clientO.sender(msg)
    
    def open_gripper2(self):
        msg="o2"
        msg=msg.ljust(38)
        clientO.sender(msg)

    def close_gripper1(self):
        msg="cg"
        msg=msg.ljust(38)
        clientO.sender(msg)

    def close_gripper2(self):
        msg="c2"
        msg=msg.ljust(38)
        clientO.sender(msg)

    def alt_hold(self):
        msg="ah"
        msg=msg.ljust(38)
        clientO.sender(msg)
    
    def stabilize(self):
        msg="st"
        msg=msg.ljust(38)
        clientO.sender(msg)
    
    def manual(self):
        msg="mn"
        msg=msg.ljust(38)
        clientO.sender(msg)


#GUI


#CLIENT
HOST = '192.168.33.1'     #socket.gethostname() #'192.168.0.163' 
PORT = 4072
clientO = Client(HOST,PORT)

#JOYSTICK
pygame.init()
j=pygame.joystick.Joystick(0)
j.init()
joy_stick_thread=joystick()


