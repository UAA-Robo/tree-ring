import sys, time, os
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication, QPushButton, QGridLayout, QLineEdit,\
QMessageBox
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCloseEvent, QImage, QPixmap, QFont
from tkinter.filedialog import askdirectory
from camera import Camera, CriticalIOError
from automationScript import Automation

class InvalidFolderError(Exception):
    def __init__(self, message: str) -> None:
        self.msg = message

class video_stream_thread(QThread):
    def __init__(self, camera: Camera) -> None:
        """
        @brief This thread gets the video (picture) stream from the camera and sends it to the 
            main GUI.
        @param Camera The camera class.
        """
        super().__init__()
        self.camera = camera
    
    # Signal to trigger change in main GUI
    change_image = pyqtSignal(QImage)

    def run(self):
        while True:
            image = self.camera.get_image()  # Converted to QT format
            if image:
                scaled_image = image.scaled(640, 480, Qt.KeepAspectRatio)
                self.change_image.emit(scaled_image)
            time.sleep(0.0001)  # Required to be slower than camera

class automation_listening_thread(QThread):
    """
    @brief This thread monitors the automation class to determine if it is running or not.
    @param Camera The camera class.
    """
    def __init__(self, automation: Automation) -> None:
        super().__init__()
        self.Automation = automation

    automation_status = pyqtSignal(bool)
    automation_message = pyqtSignal(str)

    def run(self): 
        previous_message = ""
        
        while True: 

            current_message = self.Automation.get_automation_status()
            # Prevents app from slowing down by only setting message on change
            if current_message != previous_message:
                self.automation_message.emit(current_message)
                previous_message = current_message

            if self.Automation.status_changed():
                if self.Automation.is_active(): self.automation_status.emit(True)
                else: self.automation_status.emit(False)
                self.Automation.sync_status()

            time.sleep(0.001)


