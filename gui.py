import cv2
import sys
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication, QPushButton, QGridLayout
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QImage, QPixmap
from camera import *
from automationScript import Automation


class VideoStreamThread(QThread):
    def __init__(self, camera: Camera):
        super().__init__()
        self.camera = camera
    
    # Signal to trigger change in main GUI
    changePixmap = pyqtSignal(QImage)

    # Signal to trigger pulling image from microscope camera (only acts if using microscope)
    event_image = pyqtSignal()

    def run(self):
        self.event_image.connect(self.event_image_signal)
        # self.camera = Camera(self.camera_callback, self)
        while self.camera.type() == camera_type.WEBCAM:
            convertToQtFormat = self.camera.stream()
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)

    @staticmethod
    def camera_callback(event, ctx):
        if event == amcam.AMCAM_EVENT_IMAGE:
            ctx.event_image.emit()

    @pyqtSlot()
    def event_image_signal(self):
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
        self.camera = Camera()
        self.Automation = Automation(self.camera)
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
        video_thread = VideoStreamThread(self.camera)
        video_thread.changePixmap.connect(self.setImage)
        video_thread.start()
        self.camera.connect_stream(video_thread.camera_callback, video_thread)
        self.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = GUI()
    win.show()
    sys.exit(app.exec_())