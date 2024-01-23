from camera import Camera, CustomIOError
from PyQt5.QtWidgets import QMessageBox, QWidget
import serial.tools.list_ports
import serial
import time
import threading
import os

# class CustomIOError(IOError):
#     def __init__(self, message: str):
#         self.msg = message

class Arduino:
    def __init__(self) -> None:
        """
        @brief  Starts Arduino class.
        """

        self.port = None
        self.arduino = None
        self.IS_CONNECTED = False
        self.error_box = QWidget()
        try:
            self.IS_CONNECTED = self.connect_to_arduino()
        except Exception as e:
            QMessageBox.critical(self.error_box, "Error Encountered",
                                e.msg, QMessageBox.Ok)


    def connect_to_arduino(self):
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
                raise CustomIOError("Arduino not connected")
            
        except Exception as e:
            print("ERROR Could not connect to arduino:")
            raise
            # print("  ", e)
            return False

        return True

    def write_to_arduino(self, char):
        """
        @brief  Writes to the arduino via serial.
        @param char     Character to send to arduino to trigger functions.
        """
        if self.IS_CONNECTED:
            self.arduino.write(bytes(char,  'utf-8'))


    def turn_motor_left(self):
        """
        @brief  Sends command to arduino to turn the motor left by 3 revolutions. Blocking.
        """
        if self.IS_CONNECTED:
            self.arduino.write(bytes('L',  'utf-8'))
            self.arduino.write(bytes('R',  'utf-8'))
            time.sleep(2)  # Waits for motor to finish. TODO: get response back instead


    def zero_platform(self):
        """
        @brief  Sends command to arduino to turn the motor until the limit switch is hit.
        """
        if self.IS_CONNECTED:
            self.arduino.write(bytes('Z',  'utf-8'))
            
            while(self.arduino.readline != 'Zeroed'): 
                pass


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

    def change_active_status(self, value: bool) -> None:
        self._status = value

    def is_active(self) -> bool: return self._status

    def status_changed(self) -> bool:
        if self._status != self._last_status: return True
        else: return False
    
    def sync_status(self) -> None: self._last_status = self._status

    def set_capture_location(self, file_path: str): 


        # Check if the folder exists
        if not os.path.exists(self.capture_dir):
            os.makedirs(self.capture_dir) # If it does not exist, create it

    def run_in_thread(function):
        """
        @brief  Wrap function in a thread.
        @param function     Function to put in thread.
        """
        def wrapper(*args):
            thread = threading.Thread(target=function, args=args)
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
        print("Started Automation")

        self.change_active_status(True)

        motor_shifts_needed = int(core_length * 10  / (shift_length))
        print(f"    Shifting {motor_shifts_needed} time(s) by  {shift_length} mm")

        for self.counter in range(motor_shifts_needed):
            if not self.is_active(): break
            print(self.counter)
            self.get_picture()
            time.sleep(3)
            if not self.is_active(): break
            self.shift_sample(shift_length)
        self.change_active_status(False)


    def get_picture(self):
        """
        @brief    Gets and Stores the image from the camera
        """
        folder_path = 'captures'
        # Check if the folder exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path) # If it does not exist, create it
        img = self.camera.get_image()
        if img is not None:
            img.save(f'{folder_path}/image_{self.counter}.jpg')


    def shift_sample(self, shift_length):
        """
        @brief  Rotates motor to shift sample. Rotates by 3mm each shift
        @param shift_length   Length to shift motor each turn (in cm).
        """

        # TODO - add in shift length logic
        self.arduino.turn_motor_left()
        print("Shifted Sample")
        time.sleep(2)

    @run_in_thread
    def zero_platform(self):
        """
        @brief   Zeros the platform to the left.  Non-blocking.
        """

        self.arduino.zero_platform()
        print("Zeroed Sample")












