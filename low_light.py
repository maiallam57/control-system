# import cv2
# import time
# rtsp = 'rtsp://admin:vortex123@192.168.33.64:554/Streaming/Channels/301/'
# vid = cv2.VideoCapture(rtsp)
# count=0
# start=time.time()
# while(True):
#     ret,frame=vid.read()
#     cv2.imshow('frame',frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#     count+=1
#     if count==1000:
#         break
# vid.release()
# cv2.destroyAllWindows()
# print("fps:"+str(1000/(time.time()-start)))
import cv2
import time
import threading
vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)

start=time.time()
while(True):
        ret,frame=vid.read()
        frame=cv2.resize(frame,(1000,750))
        cv2.imshow('faramel',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
vid.release()
cv2.destroyAllWindows()
