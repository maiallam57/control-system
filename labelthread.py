


from PyQt5.QtCore import QTimer, QSize, Qt,\
    QThread, pyqtSignal, pyqtSlot
import time
class movementThread(QThread):
    change_label_signal = pyqtSignal()
    ThreadActive = True
    def __init__(self):
        super().__init__()
    def run(self):
        while self.ThreadActive:
                self.change_label_signal.emit()
                
                
                