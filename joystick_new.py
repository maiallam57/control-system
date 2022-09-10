from distutils.command.config import config
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
import time
import cfg
import queue
import config
import subprocess
q=queue.Queue()
j = None
error=0.2


class joystick():

    def __init__(self): 
        pygame.init()
        self.j=pygame.joystick.Joystick(0)
        self.j.init()
        cfg.joy=self
        # super().__init__()
        self.rc_channel_values=[1500 for _ in range(9)]   #initial thrusters PWMS 
        self.initial_servo_us=1500                        #initial servo us
       
        #joystick axes
        self.forward_backwards_axis=1
        self.right_left_axis=0
        self.up_down_axis=3
      
        #joystick hats
        self.auto_dock=(0,1)
        self.S=(0,-1)
        self.roll_right=(1,0)
        self.roll_left=(-1,0)
       
        #joystick buttons
        self.btn_gripper1=4
        self.btn_gripper2=5
        self.btn_led=6
        self.btn_oak=9
        self.btn_servo_up=3
        self.btn_servo_down=0
        self.btn_speed_up=8
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
        self.max_slow_speed=1700
        self.max_turn_slow_speed=1600
        self.min_slow_speed=1200
        self.max_PWM=1750
        self.max_turn_PWM=1650             #maximum :safety of thrusters
        self.min_PWM=1150
        self.max_us=1900              #max angle of servo
        self.min_us=1100
        self.pwm_pitch_yaw=250         ###1500 +or- 150  ???
       
        #mapping
        self.b=1500                            #(min pwm +max pwm)/2
        self.a1=self.max_PWM-1500              #mapping high speed
        self.a2=self.max_slow_speed-1500
        self.a1_turn=self.max_turn_PWM-1500
        self.a2_turn=self.max_turn_slow_speed-1500       #mapping low speed
        
        #GUI_guage
        self.guage_value=0
        self.flt_array=[1500,1500,1500] #forward lateral and throttle pwms
        
        # events_thread=threading.Thread(target=self.events)
        # events_thread.start()
        self.events()


    def events(self):
        
        # pygame.event.pump()
        
        x0 = -self.j.get_axis(0)
        x1 = -self.j.get_axis(1)
        x2 = -self.j.get_axis(2)
        x3 = self.j.get_axis(3)
        x4 = self.j.get_axis(4)
        x5 = self.j.get_axis(5)
        self.manual()
        # process = subprocess.Popen("python oakClient.py", stdout=subprocess.PIPE)
        while True:
            
            time.sleep(0.1)
            pygame.event.pump()
        
            
            x0 = -self.j.get_axis(0)
            x1 = -self.j.get_axis(1)
            x2 = -self.j.get_axis(2)
            x3 = self.j.get_axis(3)
            x4 = self.j.get_axis(4)
            x5 = self.j.get_axis(5)
            zaxis_counter=0
        # # if x0 >-error or x0 < error:
        #     if x0 != self.j.get_axis(0):
        #         x0=self.j.get_axis(0)
        #         print("axis_0: "+  str(x0))

        # # if x1 > -error or x1 <error:
        #     if x1 != self.j.get_axis(1):
        #         x1=self.j.get_axis(1)
        #         print("axis_1: "+  str(x1))

        # # if x2 >-error or x2 <error:
        #     if x2 != self.j.get_axis(2):
        #         x2=self.j.get_axis(2)
        #         print("axis_2: "+  str(x2))

        # # if x3 > -error or x3 <error:
        #     if x3 != self.j.get_axis(3):
        #         x3=self.j.get_axis(3)
        #         print("axis_3: "+  str(x3))

            #axes (forward,lateral,throttle)
            # if hasattr(event,'axis'):
            if ((x1 >-error and x1 <= 0) or (x1 < error and x1 >= 0)):         #error interval
                # print("bara")
                if(self.rc_channel_values[4]!=1500):
                    self.rc_channel_values=self.forward(self.rc_channel_values,1500)


                    
                                                
            else:
                
                

                self.event_forward_value=x1 

                if self.flag_speed_up%2==1: ##high speed
                    self.a=self.a1                                  
                else:                       ##low speed
                    self.a=self.a2
                #mapping pwm                            
                self.PWM=self.a*self.event_forward_value+self.b
                
                self.PWM=int(self.PWM)
                self.rc_channel_values=self.forward(self.rc_channel_values,self.PWM)
                print("forward:"+str(int(self.PWM)))
                        

            if ((x0 >-error and x0 <= 0) or (x0 < error and x0 >=0)) :        #error interval
                if(self.rc_channel_values[5]!=1500):  
                    self.rc_channel_values=self.lateral(self.rc_channel_values,1500)
                
                
                

            else:
                
                self.event_lateral_value=x0
                
                if self.flag_speed_up%2==1:   #high speed                                
                    self.a=self.a1                                
                else:                         #low speed
                    self.a=self.a2
                #mapping pwm                        
                self.PWM=-self.a*self.event_lateral_value+self.b
                self.PWM=int(self.PWM)
                self.rc_channel_values=self.lateral(self.rc_channel_values,self.PWM)
                # print("lateral:"+str(int(self.PWM)))
                        
                        

            # print(x2)
            if ((x2 >-error and x2 <= 0) or (x2 < error and x2 >= 0)) :      #error interval   
                if(self.rc_channel_values[3]!=1500):  
                    self.rc_channel_values=self.yaw(self.rc_channel_values,1500)

            else:
                
                self.event_yaw=x2
                
                if self.flag_speed_up%2==1:             #high speed
                    self.a=self.a1_turn
                else:                                   #low speed
                    self.a=self.a2_turn
                # print("eq:"+str(-self.a*self.event_yaw))
                self.PWM=-self.a*self.event_yaw+self.b
                self.PWM=int(self.PWM)
                # print(self.PWM)
                self.rc_channel_values=self.yaw(self.rc_channel_values,self.PWM)
            
            if x5 > 0 :      #error interval   
                if(self.rc_channel_values[2]!=1750):  
                    self.rc_channel_values=self.throttle(self.rc_channel_values,1750)
            
            elif x4 > 0 :      #error interval  
                if(self.rc_channel_values[2]!=1250):  
                    self.rc_channel_values=self.throttle(self.rc_channel_values,1250)
               
            else: 
                if(self.rc_channel_values[2]!=1500):  
                    self.rc_channel_values=self.throttle(self.rc_channel_values,1500)
                
                # print("throttle:"+str(int(self.PWM)))
                #print(self.rc_channel_values,self.guage_value)
                #print("throttle",self.PWM)

                            
                #buttons(servo up,servo down,speeding up,arming & disarming,leds on & off)
                

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
            btnspeedup=self.j.get_button(self.btn_speed_up)
            # btnspeedup=50

            btn_arm_disarm=self.j.get_button(self.btn_arm_disarm)
            btn_led=self.j.get_button(self.btn_led)
            btn_gripper1=self.j.get_button(self.btn_gripper1)
            btn_gripper2=self.j.get_button(self.btn_gripper2)
            btn_alt_hold=self.j.get_button(self.btn_alt_hold)
            btn_manual=self.j.get_button(self.btn_manual)
            btn_stabilize=self.j.get_button(self.btn_stabilize)
            btn_oak=self.j.get_button(self.btn_oak)
            print ("btnspeedup")
            print(btnspeedup)
            if btnspeedup==1:
                # time.sleep(0.1)
                
                awelmara=1
                print("speedup")
               # while(self.j.get_button(self.btn_speed_up)==1):
               #     pygame.event.pump()
                self.flag_speed_up=1
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
            else:
                self.flag_speed_up=0


            if btn_arm_disarm==1:
                
                print("arm")
                while(self.j.get_button(self.btn_arm_disarm)==1):
                    pygame.event.pump()
                self.flag_arm+=1
                if self.flag_arm%2==1:
                    self.arm()
                    
                elif self.flag_arm%2==0:
                    self.disarm()
            # if btn_oak==1:
                
            #     print("oak")
            #     while(self.j.get_button(self.btn_oak)==1):
            #         pygame.event.pump()
            #     # self.flag_arm+=1
            #     # if self.flag_arm%2==1:
            #     #     self.arm()
                    
            #     # elif self.flag_arm%2==0:
            #     #     self.disarm()       
            #     start=time.time()

            #     while self.j.get_button(self.btn_oak)==0 and (time.time()-start)<=6 and x1>-error and x1<error:
            #         inloop=True
            #         print("in code")
            #         pygame.event.pump()
            #         x1 = self.j.get_axis(1)
            #         if(self.rc_channel_values[4]!=1650):
            #             self.rc_channel_values=self.forward(self.rc_channel_values,1350)
                   
                    
            #         # output = process.stdout.readline()
            #         # if output == '' and process.poll() is not None:
            #         #     pass
            #         # if output:
            #         #     clientO.sender(output.strip().decode())
            #     if inloop==True:
            #         self.rc_channel_values=self.forward(self.rc_channel_values,1500)
            #         inloop=False
                    
            #     print("out of code")

            if btn_led==1:
                # time.sleep(0.1)
                while(btn_led==1):
                    pygame.event.pump()
                    btn_led=self.j.get_button(self.btn_led)

                print("led")
                self.flag_led+=1
                if self.flag_led%2==1:
                    self.led_on()
                    # mw.leds_on()
                    # self.flag_led=1
                elif self.flag_led%2==0:
                    self.led_off()
                    #mw.leds_off()
                    # self.flag_led=0
            
            if btn_gripper1==1:
                # time.sleep(0.1)
                print("grip1")
                while(self.j.get_button(self.btn_gripper1)==1):
                    pygame.event.pump()
                    
                self.flag_gripper1+=1
                if self.flag_gripper1%2==1:
                    self.open_gripper1()
                    #mw.open_gripper()
                    # self.flag_gripper1=1
                elif self.flag_gripper1 %2==0: 
                    self.close_gripper1()
                    #mw.close_gripper()
                    # self.flag_gripper1=0
            
            if btn_gripper2==1:
                # time.sleep(0.1)
                print("grip2")
                while(self.j.get_button(self.btn_gripper2)==1):
                    pygame.event.pump()
                self.flag_gripper2+=1
                if self.flag_gripper2%2==1:
                    self.open_gripper2()
                    #mw.open_gripper()
                    # self.flag_gripper2=1
                elif self.flag_gripper2%2==0:
                    self.close_gripper2()
                    #mw.close_gripper()
                    # self.flag_gripper2=0

                    
            if btn_alt_hold==1:
                # time.sleep(0.1)
                print("altitude_hold")
                while(self.j.get_button(self.btn_alt_hold)==1):
                    pygame.event.pump()
                self.alt_hold()
                
            
            if btn_manual==1:
                # time.sleep(0.1)
                print("manual")
                while(self.j.get_button(self.btn_manual)==1):
                    pygame.event.pump()
                self.manual()

            if btn_stabilize==1:
                # time.sleep(0.1)
                print("stabilize")
                while(self.j.get_button(self.btn_stabilize)==1):
                    pygame.event.pump()
                self.stabilize()


            hat=self.j.get_hat(0)
    
            if hat == self.auto_dock:
                
                print("auto_dock")
                while self.j.get_hat(0)==self.auto_dock:
                    pygame.event.pump()
                # self.flag_arm+=1
                # if self.flag_arm%2==1:
                #     self.arm()
                    
                # elif self.flag_arm%2==0:
                #     self.disarm()       
                start=time.time()

                while self.j.get_hat(0)!=self.auto_dock and (time.time()-start)<=6 and x1>-error and x1<error:
                    inloop=True
                    print("in code")
                    pygame.event.pump()
                    x1 = self.j.get_axis(1)
                    if(self.rc_channel_values[3]!=1500):
                        self.rc_channel_values=self.yaw(self.rc_channel_values,1500)
                    if(self.rc_channel_values[5]!=1500):
                        self.rc_channel_values=self.lateral(self.rc_channel_values,1500)
                    if(self.rc_channel_values[2]!=1500):
                        self.rc_channel_values=self.throttle(self.rc_channel_values,1500)
                    if(self.rc_channel_values[4]!=1650):
                         self.rc_channel_values=self.forward(self.rc_channel_values,1650)
                   
                    
                    # output = process.stdout.readline()
                    # if output == '' and process.poll() is not None:
                    #     pass
                    # if output:
                    #     clientO.sender(output.strip().decode())
                if inloop==True:
                    self.rc_channel_values=self.forward(self.rc_channel_values,1500)
                    inloop=False
                    
                print("out of code")
            

            if hat == self.S:
                
                print("auto_S")
                while self.j.get_hat(0)==self.S:
                    pygame.event.pump()
                # self.flag_arm+=1
                # if self.flag_arm%2==1:
                #     self.arm()
                    
                # elif self.flag_arm%2==0:
                #     self.disarm()       
                start=time.time()

                while self.j.get_hat(0)!=self.S and (time.time()-start)<=8 and x1>-error and x1<error:
                    inloop=True
                    print("in right code")
                    pygame.event.pump()
                    x1 = self.j.get_axis(1)
                    if(self.rc_channel_values[3]!=1500):
                        self.rc_channel_values=self.yaw(self.rc_channel_values,1500)
                    if(self.rc_channel_values[5]!=1600):
                        self.rc_channel_values=self.lateral(self.rc_channel_values,1600)
                    if(self.rc_channel_values[2]!=1500):
                        self.rc_channel_values=self.throttle(self.rc_channel_values,1500)
                    if(self.rc_channel_values[4]!=1500):
                         self.rc_channel_values=self.forward(self.rc_channel_values,1500)
                start=time.time()
                while self.j.get_hat(0)!=self.S and (time.time()-start)<=1 and x1>-error and x1<error:
                    inloop=True
                    print("in pause code")
                    pygame.event.pump()
                    x1 = self.j.get_axis(1)
                    if(self.rc_channel_values[5]!=1500):
                        self.rc_channel_values=self.lateral(self.rc_channel_values,1500)
                    
                start=time.time()
                while self.j.get_hat(0)!=self.S and (time.time()-start)<=4 and x1>-error and x1<error:
                    inloop=True
                    print("in down1 code")
                    pygame.event.pump()
                    x1 = self.j.get_axis(1)
                    if(self.rc_channel_values[3]!=1500):
                        self.rc_channel_values=self.yaw(self.rc_channel_values,1500)
                    if(self.rc_channel_values[5]!=1500):
                        self.rc_channel_values=self.lateral(self.rc_channel_values,1500)
                    if(self.rc_channel_values[2]!=1250):
                        self.rc_channel_values=self.throttle(self.rc_channel_values,1250)
                    if(self.rc_channel_values[4]!=1500):
                         self.rc_channel_values=self.forward(self.rc_channel_values,1500)
                start=time.time()
                while self.j.get_hat(0)!=self.S and (time.time()-start)<=8 and x1>-error and x1<error:
                    inloop=True
                    print("in left code")
                    pygame.event.pump()
                    x1 = self.j.get_axis(1)
                    if(self.rc_channel_values[3]!=1500):
                        self.rc_channel_values=self.yaw(self.rc_channel_values,1500)
                    if(self.rc_channel_values[5]!=1400):
                        self.rc_channel_values=self.lateral(self.rc_channel_values,1400)
                    if(self.rc_channel_values[2]!=1500):
                        self.rc_channel_values=self.throttle(self.rc_channel_values,1500)
                    if(self.rc_channel_values[4]!=1500):
                         self.rc_channel_values=self.forward(self.rc_channel_values,1500)
                start=time.time()
                while self.j.get_hat(0)!=self.S and (time.time()-start)<=1 and x1>-error and x1<error:
                    inloop=True
                    print("in pause code")
                    pygame.event.pump()
                    x1 = self.j.get_axis(1)
                    if(self.rc_channel_values[5]!=1500):
                        self.rc_channel_values=self.lateral(self.rc_channel_values,1500)
                start=time.time()
                while self.j.get_hat(0)!=self.S and (time.time()-start)<=4 and x1>-error and x1<error:
                    inloop=True
                    print("in down2 code")
                    pygame.event.pump()
                    x1 = self.j.get_axis(1)
                    if(self.rc_channel_values[3]!=1500):
                        self.rc_channel_values=self.yaw(self.rc_channel_values,1500)
                    if(self.rc_channel_values[5]!=1500):
                        self.rc_channel_values=self.lateral(self.rc_channel_values,1500)
                    if(self.rc_channel_values[2]!=1250):
                        self.rc_channel_values=self.throttle(self.rc_channel_values,1250)
                    if(self.rc_channel_values[4]!=1500):
                         self.rc_channel_values=self.forward(self.rc_channel_values,1500)
                start=time.time()
                while self.j.get_hat(0)!=self.S and (time.time()-start)<=8 and x1>-error and x1<error:
                    inloop=True
                    print("in right2 code")
                    pygame.event.pump()
                    x1 = self.j.get_axis(1)
                    if(self.rc_channel_values[3]!=1500):
                        self.rc_channel_values=self.yaw(self.rc_channel_values,1500)
                    if(self.rc_channel_values[5]!=1600):
                        self.rc_channel_values=self.lateral(self.rc_channel_values,1600)
                    if(self.rc_channel_values[2]!=1500):
                        self.rc_channel_values=self.throttle(self.rc_channel_values,1500)
                    if(self.rc_channel_values[4]!=1500):
                         self.rc_channel_values=self.forward(self.rc_channel_values,1500)
                start=time.time()
                while self.j.get_hat(0)!=self.S and (time.time()-start)<=1 and x1>-error and x1<error:
                    inloop=True
                    print("in pause code")
                    pygame.event.pump()
                    x1 = self.j.get_axis(1)
                    if(self.rc_channel_values[5]!=1500):
                        self.rc_channel_values=self.lateral(self.rc_channel_values,1500)
                   
                    
                    # output = process.stdout.readline()
                    # if output == '' and process.poll() is not None:
                    #     pass
                    # if output:
                    #     clientO.sender(output.strip().decode())
                if inloop==True:
                    self.rc_channel_values=self.lateral(self.rc_channel_values,1500)
                    inloop=False
                    
                print("out of S code")
            if hat == self.roll_left:
                if(self.rc_channel_values[1]!=1250):  
                    self.rc_channel_values=self.roll(self.rc_channel_values,1250)
               
                

            if hat == self.roll_right:
                 if(self.rc_channel_values[1]!=1750):  
                    self.rc_channel_values=self.roll(self.rc_channel_values,1750)


                
                
            # if hat == self.pitch_down:
                        
            #     self.flag_pitch=1
            #     self.rc_channel_values=self.pitch(self.rc_channel_values,1500-self.pwm_pitch_yaw)
                
            # if hat == self.yaw_right:

            #     # self.PWM=-self.a*self.event_forward_value+self.b
            #     # self.PWM=int(self.PWM)
            #     # self.rc_channel_values=self.yaw(self.rc_channel_values,self.PWM)
                    
            #     self.rc_channel_values=self.yaw(self.rc_channel_values,1500-self.pwm_pitch_yaw)
            #     #mw.cw_arrow_on()
                
            # if hat == self.yaw_left:

                
                
            #     self.rc_channel_values=self.yaw(self.rc_channel_values,1500+self.pwm_pitch_yaw)
            #     #mw.ccw_arrow_on()
                
            if hat == (0,0):
                
                
                if(self.rc_channel_values[1]!=1500):
                    self.rc_channel_values=self.roll(self.rc_channel_values,1500)
                    
             
                    

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

    def check_flags(self,channel_values):

        #print(channel_values)

    
        if (channel_values[4]>1500):
            
            self.flag_backward_arrow=1
        elif (channel_values[4]<1500):
            #mw.backward_arrow_on()
            self.flag_forward_arrow=1
        else:
            self.flag_forward_arrow=0
            self.flag_backward_arrow=0

        if (channel_values[5]<1500):
            
            self.flag_right_arrow=1
        elif (channel_values[5]>1500):
            #mw.backward_arrow_on()
            self.flag_left_arrow=1
        else:
            self.flag_left_arrow=0
            self.flag_right_arrow=0

        if (channel_values[2]>1500):
            self.flag_up_arrow=1

        elif (channel_values[2]<1500):
            
            self.flag_down_arrow=1
        else:
            self.flag_up_arrow=0
            self.flag_down_arrow=0

        if (channel_values[3]>1500):
            self.flag_yaw_left=1
            self.flag_yaw_right=0
            
        elif (channel_values[3]<1500):
            self.flag_yaw_right=1
            self.flag_yaw_left=0
        else:
            self.flag_yaw_right=0
            self.flag_yaw_left=0
        

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

        
        channel_values[2]=PWM
        self.check_flags(channel_values)
        msg=self.convert_to_string("rc",channel_values)
        # self.flt_array=[self.rc_channel_values[2],self.rc_channel_values[4],self.rc_channel_values[5]]
        # self.guage_value=self.average_value(self.flt_array)
        # config.guage_value(self.guage_value)
       # mw.agw.update_value(self.guage_value)
        clientO.sender(msg)
        print(msg)
        return channel_values

    def yaw ( self,channel_values,PWM=1500 ):
        
        channel_values[3]=PWM
        self.check_flags(channel_values)
        msg=self.convert_to_string("rc",channel_values)
        clientO.sender(msg)
        return channel_values

    def forward ( self,channel_values,PWM=1500 ):
        
        channel_values[4]=PWM
        self.check_flags(channel_values)
        self.flt_array=[self.rc_channel_values[2],self.rc_channel_values[4],self.rc_channel_values[5]]
        # self.guage_value=self.average_value(self.flt_array)
        # config.guage_value(self.guage_value)
        #mw.agw.update_value(self.guage_value)
        msg=self.convert_to_string("rc",channel_values)
        clientO.sender(msg)
        
        return channel_values

    def lateral ( self,channel_values,PWM=1500 ):
        
        channel_values[5]=PWM
        self.check_flags(channel_values)
        # self.flt_array=[self.rc_channel_values[2],self.rc_channel_values[4],self.rc_channel_values[5]]
        # self.guage_value=self.average_value(self.flt_array)
        # config.guage_value(self.guage_value)
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
JOYPORT = 4072
SensorPort = 4073
clientO = Client(HOST,JOYPORT)
# client1 =Client(HOST,SensorPort)
# sensorThread=threading.Thread(target=client1.receiver)
# sensorThread.start()
#JOYSTICK




