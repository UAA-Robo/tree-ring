import cv2
import sys
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication, QPushButton, QGridLayout
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QImage, QPixmap
from camera import *
from automationScript import Automation


# Code borrowed from https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv


class VideoStreamThread(QThread):
    
    # Signal to trigger change in main GUI
    changePixmap = pyqtSignal(QImage)

    # Signal to trigger pulling image from microscope camera (only acts if using microscope)
    event_image = pyqtSignal()

    def run(self):
        self._apptick = 0
        self.event_image.connect(self.event_image_signal)
        self.camera = Camera(self.camera_callback, self)
        while self.camera.type() == camera_type.WEBCAM:
            self.tasks() # <-------------------------------and here?
            convertToQtFormat = self.camera.stream() #          |
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p) #                         |
    #                                                           |
    def tasks(self): #                                          |
        self._apptick += 1
        print(self._apptick)
        ... # Mya -- still not sure how the camera interacts with the event_image_signal thing
            #        so for other tasks maybe we call that from the signal method?
 #                                                              |
    @staticmethod #                                             |
    def camera_callback(event, ctx): #                          |
        if event == amcam.AMCAM_EVENT_IMAGE: #                  |
            ctx.event_image.emit() #                            |
 #                                                              |
    @pyqtSlot() #                                               |
    def event_image_signal(self): #                             V
        self.tasks() # <------------------------------------ here?
        convertToQtFormat = self.camera.stream()
        p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        self.changePixmap.emit(p)

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Tree Ring Grabber'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.Automation = Automation()

        self.initUI()
        

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Formatting
        self.grid = QGridLayout(self)

        # Create a label
        self.label = QLabel(self)
        self.label.resize(640, 480)

        # Create buttons
        self.start_button = QPushButton(self)
        self.start_button.setGeometry(QRect(150, 70, 93, 28))
        self.start_button.setText("Start Automation")
        self.grid.addWidget(self.start_button, 0, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.start_button.clicked.connect(self.Automation.start_automation) # Add Button Trigger

        # Start Video Thread
        video_thread = VideoStreamThread(self)
        video_thread.changePixmap.connect(self.setImage)
        video_thread.start()
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = GUI()
    win.show()
    sys.exit(app.exec_())