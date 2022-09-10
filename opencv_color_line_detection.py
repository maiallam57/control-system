import cv2
import numpy as np
import utils
import sys
def doc():
    """state = right  >
    keep going right by staying on your same state >
    basexPoint is shifted to the right when hitting a corner
    baseyPoint is inversed >
        state = down >
    when baseyPoint hits the upper region (since it's inversed) >
    baseyPoint is back normal >
    keep going down >
    baseyPoint is shifted down when hitting a corner >
    basexPoint is inversed >
        state = left >
    when basexPoint hits the far right region (since it's inversed) >
    basexPoint is back to normal >
    keep going left >
    basexPoint is shifted  to the left when hitting a corner >
    baseyPoint is inversed >
        state = down >
    when baseyPoint hits the upper region (since it's inversed) >
    baseyPoint is back normal >
    keep going down >
    baseyPoint is shifted down when hitting a corner >
    basexPoint is inversed >
        state = right >
    when basexPoint hits the far right region (since it's inversed) >
    basexPoint returns normal >
    keep going right....=="""
    pass





def trackLine(item,frame,horx1,hory1,horx2,hory2):
    global state
    global biggest
    global indx
    contours, _ = cv2.findContours(item,1,cv2.CHAIN_APPROX_NONE)
    biggest = 0
    for cnt in contours:
        if cv2.contourArea(cnt)>biggest:
            biggest = cv2.contourArea(cnt)
            indx = cnt
    for cnt in contours:
        area = cv2.contourArea(indx)
        if area > 4000: #and area < 15000:
            x1,y1,x2,y2 = cv2.boundingRect(indx)
            x2 = x1+x2
            y2 = y1+y2
            cv2.drawContours(frame, cnt, -1, (0,0,255), 2)
            cv2.rectangle(frame,(horx1,hory1),(horx2,hory2),(0,0,255),2) #horizontal range of screen
    # area = cv2.contourArea(indx)
    # if area > 4000: #and area < 15000:
    #     x1,y1,x2,y2 = cv2.boundingRect(indx)
    #     x2 = x1+x2
    #     y2 = y1+y2
    #     cv2.drawContours(frame, cnt, -1, (0,0,255), 2)
    #     cv2.rectangle(frame,(horx1,hory1),(horx2,hory2),(0,0,255),2) #horizontal range of screen

def empty(a):
    pass

# vid = cv2.VideoCapture("S_mazen.mkv")
def init_trackbars():
    cv2.namedWindow("TrackBars") #Create new trackbar window
    cv2.resizeWindow("TrackBars", 500, 250) #resize that window
    cv2.createTrackbar("Hue Min","TrackBars", 98, 179, empty) #125
    cv2.createTrackbar("Hue Max","TrackBars", 179, 179, empty)
    cv2.createTrackbar("Sat Min","TrackBars", 40, 255, empty)
    cv2.createTrackbar("Sat Max","TrackBars", 255, 255, empty)
    cv2.createTrackbar("Val Min","TrackBars", 99, 255, empty)
    cv2.createTrackbar("Val Max","TrackBars", 255, 255, empty)
    # cv2.createTrackbar("Cannyarg1","TrackBars", 100, 200, empty)
    # cv2.createTrackbar("Cannyarg2","TrackBars", 100, 200, empty)
    # cv2.createTrackbar("maxlinegap","TrackBars", 0, 200, empty)
    # cv2.createTrackbar("areaTrack","TrackBars", 0, 20000, empty)
    # cv2.createTrackbar("horx1","TrackBars", 0, 960, empty)
    # cv2.createTrackbar("horx2","TrackBars", 0, 960, empty)
    # cv2.createTrackbar("hory1","TrackBars", 0, 540, empty)
    # cv2.createTrackbar("hory2","TrackBars", 0, 540, empty)
    # cv2.createTrackbar("otsu_low","TrackBars", 120, 255, empty)
    # cv2.createTrackbar("otsu_up","TrackBars", 255, 255, empty)
init_trackbars()

