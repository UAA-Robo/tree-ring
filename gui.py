import cv2
import sys, time
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication, QPushButton, QGridLayout, QLineEdit
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QImage, QPixmap
from camera import *
from automationScript import Automation


class VideoStreamThread(QThread):
    def __init__(self, camera: Camera):
        super().__init__()
        self.camera = camera
    
    # Signal to trigger change in main GUI
    change_image = pyqtSignal(QImage)

    def run(self):
        while True:
            convertToQtFormat = self.camera.get_image()
            if convertToQtFormat:
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.change_image.emit(p)
            time.sleep(0.0001)  # Required to be slower than camera


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Tree Ring Grabber'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.input = 20
        self.camera = Camera()
        self.Automation = Automation(self.camera)
        
        self.initUI()
        

    @pyqtSlot(QImage)
    def set_image(self, image):
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Formatting
        self.grid = QGridLayout(self)

        # Video label for displaying the stream
        self.video_label = QLabel(self)
        self.grid.addWidget(self.video_label, 0, 0, 1, 6, Qt.AlignCenter)  # Spanning 6 columns

        # Create input
        self.input_label = QLabel('Core Length (mm)', self)
        self.grid.addWidget(self.input_label, 1, 1)
        self.input_textbox = QLineEdit(self)
        self.input_textbox.setText(str(self.input))
        self.grid.addWidget(self.input_textbox, 1, 2)
        self.input_textbox.textChanged.connect(self.on_input_change)

        # Create buttons
        self.start_button = QPushButton(self)
        self.start_button.setGeometry(QRect(150, 70, 93, 28))
        self.start_button.setText("Start Automation")
        self.grid.addWidget(self.start_button, 1, 3)
        self.start_button.clicked.connect(
            lambda: self.Automation.start_automation(float(self.input))
        )

        self.zeroing_button = QPushButton(self)
        self.zeroing_button.setGeometry(QRect(150, 70, 93, 28))
        self.zeroing_button.setText("Zero Platform")
        self.grid.addWidget(self.zeroing_button, 1, 4)
        self.zeroing_button.clicked.connect(self.Automation.zero_platform) # Add Button Trigger


        # Start Video Thread
        self.video_thread = VideoStreamThread(self.camera)
        self.video_thread.change_image.connect(self.set_image)
        self.video_thread.start()
        self.show()

    def on_input_change(self, text):
        """
        @brief Called every time the text in the textbox changes.
        @param text Contains the new text.
        """

        self.input = float(text)
        print(f"New input: {text}")




if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = GUI()
    win.show()
    sys.exit(app.exec_())