class GUI(QWidget):
    def __init__(self) -> None:
        """
        @brief This is the main GUI class.
        """
        super().__init__()
        self.title = 'Tree Ring Grabber Nabber'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        
        self.core_length = "20"  # Default value (mm)
        self.shift_length = "3"  # Default value (mm)

        self.video_width = 640
        self.video_height = 480
        try:
            self.camera = Camera()
        except CriticalIOError as e:
            raise e
        if not self.camera.is_microscope():
            QMessageBox.warning(None, "Error encountered", 
                                "Microscope camera not connected,\
                                    \ndefaulting to next camera", QMessageBox.Ok)
        try:
            self.Automation = Automation(self.camera)
        except CriticalIOError as e:
            raise e
        
        self.initUI()
        

    @pyqtSlot(QImage)
    def set_image(self, image: QPixmap) -> None:
        """
        @brief Sets the image from the camera in the GUI so a stream shows.
        @param image Image from the video_stream_thread.
        """
    
        image = image.scaled(self.video_width, self.video_height, Qt.KeepAspectRatio)
        self.video_label.setPixmap(QPixmap.fromImage(image))
    
    @pyqtSlot(bool)
    def change_automation_status(self, value: bool) -> None :
        """
        @brief Sets the automation status from the Automation Script
        @param value Status from the automation_listening_thread. True is running, False is stopped.
        """
        if value:
            self.start_stop_button.setText("Stop Automation")
        else:
            self.start_stop_button.setText("Start Automation")

    @pyqtSlot(str)
    def change_automation_message(self, value: str) -> None :
        """
        @brief Sets the automation message from the Automation Script
        @param value Automation Message from the automation_listening_thread.
        """
        self.message_label.setText(value)


    def initUI(self) -> None:
        """
        @brief Sets the layout for the GUI and starts listeners for button presses.
        """

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        #self.setStyleSheet("background-color: black;")
        self.setStyleSheet("""
            QWidget {
                background-color: black;
                font-size: 12pt;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                color: white;
                border: 1px solid white;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit {
                border: none;
                color: white;
                border-bottom: 1px solid white;  
            }
        """)


        # Formatting
        self.grid = QGridLayout(self)

        # Right side for buttons
        self.right_side = QWidget()
        self.right_grid = QGridLayout(self.right_side)
        self.grid.addWidget(self.right_side, 0, 6, 3, 1)
        self.right_side.setFixedHeight(300)

        # Title
        self.title_label = QLabel(self.title, self)
        self.grid.addWidget(self.title_label, 0, 0, 1, 5, Qt.AlignCenter)
        self.title_label.setStyleSheet('QLabel { font-size: 30pt;}')

        # Video label for displaying the stream
        self.video_label = QLabel(self)
        self.grid.addWidget(self.video_label, 1, 0, 1, 5, Qt.AlignCenter )  # Spanning 6 columns

        # Automation Messages
        self.message_label = QLabel(self)
        self.grid.addWidget(self.message_label, 2, 0, 1, 5, Qt.AlignCenter)

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
        self.right_grid.addWidget(self.start_stop_button, 2, 0, 1, 2, Qt.AlignHCenter)
        self.start_stop_button.clicked.connect(
            lambda: self.start_stop_automation()
        )

        self.zeroing_button = QPushButton(self)
        self.zeroing_button.setText("Zero Platform")

        self.right_grid.addWidget(self.zeroing_button, 3, 0, 1, 2, Qt.AlignHCenter)
        self.zeroing_button.clicked.connect(lambda: self.Automation.zero_platform()) # Add Button Trigger


        # Start Video Thread
        self.video_thread = video_stream_thread(self.camera)
        self.video_thread.change_image.connect(self.set_image)
        self.video_thread.start()

        # Start Automation Listening Thread
        self.listening_thread = automation_listening_thread(self.Automation)
        self.listening_thread.automation_status.connect(self.change_automation_status)
        self.listening_thread.automation_message.connect(self.change_automation_message)
        self.listening_thread.start()

        # Starts the GUI
        self.show()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        # return super().closeEvent(a0)
        print("Closing!")
        self.Automation.change_status(False)


    def on_core_input_change(self, text: str) -> None:
        """
        @brief Called every time the text in the core_input textbox changes.
        @param text Contains the new text.
        """

        self.core_length = text
        print(f"New core input: {text}")


    def on_shift_input_change(self, text: str) -> None:
        """
        @brief Called every time the text in the shift_input textbox changes.
        @param text Contains the new text.
        """

        self.shift_length = text
        print(f"New shift input: {text}")


    def start_stop_automation(self) -> None:
        """
        @brief Called when the start/stop button is pressed. On windows when the start button
            is pressed, a dialog prompt asks the user to enter a directory to save images.
        """
        

        if not self.Automation.is_active(): # Pressed 'START'
            try:
                if sys.platform == 'win32': 
                    open_folder = askdirectory()  
                    if open_folder:
                        self.Automation.set_capture_location(open_folder)
                    else:
                        # QMessageBox.warning(self, "Invalid capture directory", "
                        #                     "Please select a capture directory.?", QMessageBox.Ok)
                        raise InvalidFolderError("Please select a captures")
                    print('Capture directory set to', self.Automation.capture_dir)
                    print("Automation started!")
                else:
                    # Ask directory does not work on mac so sets to tree_ring_captures folder on desktop
                    self.Automation.set_capture_location(os.path.expanduser(
                        '~/Desktop/tree_ring_captures'))
                self.Automation.start_automation(float(self.core_length), float(self.shift_length))

            except InvalidFolderError as e:
                QMessageBox.warning(self, "Invalid selection", e.msg, QMessageBox.Ok)
        
        else: # Pressed 'STOP'
            print("Automation stopped")
            self.Automation.change_status(False)



    def resizeEvent(self, event) -> None:
        """
        @brief Updates the image display when the widget is resized. Part of QWidget and called by
            pyqt (name can NOT be changed).
        @param event Event that resizes screen.
        """
        self.video_width = int(self.size().width() * 0.75)
        self.video_height = int(self.size().height() * 0.8)
        super().resizeEvent(event)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        win = GUI()
        win.show()
        sys.exit(app.exec_())
    except CriticalIOError as e:
        QMessageBox.critical(None, "Error encountered", e.msg, QMessageBox.Ok)