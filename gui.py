import cv2
import sys
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from camera import Camera


# Code borrowed from https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv

Cam = Camera()

class VideoStreamThread(QThread):

    # Signal to trigger change in main GUI
    changePixmap = pyqtSignal(QImage)

    def run(self):
        while True:
            convertToQtFormat = Cam.webcam_picture()
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = GUI()
    win.show()
    sys.exit(app.exec_())