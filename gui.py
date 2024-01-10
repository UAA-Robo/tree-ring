import cv2
import sys
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from camera import *


# Code borrowed from https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv

# Cam = Camera()

class VideoStreamThread(QThread):

    # Signal to trigger change in main GUI
    changePixmap = pyqtSignal(QImage)

    # Signal to trigger pulling image from microscope camera (only acts if using microscope)
    event_image = pyqtSignal()

    def run(self):
        self.event_image.connect(self.event_image_signal)
        self.camera = Camera(self.camera_callback, self)
        while self.camera.type() == camera_type.WEBCAM:
            self.tasks() # <-------------------------------and here?
            convertToQtFormat = self.camera.stream() #          |
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p) #                         |
    #                                                           |
    def tasks(self): #                                          |
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
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # create a label
        self.label = QLabel(self)
        self.label.resize(640, 480)
        video_thread = VideoStreamThread(self)
        video_thread.changePixmap.connect(self.setImage)
        video_thread.start()
        self.show()

# if __name__ == '__main__':
if True:
    app = QApplication(sys.argv)
    win = GUI()
    win.show()
    sys.exit(app.exec_())