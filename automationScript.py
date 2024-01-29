from camera import Camera, CriticalIOError
from PyQt5.QtWidgets import QMessageBox, QWidget
import serial.tools.list_ports
import serial
from datetime import datetime
import time
import threading
import os

class Arduino:
    def __init__(self) -> None:
        """
        @brief  Starts Arduino class.
        """

        self.port = None
        self.arduino = None
        self.IS_CONNECTED = False
        self.error_box = QWidget()

        self.SHIFT_LENGTH_CHANGE = 0.1  # Increment to change shift length (mm) 

        try:
            self.IS_CONNECTED = self.connect_to_arduino()
        except Exception as e:
            QMessageBox.critical(self.error_box, "Error Encountered",
                                e.msg, QMessageBox.Ok)


    def connect_to_arduino(self) -> None:
        """
        @brief  Connects to arduino port.
        """
        try:
            for p in list(serial.tools.list_ports.comports()):
                if "CH340" in p.description:
                    self.port = p.device
                    break
        
            self.arduino = serial.Serial(port=self.port,  baudrate=9600, timeout=.1)
            if not self.arduino.is_open:
                # raise CriticalIOError("Arduino not connected")
                ...
            
        except Exception as e:
            print("ERROR Could not connect to arduino:")
            raise
            return False

        return True

    def write_to_arduino(self, char) -> None:
        """
        @brief  Writes to the arduino via serial.
        @param char     Character to send to arduino to trigger functions.
        """
        if self.IS_CONNECTED:
            self.arduino.write(bytes(char,  'utf-8'))


    def turn_motor_left(self) -> None:
        """
        @brief  Sends command to arduino to turn the motor left by 3 revolutions. Blocking.
        """
        if self.IS_CONNECTED:
            self.arduino.write(bytes('L',  'utf-8'))
            self.arduino.write(bytes('R',  'utf-8'))
            # time.sleep(2)
            while(self.arduino.readline() != 'AntiClockwise'): 
                pass


    def zero_platform(self) -> None:
        """
        @brief  Sends command to arduino to turn the motor until the limit switch is hit.
        """
        if self.IS_CONNECTED:
            self.arduino.write(bytes('Z',  'utf-8'))
            
            while(self.arduino.readline() != 'Zeroed'): 
                pass
    
    def update_shift_length(self, shift_length: float) -> None:
        """
        @brief  Sends command to arduino to update shift length.
        @param  shift_length Length in mm to shift sample each time.
        """
        if self.IS_CONNECTED:
            current_shift_length = float(self.arduino.readline())

            increments = (current_shift_length - shift_length) / self.SHIFT_LENGTH_CHANGE

            if increments < 0:
                for _ in range(abs(increments)):
                    # Decrements by SHIFT_LENGTH_CHANGE each time
                    self.arduino.write(bytes('-',  'utf-8'))
                    time.sleep(0.001)
            else:
                for _ in range(increments):
                    # Increments by SHIFT_LENGTH_CHANGE each time
                    self.arduino.write(bytes('+',  'utf-8'))
                    time.sleep(0.001)



class Automation():

    def __init__(self, camera: Camera) -> None:
        """
        @brief  Starts the automation class.
        @param camera   Instance of type Camera
        """

        self.camera = camera
        self.arduino = Arduino()
        self.counter = 0
        self.capture_dir = 'captures'
        self._status = False
        self._last_status = False
        self._status_message = ""
        self.IS_PAUSED = False

    def change_status(self, value: bool) -> None:
        """
        @brief  Sets automation status.
        @param value  True/False status to set.
        """
        self._status = value

    def is_active(self) -> bool: 
        """
        @brief  Gets automation status.
        """
        return self._status

    def status_changed(self) -> bool:
        """
        @brief  Updates automation status.
        """
        if self._status != self._last_status: return True
        else: return False
    
    def sync_status(self) -> None: 
        """
        @brief  Updates sync status.
        """
        self._last_status = self._status

    def get_automation_status(self) -> None:
        """
        @brief  Gets automation status message
        @return Return status as string
        """
        return self._status_message

    def set_capture_location(self, file_path: str) -> None: 
        """
        @brief Sets capture location.
        @param file_path Path to set as capture location.
        """

        self.capture_dir = file_path

    def check_capture_location(self) -> None:
        """
        @brief Checks the capture location and creates a folder if it does not exist.
        """
        if not os.path.exists(self.capture_dir):
            os.makedirs(self.capture_dir) # If it does not exist, create it

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


    @run_in_thread
    def start_automation(self, core_length, shift_length):
        """
        @brief Starts the automation process. Non-blocking,
        @param core_length    Core size (in mm).
        @param shift_length   Length to shift motor each turn (in cm).
        """

        self._status_message = "Automation Started..."

        self.change_status(True)

        motor_shifts_needed = int(core_length * 10  / (shift_length))

        for self.counter in range(motor_shifts_needed):
            self._status_message = f"Automation Started...  Shifting {self.counter} / {motor_shifts_needed} time(s) by  {shift_length} mm"
            while (self.IS_PAUSED):
                if not self.is_active(): break
            if not self.is_active(): break
            self.get_picture()
            time.sleep(3)
            while (self.IS_PAUSED):
                if not self.is_active(): break
            if not self.is_active(): break
            self.shift_sample(shift_length)
        self.change_status(False)
        self._status_message = "Automation Stopped."


    def get_picture(self):
        """
        @brief    Gets and Stores the image from the camera
        """
        self.check_capture_location()
        img = self.camera.get_image()

        current_time = datetime.now().strftime("%d-%m-%y_%H:%M:%S")
        if img is not None:
            img.save(f'{self.capture_dir}/image_{current_time}.jpg')


    def shift_sample(self, shift_length):
        """
        @brief  Rotates motor to shift sample. Rotates by 3mm each shift
        @param shift_length   Length to shift motor each turn (in cm).
        """

        self.arduino.update_shift_length(shift_length)
        self.arduino.turn_motor_left()
        time.sleep(2)

    @run_in_thread
    def zero_platform(self):
        """
        @brief   Zeros the platform to the left.  Non-blocking.
        """
        self._status_message = "Zeroing Platform..."
        self.arduino.zero_platform()
        self._status_message = "Finished Zeroing Platform."












