import sys
import config
import os
import time
import cfg
import subprocess
from tkinter.ttk import LabeledScale 
import numpy as np
import cv2
from PyQt5.QtGui import  QImage,QPixmap,QFont
from PyQt5.QtWidgets import QMainWindow,QApplication,\
    QVBoxLayout, QFrame,QHBoxLayout, QVBoxLayout,\
        QLabel, QGridLayout, QLineEdit, QPushButton,\
            QStatusBar, QMenuBar,QStackedWidget,QAction
from PyQt5.QtCore import QTimer, QSize, Qt,\
    QThread, pyqtSignal, pyqtSlot
import threading
from PyQt5 import uic
from labelthread import movementThread
from analoggaugewidget import AnalogGaugeWidget
#from camera import cameraThread
import cfg
from joystick_new import joystick
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc

import cv2
import numpy as np
# subprocess.Popen("python oak_readstream.py",shell=True)
# def recv_oak():
#     process = subprocess.Popen("python test_process.py", stdout=subprocess.PIPE)
#     while True:
#         output = process.stdout.readline()
#         if output == '' and process.poll() is not None:
#             break
#         if output:
#             print( (output.strip()).decode())
#     rc = process.poll()
#     return rc
# oak_outputs=threading.Thread(target=recv_oak)
# oak_outputs.start()
# print("after call")
class pilotUI(QMainWindow):
    
    cameraL1 = None
    cameraL2 = None
    arrowforlabel=None
    arrowbacklabel=None
    arrowrightlabel=None
    arrowuplabel=None
    arrowdownlabel=None
    arrowcwlabel=None
    arrowccwlabel=None
    gripperlabel=None
    docking_btn= None
    joy_stick_thread=None 
    armed_disarm=None  
    second = 0      # related to the GUI Timer 
    minutes = 0
    
    def __init__(self) :
        super(pilotUI, self).__init__()
        
        # load the ui file
        uic.loadUi('modern.ui',self)
        
        # show the App
        self.show()
        # defining ui components
        self.ui_components()
        # self.agw = AnalogGaugeWidget(self)
        # self.agw.value_min = 0
        # self.agw.value_max = 400
        # self.agw.DisplayValueColor = qtg.QColor(255, 0, 0, 255)
        # self.agw.ScaleValueColor = qtg.QColor(255, 0, 0, 255)
        # self.agw.NeedleColor = qtg.QColor(255, 80, 0, 255)
        # self.agw.CenterPointColor = qtg.QColor(255, 80, 0, 255)
        # self.agw.update_value(100)
        # self.agw.show()
        # self.agw.update_value(100)
        # camera setting ------------>
        
        # self.cam1 = cameraThread("oak")
        # self.cameraWidth = self.cameraL1.size().width()
        # self.cameraHight = self.cameraL1.size().height()
        # # connect its signal to the update_image slot
        # self.cam1.change_pixmap_signal.connect(self.update_image)
        # # start the thread
        # self.cam1.start()

        # self.cam2 = cameraThread(1)
        # self.cameraWidth = self.cameraL2.size().width()
        # self.cameraHight = self.cameraL2.size().height()
        # #connect its signal to the update_image slot
        # self.cam2.change_pixmap_signal.connect(self.update_image2)
        # # start the thread
        # self.cam2.start()
        thjoy=threading.Thread(target=self.joyinit)
        thjoy.start()
        time.sleep(0.1)
        # self.mov=movementThread()
        # self.mov.change_label_signal.connect(self.updateLabels)
        # self.mov.start()

        # self.mov2=movementThread()
        # self.mov2.change_label_signal.connect(self.updatelabels2)
        # self.mov2.start()
      
        # self.sensor_readings=movementThread()
        # self.sensor_readings.change_label_signal.connect(self.updatelabels3)
        # self.sensor_readings.start()
        
        # guage=threading.Thread(target=self.guage)
        # guage.start()
        # self.agw_thread=movementThread()
        # self.agw_thread.change_label_signal.connect(self.updatelabels4)
        # self.agw_thread.start()

        self.timer=QTimer()
        self.timer.timeout.connect(self.timeCounter)
        self.timer.start(200)    # what does this line do??!
       
        self.cnt=0

        

        
    
    def ui_components(self):
        """ defining ui components from 'pilot.ui' file as variables """ 

        self.stackedwidget=self.findChild(QStackedWidget,"stackedwidget")
        self.cameraL1 = self.findChild(QLabel,"Maincamera")
        self.cameraL2 = self.findChild(QLabel,"GripperCamera")
        self.timerLabel = self.findChild(QLabel,"timerLabel")
        self.stopTimer = self.findChild(QPushButton,"stopButton")
        self.startTimer = self.findChild(QPushButton,"startButton")
        self.resetTimer = self.findChild(QPushButton,"resetButton")
        self.arrowforlabel=self.findChild(QLabel,"forward")
        self.arrowbacklabel=self.findChild(QLabel,"backwardBtn")
        self.arrowrightlabel=self.findChild(QLabel,"rightBtn")
        self.arrowleftlabel=self.findChild(QLabel,"leftBtn")
        self.arrowuplabel=self.findChild(QLabel,"upBtn")
        self.arrowdownlabel=self.findChild(QLabel,"downBtn")
        self.arrowcwlabel=self.findChild(QLabel,"cwBtn")
        self.arrowccwlabel=self.findChild(QLabel,"ccwBtn")
        self.gripperlabel=self.findChild(QLabel,"openGripper")
        self.horizontalGripperLabel=self.findChild(QLabel,"horizontal_gripper_open")
        self.armed_disarm=self.findChild(QLabel,"armed_disarm")
        self.armed_disarm.setText('<h3 >'+"Disarmed"+'</h3>')
        self.temp=self.findChild(QLabel,"temp")
        self.vAcce=self.findChild(QLabel,"vAcce")
        self.vBar30=self.findChild(QLabel,"vBar30")
        self.vGyro=self.findChild(QLabel,"vGyro")
        self.vTemp=self.findChild(QLabel,"vTemp")
        self.agw=self.findChild(AnalogGaugeWidget,"analog_widget")
        self.labelspeed=self.findChild(QLabel,"label_3")
        self.agw.update_value(100)
        # self.actionExit = self.findChild(QAction, "actionExit")
        # self.actionExit.triggered.connect(self.closeEvent)
        
        self.docking_btn=self.findChild(QPushButton,"dockingbutton")
        self.docking_btn.setText("docking")
        # print(self.docking_btn)
        self.docking_btn.clicked.connect(self.docking)
        self.timerButtons()


     
    # ---------------------------- Camera controls ----------------------------

    def closeEvent (self,event):
        
        print("exit")
        os._exit(0)


    
    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        cameraLabel_Obj = self.cameraL1
        cameraWidth = cameraLabel_Obj.size().width()-2 # the -2 is a must or the camera size will keep growing 
        cameraHight = cameraLabel_Obj.size().height()-2
        qt_img = self.convert_cv_qt(cv_img, cameraWidth,cameraHight)
        cameraLabel_Obj.setPixmap(qt_img)
    
    @pyqtSlot(np.ndarray)
    def update_image2(self, cv_img):
        """Updates the image_label with a new opencv image"""
        cameraLabel_Obj = self.cameraL2
        cameraWidth = cameraLabel_Obj.size().width()-2 # the -2 is a must or the camera size will keep growing 
        cameraHight = cameraLabel_Obj.size().height()-2
        qt_img = self.convert_cv_qt(cv_img, cameraWidth,cameraHight)
        cameraLabel_Obj.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img, cameraW,cameraH):
        """Convert from an opencv image to QPixmap"""

        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(cameraW, cameraH, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def stopCamera_Function(self,threadObj,displayStatObj):
        if threadObj.ThreadActive == True:
            threadObj.ThreadActive = False
            displayStatObj.setText('Start Camera')
        elif threadObj.ThreadActive == False:
            threadObj.ThreadActive = True
            displayStatObj.setText('Stop Camera')
            threadObj.start()
            
            
            
    # --------------------------------- Timer ---------------------------------
    
    def timerButtons(self):
        ''' connecting buttons with functions'''
        
        self.stopTimer.clicked.connect(self.stop_timeCounter)
        self.startTimer.clicked.connect(self.start_timeCounter)
        self.startTimer.setEnabled(False)
        self.resetTimer.clicked.connect(self.reset_timeCounter)
        self.resetTimer.setEnabled(False)

    
    def timeCounter(self):
        self.cnt+=1
        if self.cnt==5:
            self.cnt=0
            self.second +=1
            if (self.second == 59):
                self.minutes += 1
                self.second = 0
            text = str(self.minutes) + ' : ' + str(self.second)
            self.timerLabel.setText('<h1 style="color:white">'+text+'</h1>')
        if cfg.joy.flag_speed_up %2:
            self.labelspeed.setText("current speed: High speed")
        else:
            self.labelspeed.setText("current speed: low speed")
        if cfg.joy.flag_forward_arrow: 
            self.arrowforlabel.setPixmap(QPixmap("qss_icons/icons/frwrd-arrow.png"))
        else:
            self.arrowforlabel.setPixmap(QPixmap("qss_icons/icons/frwrd-arrowred.png"))
        if cfg.joy.flag_right_arrow: 
            self.arrowrightlabel.setPixmap(QPixmap("qss_icons/icons/right-arrow.png"))
        else:
            self.arrowrightlabel.setPixmap(QPixmap("qss_icons/icons/right-arrowred.png"))
        if cfg.joy.flag_left_arrow: 
            self.arrowleftlabel.setPixmap(QPixmap("qss_icons/icons/left-arrow.png"))
        else:
            self.arrowleftlabel.setPixmap(QPixmap("qss_icons/icons/left-arrowred.png"))
        if cfg.joy.flag_backward_arrow: 
            self.arrowbacklabel.setPixmap(QPixmap("qss_icons/icons/bckwrd-arrow.png"))
        else:
            self.arrowbacklabel.setPixmap(QPixmap("qss_icons/icons/bckwrd-arrowred.png"))
        if cfg.joy.flag_up_arrow: 
            self.arrowuplabel.setPixmap(QPixmap("qss_icons/icons/upward-arrow.png"))
        else:
            self.arrowuplabel.setPixmap(QPixmap("qss_icons/icons/upward-arrowred.png"))
        if cfg.joy.flag_down_arrow: 
            self.arrowdownlabel.setPixmap(QPixmap("qss_icons/icons/downward-arrow.png"))
        else:
            self.arrowdownlabel.setPixmap(QPixmap("qss_icons/icons/downward-arrowred.png"))
        if cfg.joy.flag_yaw_right: 
            self.arrowcwlabel.setPixmap(QPixmap("qss_icons/icons/cw.png"))
        else:
           self.arrowcwlabel.setPixmap(QPixmap("qss_icons/icons/cwred.png"))
        if cfg.joy.flag_yaw_left: 
            self.arrowccwlabel.setPixmap(QPixmap("qss_icons/icons/ccw.png"))
        else:
           self.arrowccwlabel.setPixmap(QPixmap("qss_icons/icons/ccwred.png"))
 
             
        
        if cfg.joy.flag_arm %2==1:
            self.armed_disarm.setText('<h3 >'+"Armed"+'</h3>')
            
            self.armed_disarm.setStyleSheet("background-color: #42ba32;")
        else:
            self.armed_disarm.setText('<h3 >'+"Disarmed"+'</h3>')
            self.armed_disarm.setStyleSheet("background-color: rgb(236, 28, 36);")
        if cfg.joy.flag_gripper1 %2==1:
            self.gripperlabel.setPixmap(QPixmap("qss_icons/icons/grapper-open.png"))
        else:
            self.gripperlabel.setPixmap(QPixmap("qss_icons/icons/grapper-close.png"))

        if cfg.joy.flag_gripper2 %2==1:
            self.horizontalGripperLabel.setPixmap(QPixmap("qss_icons/icons/grapper-open-horizontal.png"))
        else:
            self.horizontalGripperLabel.setPixmap(QPixmap("qss_icons/icons/grapper-close-horizontalpng.png")) 
        # self.updatelabels3()

    def stop_timeCounter(self):
        self.stopTimer.setEnabled(False)
        self.startTimer.setEnabled(True)
        self.resetTimer.setEnabled(True)
        self.timer.timeout.disconnect(self.timeCounter)

    def start_timeCounter(self):
        self.startTimer.setEnabled(False)
        self.stopTimer.setEnabled(True)
        self.resetTimer.setEnabled(False)
        self.timer.timeout.connect(self.timeCounter)

    def reset_timeCounter(self):
        self.startTimer.setEnabled(True)
        self.stopTimer.setEnabled(False)
        self.resetTimer.setEnabled(False)
        self.second = 0
        self.minutes = 0
        self.timerLabel.setText('<h1 style="color:white">' + '00:00' + '</h1>')
    
    def docking (self):
        # subprocess.Popen("python docking_try.py",shell=True)
        rc_channels=[1500 for _ in range(9)]
        rc_channels=cfg.joy.forward(rc_channels,1700)
        # time.sleep(3)
        rc_channels=cfg.joy.forward(rc_channels,1500)



    @pyqtSlot()
    def updateLabels(self):
        pass
    @pyqtSlot()
    def updatelabels2(self):
        pass

    def updatelabels3(self):
        
        # self.vTemp.setText ('<h3 >'+"temp"+'</h3>')
        # imuData = config.sensors[0]
        # xacc=imuData['xacc']
        # yacc=imuData['yacc']
        # zacc = imuData['zacc']
        if config.sensors:
            pressure = (config.sensors[0]-908)*0.0101971621
        
        # xgyro=imuData['xgyro']
        # ygyro=imuData['ygyro']
        # zgyro =imuData['zgyro']
        # self.vAcce.setText ('<h3 >'+"x:"+str(xacc)+"\n"+'<h3 >'+"y:"+str(yacc)+"\n"+'<h3 >'+"z:"+str(zacc))
        # self.vGyro.setText ('<h3 >'+"x:"+str(xgyro)+"\n"+'<h3 >'+"y:"+str(ygyro)+"\n"+'<h3 >'+"z:"+str(zgyro))
        self.vBar30.setText ('<h3 >'+str(round(pressure,3))+'</h3>')
    
    # def  updatelabels4(self):
    #     print(cfg.joy.guage_value)
    #     self.agw.update_value(cfg.joy.guage_value)
    # def guage(self):
    #     while True:
    #         self.agw.update_value(config.guage_value)
        pass
    def joyinit(self):
        joystick()



app =  QApplication(sys.argv)
cfg.pilotUI = pilotUI()

print("before")
app.exec_()
print("after")


