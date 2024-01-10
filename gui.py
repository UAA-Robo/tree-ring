import cv2
import sys
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap



# Code borrowed from https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv

class VideoStreamThread(QThread):

    # Signal to trigger change in main GUI
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
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
        #self.resize(1800, 1200)
        # create a label
        self.label = QLabel(self)
        #self.label.move(280, 120)
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