import sys, time, os
import threading
from PyQt5.QtWidgets import  QWidget, QLabel, QCheckBox, QSlider, QApplication, QPushButton, QGridLayout, QLineEdit,\
QMessageBox, QHBoxLayout, QComboBox
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
        @param camera The camera class.
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
    def __init__(self, automation: Automation) -> None:
        """
        @brief This thread monitors the automation class to determine if it is running or not.
        @param automation The Automation class.
        """
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
        
        self.image_name = "Tree_Core"  # Default value
        self.core_length = "20"  # Default value (cm)
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
        self.camera_options_widget = None
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
        self.stylesheet = """
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
        """
        self.setStyleSheet(self.stylesheet)


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
        self.grid.addWidget(self.message_label, 2, 1, 1, 5, Qt.AlignCenter)

        # Create image name input
        self.image_name_label = QLabel('Image/Core name', self)
        self.right_grid.addWidget(self.image_name_label, 0,0, Qt.AlignRight)
        self.image_name_textbox = QLineEdit(self)
        self.image_name_textbox.setText(str(self.image_name))
        self.image_name_textbox.setFixedWidth(100)
        self.right_grid.addWidget(self.image_name_textbox, 0, 1, Qt.AlignLeft)
        self.image_name_textbox.textChanged.connect(self.on_image_name_change)

        # Create core length input
        self.core_input_label = QLabel('Core Length (cm)', self)
        self.right_grid.addWidget(self.core_input_label, 1, 0, Qt.AlignRight)
        self.core_input_textbox = QLineEdit(self)
        self.core_input_textbox.setText(str(self.core_length))
        self.core_input_textbox.setFixedWidth(50)
        self.right_grid.addWidget(self.core_input_textbox, 1, 1, Qt.AlignLeft)
        self.core_input_textbox.textChanged.connect(self.on_core_input_change)

        # Create shift length input
        self.shift_input_label = QLabel('Shift Length (mm)', self)
        self.right_grid.addWidget(self.shift_input_label, 2,0, Qt.AlignRight)
        self.shift_input_textbox = QLineEdit(self)
        self.shift_input_textbox.setText(str(self.shift_length))
        self.shift_input_textbox.setFixedWidth(50)
        self.right_grid.addWidget(self.shift_input_textbox, 2, 1, Qt.AlignLeft)
        self.shift_input_textbox.textChanged.connect(self.on_shift_input_change)


        # Create buttons
        self.single_picture_button = QPushButton(self)
        self.single_picture_button.setText("Take Single Image")
        self.right_grid.addWidget(self.single_picture_button, 3, 0, 1, 2)
        self.single_picture_button.clicked.connect(
            lambda: self.take_single_image()
        )

        self.start_stop_button = QPushButton(self)
        self.start_stop_button.setText("Start Automation")
        self.right_grid.addWidget(self.start_stop_button, 4, 0, 1, 1)
        self.start_stop_button.clicked.connect(
            lambda: self.start_stop_automation()
        )
        
        self.options_button = QPushButton(self)
        self.options_button.setText("Adjust Camera Options")
        self.right_grid.addWidget(self.options_button, 5, 0, 1, 2, Qt.AlignHCenter)
        self.options_button.clicked.connect(
            lambda: self.open_camera_options_widget()
        )

        self.pause_play_button = QPushButton(self)
        self.pause_play_button.setText("Pause")
        self.right_grid.addWidget(self.pause_play_button, 4, 1, 1, 1)
        self.pause_play_button.clicked.connect(
            lambda: self.pause_play()
        )




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
        if self.camera_options_widget is not None: self.camera_options_widget.close()
        self.Automation.change_status(False)

    def on_image_name_change(self, text: str) -> None:
        """
        @brief Called every time the text in the image_name_textbox changes.
        @param text Contains the new text.
        """

        self.image_name = text
        print(f"New image name input: {text}")

    def on_core_input_change(self, text: str) -> None:
        """
        @brief Called every time the text in the core_input_textbox changes.
        @param text Contains the new text.
        """

        self.core_length = text
        print(f"New core input: {text}")


    def on_shift_input_change(self, text: str) -> None:
        """
        @brief Called every time the text in the shift_input_textbox changes.
        @param text Contains the new text.
        """

        self.shift_length = text
        print(f"New shift input: {text}")

    def pause_play(self) -> None:
        """
        @brief Pauses or plays the automation status.
        """
        if self.Automation.is_paused():
            self.Automation.set_pause(False)
            self.pause_play_button.setText("Pause")
        else:
            self.Automation.set_pause(True)
            self.pause_play_button.setText("Play")

    def take_single_image(self) -> None:
        """
        @brief Takes single image, saving it in the specified directory.
        """
        self.set_directory()
        self.Automation.get_picture_in_thread(self.image_name)
        
    def open_camera_options_widget(self) -> None:
        self.camera_options_widget = CameraOptionsGUI(self.camera, self.stylesheet)
        self.camera_options_widget.launch_dialog()


    def start_stop_automation(self) -> None:
        """
        @brief Called when the start/stop button is pressed. On windows when the start button
            is pressed, a dialog prompt asks the user to enter a directory to save images.
        """
        

        if not self.Automation.is_active(): # Pressed 'START'
            self.set_directory()
            self.Automation.start_automation(self.image_name, float(self.core_length), float(self.shift_length))
        
        else: # Pressed 'STOP'
            print("Automation stopped")
            self.Automation.change_status(False)

    def set_directory(self):
        try:
            if sys.platform == 'win32': 
                open_folder = askdirectory()  
                if open_folder:
                    self.Automation.set_capture_location(open_folder)
                else:
                    raise InvalidFolderError("Please select a captures")
                print('Capture directory set to', self.Automation._capture_dir)
                print("Automation started!")
            else:
                # Ask directory does not work on mac so sets to tree_ring_captures folder on desktop
                self.Automation.set_capture_location(os.path.expanduser(
                    '~/Desktop/tree_ring_captures'))
        except InvalidFolderError as e:
            QMessageBox.warning(self, "Invalid selection", e.msg, QMessageBox.Ok)
    


    def resizeEvent(self, event) -> None:
        """
        @brief Updates the image display when the widget is resized. Part of QWidget and called by
            pyqt (name can NOT be changed).
        @param event Event that resizes screen.
        """
        self.video_width = int(self.size().width() * 0.75)
        self.video_height = int(self.size().height() * 0.8)
        super().resizeEvent(event)

    def run_in_thread(function):
        """
        @brief  Wrap function in a thread.
        @param function     Function to put in thread.
        """
        def wrapper(*args, **kwargs):
            thread = threading.Thread(target=function, args=args, kwargs=kwargs)
            thread.start()
            return thread
        return wrapper


    ############################################################################################
    #  Associated GUI Widgets                                                                  #
    ############################################################################################


