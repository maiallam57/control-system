# import required libraries
from vidgear.gears import NetGear
import cv2
import numpy as np

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

result = cv2.VideoWriter('color.avi', 
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         30, (640, 480))

resultDepth = cv2.VideoWriter('depth.avi', 
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         30, (1280, 480))
switch = "s"
msg = "S"
frame = None
disparity = None
depth = None
right = None

while True:

    # receive data from network
    msg, data = client.recv(return_data=switch)
    if data is None:
        cv2.destroyAllWindows()
        
    if switch == "s" and msg == "S":
        frame = data
        result.write(frame)
        cv2.imshow("frame", frame)

    if switch == "d" and msg == "D":

        right, disparity, depth = cv2.split(data)
        resultDepth.write(np.hstack([depth, right]))
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



    key = cv2.waitKey(1)

    if key == ord("S") or key == ord("s"):
        switch = "s"
        cv2.destroyAllWindows()
    if key == ord("D") or key == ord("d"):
        switch = "d"
        cv2.destroyAllWindows()

    if key == ord("F") or key == ord("f"):
        switch = "f"
        cv2.destroyAllWindows()
    
    if key == ord("Q") or key == ord("q"):
        break
    if key == ord("x") or key ==('X'):
        result.release()
        resultDepth.release()
# close output window
cv2.destroyAllWindows()


# safely close client
client.close()