def detection(framecap,uni_state,move_state):
        global state 
        state=uni_state
        frame=framecap.copy()
        frame = cv2.resize(frame, (960, 540))
        
        imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)   #convert image to HSV
        h_min = cv2.getTrackbarPos("Hue Min","TrackBars") #Get the positions of the trackbars to use as values
        h_max = cv2.getTrackbarPos("Hue Max", "TrackBars")
        s_min = cv2.getTrackbarPos("Sat Min", "TrackBars")
        s_max = cv2.getTrackbarPos("Sat Max", "TrackBars")
        v_min = cv2.getTrackbarPos("Val Min", "TrackBars")
        v_max = cv2.getTrackbarPos("Val Max", "TrackBars")
        maxlinegap = 0#cv2.getTrackbarPos("maxlinegap", "TrackBars")
        areaTrack = 0#cv2.getTrackbarPos("areaTrack", "TrackBars")
        canny1 =100# cv2.getTrackbarPos("Cannyarg1", "TrackBars")
        canny2 =100# cv2.getTrackbarPos("Cannyarg2", "TrackBars")
        horx1 =0#cv2.getTrackbarPos("horx1", "TrackBars")
        hory1 =0#cv2.getTrackbarPos("hory1", "TrackBars")
        horx2 =0#cv2.getTrackbarPos("horx2", "TrackBars")
        hory2 =0#cv2.getTrackbarPos("hory2", "TrackBars")
        otsu1=125#cv2.getTrackbarPos("otsu_low", "TrackBars")
        otsu2=255#cv2.getTrackbarPos("otsu_up", "TrackBars")
        kernel = np.ones((5,5),np.uint8)
        otsuframe=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # otsuframe = cv2.equalizeHist(otsuframe)
        ret, otsuframe = cv2.threshold(otsuframe, otsu1, otsu2, cv2.THRESH_BINARY + cv2.THRESH_OTSU) 
        frame = cv2.bitwise_and(frame, frame, mask=otsuframe)                                   
        lower = np.array([h_min,s_min,v_min]) #Create an array of min values
        upper = np.array([h_max,s_max,v_max]) #Create an array of max values
        mask = cv2.inRange(imgHSV, lower, upper)
        #print("trackvals: ", h_min, h_max, s_min, s_max, v_min, v_max)
            
        # Display the resulting frame   
        frameResult = cv2.bitwise_and(frame, frame, mask=mask)
        maskCanny = cv2.Canny(frameResult, canny1, canny2)
        #maskCanny = cv2.erode(maskCanny, kernel, iterations=1)
        maskDialated = cv2.dilate(maskCanny, kernel, iterations=3)
        maskDialated = cv2.resize(maskDialated, (960, 540))
        baseyPoint, basexPoint = utils.getbasePoints(maskDialated, minpercentage=0.1)
        #print(baseyPoint, basexPoint)
        if state == 1:
            if basexPoint > 600:
                state+=1
        elif state == 2:
            if baseyPoint > 300:
                state+=1
        elif state == 3:
            if basexPoint < 350:
                state +=1
        elif state == 4:
            if baseyPoint > 400:
                state +=1
        elif state == 5:
            if basexPoint < 330: #THIS VALUE IS FOR THE END OF STATE 5, (final right)
                # print("END")
                pass
                #quit() 
        ##STATE SWITCHER ^^^

        utils.movement(state,move_state)
        utils.centralizeX(basexPoint, state,move_state) ##CENTRALIZATION OF THE LINE DEPENDING ON STATE (VERTICAL/HORIZONTAL)
        utils.centralizeY(baseyPoint, state,move_state)
        # print(state)

        cv2.line(frame, (basexPoint, 0), (basexPoint, 540), (0, 255, 255), 2) ##DRAW LOCATION OF BASEPOINT FOR VISUAL
        cv2.line(frame, (0, baseyPoint), (960, baseyPoint), (0, 255, 255), 2)
        cv2.circle(frame, (basexPoint, baseyPoint), 10, (0, 0, 0), cv2.FILLED)
        contours, hierarchy = cv2.findContours(maskDialated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        lines = cv2.HoughLinesP(maskDialated, 1, np.pi/180, 100, maxLineGap=maxlinegap)
        trackLine(maskDialated,frame,horx1,hory1,horx2,hory2)
        #cv2.imshow("Line", frameResult)
        #getContours(maskDialated)
        #cv2.imshow("Dilated_filter", maskDialated)
        # cv2.imshow("LinesResult", frame)
        # cv2.imshow("Dialated", maskDialated)
        #cv2.imshow("Canny", maskCanny)
        key=cv2.waitKey(1)
        if key == ord('q'):
            return 0
        # elif key == ord('p'):
        #     play=False
        # elif key == ord('r'):
        #     play=True
        return 1 , state,frame
ret=1
state = 1
play=True
move_state=False
# while ret:
#     sys.stdout.flush()
#     ret,frame=vid.read()
#     ret ,state ,show= detection(frame ,state,move_state)
#     cv2.imshow("Canny", show)
#     key=cv2.waitKey(1)
#     if key == ord('q'):
#         break
#     elif key == ord('p'):
#         while key!=ord('r'):
#             key=cv2.waitKey(1)
#             ret ,state ,show= detection(frame ,state,move_state)
#             cv2.imshow("Canny", show)
#     elif key == ord('m'):
#         move_state=True
#     elif key == ord('n'):
#         move_state=False   
    