class Slider(QWidget):
    def __init__(self, callback: callable, min_range: int, max_range: int, delta: int) -> None:
        super(Slider, self).__init__()
        self.callback = callback
        self.minimum = min_range
        self.maximum = max_range
        self.delta = delta
        self.value: int = None
        self.boxlayout = QHBoxLayout()
        self.decrement_btn = QPushButton(self)
        self.decrement_btn.setText("-")
        self.decrement_btn.clicked.connect(self.decrement_value)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(self.minimum, self.maximum)
        self.slider.valueChanged.connect(self.update_value)
        self.increment_btn = QPushButton(self)
        self.increment_btn.setText("+")
        self.increment_btn.clicked.connect(self.increment_value)
        self.boxlayout.addWidget(self.decrement_btn)
        self.boxlayout.addWidget(self.slider)
        self.boxlayout.addWidget(self.increment_btn)
        self.setLayout(self.boxlayout)

    def set_value(self, value: int) -> None:
        self.value = value
        self.slider.setValue(self.value)

    def get_value(self) -> int: return self.value

    def decrement_value(self, value: int) -> None:
        self.value -= self.delta
        self.slider.setValue(self.value)
        self.callback(self.value)

    def increment_value(self, value: int) -> None:
        self.value += self.delta
        self.slider.setValue(self.value)
        self.callback(self.value)

    def update_value(self, value: int):
        self.value = value
        self.callback(self.value)


