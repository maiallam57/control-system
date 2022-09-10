
# import required libraries
from threading import Thread
import threading
from numpy import take_along_axis
from vidgear.gears import NetGear
#from imutils import build_montages # 

import cv2
import time
# activate multiserver_mode
options = {"multiserver_mode": True}

# Define NetGear Client at given IP address and assign list/tuple 
# of all unique Server((5566,5567) in our case) and other parameters
# !!! change following IP address '192.168.x.xxx' with yours !!!
client = NetGear(
    address="192.168.33.100",
    port=(5454,),
    protocol="tcp",
    pattern=1,
    receive_mode=True,
    **options
)



    # loop over until Keyboard Interrupted
def oak_stream():

    while True:

        try:
            # receive data from network
            data = client.recv()

            # check if data received isn't None
            if data is None:
                break

            # extract unique port address and its respective frame
            unique_address, frame = data

            # # {do something with the extracted frame here}

            # # get extracted frame's shape
            # (h, w) = frame.shape[:2]

            # # update the extracted frame in the received frame dictionary
            # frame_dict[unique_address] = frame

            # # build a montage using data dictionary
            # montages = build_montages(frame_dict.values(), (w, h), (2, 1))

            # display the montage(s) on the screen
            # for (i, montage) in enumerate(montages):
            #print(unique_address)

            if unique_address == '5454':
                frame = cv2.cv2.rotate(frame, cv2.ROTATE_180)
                frame=cv2.resize(frame,(1000,750))
                cv2.imshow("Montage Footage", frame)

            # check for 'q' key if pressed
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                close_stream()
                break

        except KeyboardInterrupt:
            break
def close_stream():
        
    # close output window
    cv2.destroyAllWindows()

    # safely close client
    client.close()
oak=threading.Thread(target=oak_stream)
oak.start()
print("in call")