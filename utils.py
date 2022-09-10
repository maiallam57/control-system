import cv2
import numpy as np
# [pitch,roll,throttle,yaw,forward,lateral,none,none] 
def movement(state,move_state):
    if move_state:
        if state == 1:
            #[pitch,roll,throttle,yaw,forward,lateral,none,none]
            print("rc150015001500150015001650150015001500")
            # rc150015001500150015001750150015001500
            # print("right")
        elif state == 2:
            print("rc150015001200150015001500150015001500")
            # print("down")
        elif state == 3:
            print("rc150015001500150015001350150015001500")
            # print("left")
        elif state == 4:
            print("rc150015001200150015001500150015001500")
            # print("down")
        elif state == 5:
            print("rc150015001500150015001650150015001500")
            # print("right")

def getbasePoints(img, minpercentage=0.1):
    histyValues = np.sum(img, axis=0)
    histxValues = np.sum(img, axis=1)
    maxyValue = np.max(histyValues)
    maxxValue = np.max(histxValues)
    minyValue = minpercentage*maxyValue
    minxValue = minpercentage*maxxValue
    indexyArray = np.where(histyValues>=minyValue)
    indexxArray = np.where(histxValues>=minxValue)
    baseyPoint = int(np.average(indexyArray))
    basexPoint = int(np.average(indexxArray))
    return basexPoint, baseyPoint


def centralizeY(baseyPoint, state,move_state):
    if move_state:
        if state == 1 or state == 3 or state == 5:
            if baseyPoint > 280:
                print("rc150015001200150015001500150015001500")
                # print("down")
            elif baseyPoint < 260:
                print("rc150015001700150015001500150015001500")
                # print("up")
            else:
                movement(state)

        else: pass

def centralizeX(basexPoint, state,move_state):
    if move_state:
        if state == 2 or state == 4:
            if basexPoint > 490:
                print("rc150015001500150015001650150015001500")
                # print("right")
            elif basexPoint < 470:
                print("rc150015001500150015001350150015001500")
                # print("left")
            else:
                movement(state)
    else: pass

