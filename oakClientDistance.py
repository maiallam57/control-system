# import required libraries
from vidgear.gears import NetGear
#import getXYZ
import cv2
import numpy as np
import time
import os


def ROI(event, x, y, flags, params):
    global MOVE
    global CURRENT_AREA_OF_CHANGE
    if event == cv2.EVENT_LBUTTONDOWN and MOVE == False:
        MOVE = True
        CURRENT_AREA_OF_CHANGE = [[max(0, min(639, x)), max(0, min(399, y))], [max(0, min(639, x)), max(0, min(399, y))]]
    if MOVE:
        if event == cv2.EVENT_MOUSEMOVE:
            CURRENT_AREA_OF_CHANGE[1] = [max(0, min(639, x)), max(0, min(399, y))]
    if event == cv2.EVENT_LBUTTONUP and MOVE:
        MOVE = False
        AREA_OF_CHANGE.append([CURRENT_AREA_OF_CHANGE])

def processDrawnArea(area, depthFrame):
    # get midpoint
    midX = (area[0][0][0]+area[0][1][0])//2
    midY = (area[0][0][1]+area[0][1][1])//2
    # diagonal points
    x1, y1 = area[0][0][0], area[0][0][1]
    x2, y2 = area[0][1][0], area[0][1][1]
    xmin, ymin = min(x1, x2), min(y1, y2)
    xmax, ymax = max(x1, x2), max(y1, y2)
    # getXYZ of a given ROI
    spatials, centroid = calcSpatial.calc_spatials(depthFrame, [xmin, ymin, xmax, ymax]) 
    return area, midX, midY, spatials

def processSpatialCoordiantes(S1, S2, yCoefficient = 1):
    x1, y1, z1 = S1['x']/1000, S1['y']/1000, S1['z']/1000
    x2, y2, z2 = S2['x']/1000, S2['y']/1000, S2['z']/1000
    distance = np.sqrt((x1-x2)**2 + yCoefficient*(y1-y2)**2 + (z1-z2)**2)
    return distance

# activate multiserver_mode
options = {"bidirectional_mode": True, "max_retries": 10000}

# Define NetGear Client at given IP address and assign list/tuple 
client = NetGear(
    address="192.168.33.100",
    port=5454,
    protocol="tcp",
    pattern=1,
    receive_mode=True,
    **options
)

# initial value for bidirectional network
switch = "s"
msg = "S"
# initial value for images recieved from network
frame, disparity, depth, right = None, None, None, None
# a list to save frames to be used for distance measurement
capturedFrames = list(np.load("capturedFrames.npy", allow_pickle=True)) if os.path.isfile("capturedFrames.npy") else []
capturedFramesIndex = 0
windowFlag = True if len(capturedFrames) else False
# intial value for timer used to capture frames every second
elapsedTime = 0
calcSpatial = getXYZ.HostSpatialsCalc()
############################
MOVE = False
AREA_OF_CHANGE = []
CURRENT_AREA_OF_CHANGE = []

while True:
    
    # receive data from network
    msg, data = client.recv(return_data=switch)
    # used to capture keyboard inputs
    key = cv2.waitKey(1)

    if data is None:
        cv2.destroyAllWindows()
        
    if switch == "s" and msg == "S":
        frame = data
        cv2.imshow("rgb", frame)

        if len(capturedFrames):
            if windowFlag:
                cv2.namedWindow("disparity-right")
                cv2.setMouseCallback("disparity-right", ROI)
                windowFlag = False

            currentCapturedFrames = capturedFrames[capturedFramesIndex]
            depthFrame = currentCapturedFrames["depth"]
            calculationsFrame = np.hstack([currentCapturedFrames["disparity"], currentCapturedFrames["right"]])
            calculationsFrame = cv2.cvtColor(calculationsFrame, cv2.COLOR_GRAY2BGR)

            if MOVE:
                cv2.rectangle(calculationsFrame, tuple(CURRENT_AREA_OF_CHANGE[0]), tuple(CURRENT_AREA_OF_CHANGE[1]), (255, 255, 0), 3)

            for counter, area in enumerate(AREA_OF_CHANGE):
                cv2.rectangle(calculationsFrame, tuple(area[0][0]), tuple(area[0][1]), (255, 0, 0), 3)
                if counter % 2 == 0:
                    area1, midX1, midY1, spatials1 = processDrawnArea(area, depthFrame)
                    cv2.circle(calculationsFrame, (midX1, midY1), 3, (255, 0, 0), -1)
                else:
                    area2, midX2, midY2, spatials2 = processDrawnArea(area, depthFrame)
                    cv2.circle(calculationsFrame, (midX2, midY2), 3, (255, 0, 0), -1)
                    cv2.line(calculationsFrame, (midX1, midY1), (midX2, midY2), (0, 255, 0), 1)
                    distance = processSpatialCoordiantes(spatials1, spatials2)
                    cv2.putText(calculationsFrame, '{}'.format(round(distance*100, 2)), ((midX1+midX2)//2, (midY1+midY2)//2),
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                0.8, 
                                (0, 0, 255), 
                                1, 
                                cv2.LINE_AA) 
            if key == ord("z") or key == ord("Z"):
                if capturedFramesIndex > 0:
                    AREA_OF_CHANGE = []
                    capturedFramesIndex -= 1

            if key == ord("x") or key == ord("X"):
                if capturedFramesIndex < len(capturedFrames) -1:
                    AREA_OF_CHANGE = []
                    capturedFramesIndex += 1
                    
            cv2.imshow("disparity-right", calculationsFrame)

    if switch == "d" and msg == "D":
        right, disparity, depth = cv2.split(data)
        right = np.uint8(right)
        disparity = np.uint8(disparity)
        frame = np.hstack([disparity, right])
        cv2.imshow("disparity-right", frame)

        # save right-disparity-depth images every 1 second or by pressing C
        if key == ord("C") or key == ord("c") or time.time()-elapsedTime > 1:
            images = {"right":right, "disparity":disparity, "depth":depth}
            capturedFrames.append(images)
            np.save("capturedFrames.npy", capturedFrames)
            # reset timer
            elapsedTime = time.time()


    if switch == "f" and msg == "F":
        frame = np.uint8(data[:, :640])
        right, disparity, depth = cv2.split(data[:, 640:])
        right = np.uint8(right)
        disparity = np.uint8(disparity)
        cv2.imshow("rgb", frame)
        cv2.imshow("disparity", disparity)
        cv2.imshow("right", right)
    

    if key == ord("S") or key == ord("s"):
        if switch != "S":
            windowFlag = True if len(capturedFrames) else False
            AREA_OF_CHANGE = []
        switch = "s"
        cv2.destroyAllWindows()

    if key == ord("D") or key == ord("d"):
        switch = "d"
        elapsedTime = time.time()
        cv2.destroyAllWindows()

    if key == ord("F") or key == ord("f"):
        switch = "f"
        cv2.destroyAllWindows()
    
    if key == ord("Q") or key == ord("q"):
        break

    # if key == ord("x") or key ==('X'):
    #     cv2.imwrite("right.jpg", right)
    #     cv2.imwrite("disparity.jpg", disparity)
    #     cv2.imwrite("rgb.jpg", frame)
    #     cv2.imwrite("depth", depth)

# close output window
cv2.destroyAllWindows()

# safely close client
client.close()