from time import time

from joystick import joy_stick_thread
fr=4
lt=5
th=2
yw=3
rc_channels=[1500 for _ in range(9)]
docking=False
def check_flags():
    while not docking:
        if (rc_channels[fr]>1500):
            joy_stick_thread.flag_forward_arrow=1
        elif (rc_channels[fr]>1500):
            #mw.backward_arrow_on()
            joy_stick_thread.flag_backward_arrow=1
        else:
            joy_stick_thread.flag_forward_arrow=0
            joy_stick_thread.flag_backward_arrow=0

        if (rc_channels[lt]>1500):
            joy_stick_thread.flag_left_arrow=1

        elif (rc_channels[lt]>1500):
            #mw.backward_arrow_on()
            joy_stick_thread.flag_right_arrow=1
        else:
            joy_stick_thread.flag_left_arrow=0
            joy_stick_thread.flag_right_arrow=0

        if (rc_channels[th]>1500):
            joy_stick_thread.flag_up_arrow=1

        elif (rc_channels[th]>1500):
            
            joy_stick_thread.flag_down_arrow=1
        else:
            joy_stick_thread.flag_up_arrow=0
            joy_stick_thread.flag_down_arrow=0

        if (rc_channels[yw]>1500):
            joy_stick_thread.flag_yaw_left=1

        elif (rc_channels[yw]>1500):
            
            joy_stick_thread.flag_yaw_right=1
        else:
            joy_stick_thread.flag_yaw_right=0
            joy_stick_thread.flag_yaw_left=0
        
# def docking ():
joy_stick_thread.flag_forward_arrow=1
rc_channels=joy_stick_thread.forward(rc_channels,1700)
time.sleep(3)
rc_channels=joy_stick_thread.forward(rc_channels,1500)

