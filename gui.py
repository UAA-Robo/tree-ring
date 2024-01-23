import cv2
import sys, time, os
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication, QPushButton, QGridLayout, QLineEdit
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QImage, QPixmap
from tkinter.filedialog import askdirectory
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

class AutomationListeningThread(QThread):
    def __init__(self, automation: Automation):
        super().__init__()
        self.Automation = automation

    automation_status = pyqtSignal(bool)

    def run(self): 
        while True: 
            if self.Automation.status_changed():
                if self.Automation.is_active(): self.automation_status.emit(True)
                else: self.automation_status.emit(False)
                self.Automation.sync_status()


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Tree Ring Grabber'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        
        self.core_length = 20  # Default value (mm)
        self.shift_length = 3  # Default value (mm)
        self.camera = Camera()
        self.Automation = Automation(self.camera)
        
        self.initUI()
        

    @pyqtSlot(QImage)
    def set_image(self, image):
        self.video_label.setPixmap(QPixmap.fromImage(image))
    
    @pyqtSlot(bool)
    def change_automation_status(self, value: bool):
        if value:
            self.start_stop_button.setText("Stop Automation")
        else:
            self.start_stop_button.setText("Start Automation")

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        #self.setStyleSheet("background-color: black;")
        self.setStyleSheet("""
            QWidget {
                background-color: black;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                color: white;
                border: 1px solid white;
                border-radius: 15px;
                padding: 10px;
            }
            QLineEdit {
                border: none;
                border-bottom: 1px solid white;  
            }
        """)


        # Formatting
        self.grid = QGridLayout(self)


        # Video label for displaying the stream
        self.video_label = QLabel(self)
        self.grid.addWidget(self.video_label, 0, 0, 1, 5, Qt.AlignCenter )  # Spanning 6 columns

        # Right side for buttons
        self.right_side = QWidget()
        self.right_grid = QGridLayout(self.right_side)
        self.grid.addWidget(self.right_side, 0, 6)
        self.right_side.setFixedHeight(300)

        # Create core length input
        self.core_input_label = QLabel('Core Length (cm)', self)
        self.right_grid.addWidget(self.core_input_label, 0, 0, Qt.AlignRight)
        self.core_input_textbox = QLineEdit(self)
        self.core_input_textbox.setText(str(self.core_length))
        self.core_input_textbox.setFixedWidth(50)
        self.right_grid.addWidget(self.core_input_textbox, 0, 1, Qt.AlignLeft)
        self.core_input_textbox.textChanged.connect(self.on_core_input_change)

        # Create shift length input
        self.shift_input_label = QLabel('Shift Length (mm)', self)
        self.right_grid.addWidget(self.shift_input_label, 1,0, Qt.AlignRight)
        self.shift_input_textbox = QLineEdit(self)
        self.shift_input_textbox.setText(str(self.shift_length))
        self.shift_input_textbox.setFixedWidth(50)
        self.right_grid.addWidget(self.shift_input_textbox, 1, 1, Qt.AlignLeft)
        self.shift_input_textbox.textChanged.connect(self.on_shift_input_change)


        # Create buttons
        self.start_stop_button = QPushButton(self)
        self.start_stop_button.setText("Start Automation")
        self.start_stop_button.setFixedWidth(150)
        self.right_grid.addWidget(self.start_stop_button, 2, 0, 1, 2, Qt.AlignHCenter)
        self.start_stop_button.clicked.connect(
            lambda: self.start_stop_automation()
        )

        self.zeroing_button = QPushButton(self)
        self.zeroing_button.setText("Zero Platform")
        self.zeroing_button.setFixedWidth(150)
        self.right_grid.addWidget(self.zeroing_button, 3, 0, 1, 2, Qt.AlignHCenter)
        self.zeroing_button.clicked.connect(self.Automation.zero_platform) # Add Button Trigger


        # Start Video Thread
        self.video_thread = VideoStreamThread(self.camera)
        self.video_thread.change_image.connect(self.set_image)
        self.video_thread.start()

        # Start Automation Listening Thread
        self.listening_thread = AutomationListeningThread(self.Automation)
        self.listening_thread.automation_status.connect(self.change_automation_status)
        self.listening_thread.start()

        # Starts the GUI
        self.show()


    def on_core_input_change(self, text):
        """
        @brief Called every time the text in the textbox changes.
        @param text Contains the new text.
        @param update_value     Value to update (needs to be pointer aka class variable)
        """

        self.core_length = text
        print(f"New core input: {text}")

    def on_shift_input_change(self, text):
        """
        @brief Called every time the text in the textbox changes.
        @param text Contains the new text.
        @param update_value     Value to update (needs to be pointer aka class variable)
        """

        self.shift_length = text
        print(f"New shift input: {text}")

    def start_stop_automation(self):
        

        if not self.Automation.is_active(): # Pressed 'START'
            # Ask directory does not work on mac
            if sys.platform == 'win32': 
                open_folder = askdirectory()  
                if open_folder:
                    self.Automation.set_capture_location(open_folder)
                print('Capture directory set to', self.Automation.capture_dir)
                print("Automation started!")

            self.Automation.start_automation(float(self.core_length), float(self.shift_length))
        else: # Pressed 'STOP'
            print("Automation stopped")
            self.Automation.change_active_status(False)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = GUI()
    win.show()
    sys.exit(app.exec_())