# import required libraries
from vidgear.gears import NetGear
import cv2
import numpy as np
import sys
from opencv_color_line_detection import *
# activate multiserver_mode

options = {"bidirectional_mode": True, "max_retries": 10000}

# Define NetGear Client at given IP address and assign list/tuple 
# of all unique Server((5566,5567) in our case) and other parameters
# !!! change following IP address '192.168.x.xxx' with yours !!!
client = NetGear(
    address="192.168.33.100",
    port=5454,
    protocol="tcp",
    pattern=1,
    receive_mode=True,
    **options
)


switch = "s"
msg = "S"
frame = None
disparity = None
depth = None
right = None
# init_trackbars()
detect=False
count = 0
def readFrame():

    # try:
        key = cv2.waitKey(1)
        global switch
        global msg
        global frame
        global disparity
        global depth
        global right
        global detect
        global count
        # receive data from network
        
        msg, data = client.recv(return_data=switch)
        if data is None:
            cv2.destroyAllWindows()
            
        if switch == "s" and msg == "S":
            frame = data.copy()
            data = cv2.rotate(data, cv2.ROTATE_180)
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            # sys.stdout.flush()
            # if detect:
            #     ret,state,frameprocessed = detection(frame ,state,False)
            #     frame=frameprocessed
            #     # if ret==0:
            #     #     detect=False
            #     #     cv2.destroyAllWindows()
            #     #     cv2.imshow("frame", frame)
            frame = cv2.resize(frame, (1280, 720))
            return frame
            # cv2.imshow("Pilotframe", frame)


        if switch == "d" and msg == "D":
            right, disparity, depth = cv2.split(data)
            right = np.uint8(right)
            disparity = np.uint8(disparity)
            cv2.imshow("disparity", disparity)
            cv2.imshow("right", right)

        if switch == "f" and msg == "F":
            frame = np.uint8(data[:, :640])
            right, disparity, depth = cv2.split(data[:, 640:])
            right = np.uint8(right)
            disparity = np.uint8(disparity)
            cv2.imshow("frame", frame)
            cv2.imshow("disparity", disparity)
            cv2.imshow("right", right)


       
        if key == ord("S") or key == ord("s"):
            switch = "s"
            cv2.destroyAllWindows()
        if key == ord("D") or key == ord("d"):
            switch = "d"
            cv2.destroyAllWindows()

        if key == ord("F") or key == ord("f"):
            switch = "f"
            cv2.destroyAllWindows()
        
        # if key == ord("Q") or key == ord("q"):
            # break
        # if key == ord("R") or key == ord("r"):
        #     detect=True
        # if key == ord("P") or key == ord("p"):
        #     detect=False
        # if key == ord("X") or key == ord("x"):
        #     cv2.imwrite("CAPTURE.jpg", data)
        #     cv2.imshow("CAPTURE", data)

        # if key == ord("X") or key == ord("x"):
        #     cv2.imwrite("C:\Users\user\Desktop\MATE GIVEN\exe files\CAPTURE{}.JPG".format(count), data)
        #     count += 1
    # except KeyboardInterrupt:
    #     break

# close output window
# cv2.destroyAllWindows()

# # safely close client
# client.close()