class CameraOptionsGUI(QWidget):
    def __init__(self, camera: Camera, stylesheet: str) -> None:
        """
        @brief This widget controls camera video options
        """
        super().__init__()
        self.toggled = False
        self.title = ''
        self._camera = camera
        self.stylesheet = stylesheet # <-- COULD REMOVE
        self.stylesheet = """
        QWidget {
            background-color: black;
            font-size: 12pt;
        }
        QLabel {
            color: white;
            font-size: 8pt;
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
    """
        # self.left = 100
        # self.top = 100
        # self.width = 300
        # self.height = 200
        self.setFixedHeight(500)
        self.setFixedWidth(300)
        
        self.initUI()

    def launch_dialog(self):
        self.toggled = True
        self.load_default_slider_values()
        self.show()
        
    def initUI(self) -> None:
        self.setStyleSheet(self.stylesheet)
        self.grid = QGridLayout(self)
        # self.grid.setSpacing(0)
        self.sliders_side = QWidget()
        self.buttons_bottom = QWidget()
        self.sliders_grid = QGridLayout(self.sliders_side)
        self.buttons_grid = QGridLayout(self.buttons_bottom)
        self.grid.addWidget(self.sliders_side, 0, 0, 4, 6)
        self.grid.addWidget(self.buttons_bottom, 4, 0, 1, 6)

        self.fformat_label = QLabel('File Format', self)
        self.sliders_grid.addWidget(self.fformat_label, 0, 0, alignment=Qt.AlignLeft)
        # self.fformat_dropdown = FileFormatComboBox(self.update_fformat_value)
        self.fformat_dropdown = QComboBox(self)
        self.fformat_dropdown.addItems(('jpeg', 'tiff', 'png'))
        self.fformat_dropdown.currentIndexChanged.connect(self.update_fformat_value)
        self.fformat_dropdown.setStyleSheet(
            '''
            QWidget {
                background-color: white;
                font-size: 11pt;
            }
            '''
        )
        self.sliders_grid.addWidget(self.fformat_dropdown, 0, 0, alignment=Qt.AlignRight)

        self.temp_label = QLabel('Temperature', self)
        self.sliders_grid.addWidget(self.temp_label, 1, 0, alignment=Qt.AlignLeft)
        self.temp_slider = Slider(self.update_temp_value, 2000, 15000, 5)
        self.sliders_grid.addWidget(self.temp_slider, 1, 0, alignment=Qt.AlignRight)

        self.tint_label = QLabel('Tint', self)
        self.sliders_grid.addWidget(self.tint_label, 2, 0, alignment=Qt.AlignLeft)
        self.tint_slider = Slider(self.update_tint_value, 200, 2500, 2)
        self.sliders_grid.addWidget(self.tint_slider, 2, 0, alignment=Qt.AlignRight)

        self.contrast_label = QLabel('Contrast', self)
        self.sliders_grid.addWidget(self.contrast_label, 3, 0, alignment=Qt.AlignLeft)
        self.contrast_slider = Slider(self.update_contrast_value, -100, 100, 1)
        self.sliders_grid.addWidget(self.contrast_slider, 3, 0, alignment=Qt.AlignRight)

        self.hue_label = QLabel('Hue', self)
        self.sliders_grid.addWidget(self.hue_label, 4, 0, alignment=Qt.AlignLeft)
        self.hue_slider = Slider(self.update_hue_value, -180, 180, 1)
        self.sliders_grid.addWidget(self.hue_slider, 4, 0, alignment=Qt.AlignRight)

        self.saturation_label = QLabel('Saturation', self)
        self.sliders_grid.addWidget(self.saturation_label, 5, 0, alignment=Qt.AlignLeft)
        self.saturation_slider = Slider(self.update_saturation_value, 0, 255, 1)
        self.sliders_grid.addWidget(self.saturation_slider, 5, 0, alignment=Qt.AlignRight)

        self.brightness_label = QLabel('Brightness', self)
        self.sliders_grid.addWidget(self.brightness_label, 6, 0, alignment=Qt.AlignLeft)
        self.brightness_slider = Slider(self.update_brightness_value, -64, 64, 1)
        self.sliders_grid.addWidget(self.brightness_slider, 6, 0, alignment=Qt.AlignRight)

        self.sharpening_label = QLabel('Sharpening', self)
        self.sliders_grid.addWidget(self.sharpening_label, 7, 0, alignment=Qt.AlignLeft)
        self.sharpening_slider = Slider(self.update_sharpening_value, 0, 500, 2)
        self.sliders_grid.addWidget(self.sharpening_slider, 7, 0, alignment=Qt.AlignRight)
        
        self.linear_label = QLabel('Linear TM', self)
        self.sliders_grid.addWidget(self.linear_label, 8, 0, alignment=Qt.AlignLeft)
        self.linear_cb = QCheckBox(self)
        self.sliders_grid.addWidget(self.linear_cb, 8, 0, alignment=Qt.AlignRight)
        self.linear_cb.stateChanged.connect(self.update_linear_value)

        self.curve_label = QLabel('Curve TM', self)
        self.sliders_grid.addWidget(self.curve_label, 9, 0, alignment=Qt.AlignLeft)
        self.curve_dropdown = QComboBox(self)
        self.curve_dropdown.addItems(('Off', 'Polynomial', 'Logarithmic'))
        self.curve_dropdown.currentIndexChanged.connect(self.update_curve_value)
        self.curve_dropdown.setStyleSheet(
            '''
            QWidget {
                background-color: white;
                font-size: 11pt;
            }
            '''
        )
        self.sliders_grid.addWidget(self.curve_dropdown, 9, 0, alignment=Qt.AlignRight)


        # Create buttons
        self.save_button = QPushButton(self)
        self.save_button.setText("Save")
        self.buttons_grid.addWidget(self.save_button, 0, 0, alignment=Qt.AlignLeft)
        self.save_button.clicked.connect(
            lambda: self.save_configuration()
        )

        self.reset_button = QPushButton(self)
        self.reset_button.setText("Reset")
        self.buttons_grid.addWidget(self.reset_button, 0, 0, alignment=Qt.AlignRight)
        self.reset_button.clicked.connect(
            lambda: self.reset_configuration()
        )

    def load_default_slider_values(self) -> None:
        if self.toggled:
            try:
                (
                    temp_pos,
                    tint_pos,
                    contrast_pos,
                    hue_pos,
                    sat_pos,
                    brightness_pos,
                    sharpening,
                    linear,
                    curve,
                    fformat,
                ) = self._camera.get_slider_values()
            except ValueError as e:
                print(e)
                temp_pos = 6503
                tint_pos = 1000
                contrast_pos = 0
                hue_pos = 0
                sat_pos = 128
                brightness_pos = 16
                sharpening = 500
            if fformat is not None:
                if fformat == 'jpeg': self.fformat_dropdown.setCurrentIndex(0)
                elif fformat == 'tiff': self.fformat_dropdown.setCurrentIndex(1)
                elif fformat == 'png': self.fformat_dropdown.setCurrentIndex(2)
                else: self.fformat_dropdown.setCurrentIndex(0)
            if temp_pos is not None: self.temp_slider.set_value(temp_pos)
            if tint_pos is not None: self.tint_slider.set_value(tint_pos)
            if contrast_pos is not None: self.contrast_slider.set_value(contrast_pos)
            if hue_pos is not None: self.hue_slider.set_value(hue_pos)
            if sat_pos is not None: self.saturation_slider.set_value(sat_pos)
            if brightness_pos is not None: self.brightness_slider.set_value(brightness_pos)
            if sharpening is not None: self.sharpening_slider.set_value(sharpening)
            if linear is not None:
                if linear == 1: self.linear_cb.setChecked(True)
                else: self.linear_cb.setChecked(False)
            if curve is not None:
                if curve == 'Off': self.curve_dropdown.setCurrentIndex(0)
                elif curve == 'Polynomial': self.curve_dropdown.setCurrentIndex(1)
                elif curve == 'Logarithmic': self.curve_dropdown.setCurrentIndex(2)
                else: self.curve_dropdown.setCurrentIndex(0)

    def update_fformat_value(self, value: int):
        if not self.toggled: return
        if value is not None: self._camera.set_camera_image_settings(fformat=('jpeg', 'tiff', 'png')[value])
    def update_temp_value(self, value: int):
        if not self.toggled: return
        if value is not None: self._camera.set_camera_image_settings(temp=value)
    def update_tint_value(self, value: int):
        if not self.toggled: return
        if value is not None: self._camera.set_camera_image_settings(tint=value)
    def update_contrast_value(self, value: int):
        if not self.toggled: return
        if value is not None: self._camera.set_camera_image_settings(contrast=value)
    def update_hue_value(self, value: int):
        if not self.toggled: return
        if value is not None: self._camera.set_camera_image_settings(hue=value)
    def update_saturation_value(self, value: int):
        if not self.toggled: return
        if value is not None: self._camera.set_camera_image_settings(saturation=value)
    def update_brightness_value(self, value: int):
        if not self.toggled: return
        if value is not None: self._camera.set_camera_image_settings(brightness=value)
    def update_sharpening_value(self, value: int):
        if not self.toggled: return
        if value is not None: self._camera.set_camera_image_settings(sharpening=value)
    def update_linear_value(self, value: int):
        if not self.toggled: return
        if self.linear_cb.isChecked(): self._camera.set_camera_image_settings(linear=1)
        if not self.linear_cb.isChecked(): self._camera.set_camera_image_settings(linear=0)

    def update_curve_value(self, value: int):
        if not self.toggled: return
        if value is not None: self._camera.set_camera_image_settings(curve=('Off', 'Polynomial', 'Logarithmic')[value])

    def save_configuration(self) -> None: self._camera.save_camera_settings()

    def reset_configuration(self) -> None:
        self._camera.reset_camera_image_settings()
        self._camera.load_camera_image_settings()
        self._camera.set_camera_image_settings()
        self.load_default_slider_values()

class FileFormatComboBox(QWidget):

    def __init__(self, callback) -> None:
        super(FileFormatComboBox, self).__init__(None)
        self.callback = callback

        layout = QHBoxLayout()
        self.box = QComboBox()
        self.box.addItems(('png', 'jpg'))
        self.box.currentIndexChanged.connect(self.callback)
        layout.addWidget(self.box)
        self.setLayout(layout)
    
    def get_contents(self, idx: int):
        return self.box.itemData(idx)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        win = GUI()
        # win.show() TODO: Check this
        sys.exit(app.exec_())
    except CriticalIOError as e:
        QMessageBox.critical(None, "Error encountered", e.msg, QMessageBox.Ok)