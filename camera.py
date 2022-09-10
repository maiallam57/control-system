
import cv2
import numpy as np
from PyQt5.QtGui import  QImage,QPixmap
from PyQt5.QtCore import QTimer, QSize, Qt,\
    QThread, pyqtSignal, pyqtSlot
# import required libraries
from vidgear.gears import NetGear
#from imutils import build_montages # 


import time
# activate multiserver_mode
options = {"multiserver_mode": True}

# Define NetGear Client at given IP address and assign list/tuple 
# of all unique Server((5566,5567) in our case) and other parameters
# !!! change following IP address '192.168.x.xxx' with yours !!!
client = NetGear(
    address="192.168.33.20",
    port=(5454,),
    protocol="tcp",
    pattern=1,
    receive_mode=True,
    **options
)
class cameraThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    ThreadActive = True
    def __init__(self,cameraSource):
        super().__init__()
        self.cameraSource=cameraSource

    def run(self):
        ''' capture from web cam ''' 
        '''
             i used this:
                cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            insted of this:
                cam = cv2.VideoCapture(1)

            have a look
             https://github.com/ProgrammingHero1/security_cam/issues/2

        '''
        if self.cameraSource==0 or self.cameraSource==1:
            cap = cv2.VideoCapture(self.cameraSource, cv2.CAP_DSHOW)
        elif self.cameraSource=="oak":
            pass  

        else:
            cap = cv2.VideoCapture(self.cameraSource)
        while self.ThreadActive:
            if self.cameraSource != "oak":
                ret, cv_img = cap.read()
                if ret:
                    self.change_pixmap_signal.emit(cv_img)
            else:
                data = client.recv()

        # check if data received isn't None
                if data is None:
                    break

                # extract unique port address and its respective frame
                unique_address, frame = data
                if unique_address == '5454':
                    frame = cv2.cv2.rotate(frame, cv2.ROTATE_180)
                    cv_img=frame
                    self.change_pixmap_signal.emit(cv_img)
                   

            
            
                
        # shut down capture system
        cap.release()