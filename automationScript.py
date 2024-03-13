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

        self._port = None
        self._arduino = None
        self._IS_CONNECTED = False
        self._error_box = QWidget()

        self._SHIFT_LENGTH_CHANGE = 0.1  # Increment to change shift length (mm) 

        try:
            self._IS_CONNECTED = self.connect_to_arduino()
        except Exception as e:
            QMessageBox.critical(self._error_box, "Error Encountered",
                                e.msg, QMessageBox.Ok)


    def connect_to_arduino(self) -> None:
        """
        @brief  Connects to arduino port.
        """
        try:
            for p in list(serial.tools.list_ports.comports()):
                if "CH340" in p.description:
                    self._port = p.device
                    break
        
            self._arduino = serial.Serial(port=self._port,  baudrate=9600, timeout=.1)
            if not self._arduino.is_open:
                raise CriticalIOError("Arduino not connected")
                return False
            
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
        if self._IS_CONNECTED:
            self._arduino.write(bytes(char,  'utf-8'))


    def shift_right(self) -> None:
        """
        @brief  Sends command to arduino turn the motor left to shift the platform right by the shift 
                length. Blocking.
        """
        if self._IS_CONNECTED:
            self._arduino.write(bytes('L',  'utf-8'))
            self._arduino.write(bytes('R',  'utf-8'))
            time.sleep(1)

            # while(self.arduino.readline() != 'AntiClockwise'): 
            #     pass
    
    def update_shift_length(self, shift_length: float) -> None:
        """
        @brief  Sends command to arduino to update shift length.
        @param  shift_length Length in mm to shift sample each time.
        """
        if self._IS_CONNECTED:

            current_shift_length = 3  # TODO: ask arduino for length

            increments = current_shift_length - int(shift_length)

            if increments < 0:
                for _ in range(abs(increments)):
                    # Decrements by _SHIFT_LENGTH_CHANGE each time
                    self._arduino.write(bytes('-',  'utf-8'))
                    print("-")
                    time.sleep(0.001)
            else:
                for _ in range(increments):
                    # Increments by _SHIFT_LENGTH_CHANGE each time
                    self._arduino.write(bytes('+',  'utf-8'))
                    print("+")
                    time.sleep(0.001)



class Automation():

    def __init__(self, camera: Camera) -> None:
        """
        @brief  Starts the automation class.
        @param camera   Instance of type Camera
        """

        self._camera = camera
        self._arduino = Arduino()
        self._counter = 0
        self._capture_dir = "tree_core"
        self._status = False
        self._last_status = False
        self._status_message = ""
        self._stored_status_message = None
        self._IS_PAUSED = False

    def change_status(self, value: bool) -> None:
        """
        @brief  Sets automation status.
        @param value  True/False status to set.
        """
        self._status = value

    def is_active(self) -> bool: 
        """
        @brief  Gets automation status.
        @return True if the automation script is active, false otherwise.
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

    def is_paused(self) -> bool:
        """
        @brief Gets automation pause status.
        @return True if the automation script is paused, false otherwise.
        """
        return self._IS_PAUSED

    def set_pause(self, value: bool) -> None:
        """
        @brief Sets whether the Automation scripts is paused.
        """
        self._IS_PAUSED = value
        if value and self.is_active():
            self._stored_status_message = self._status_message
            self._status_message = "Automation paused..."
        elif self.is_active():
            self._status_message = self._stored_status_message

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

        self._capture_dir = file_path
        self.check_capture_location()

    def check_capture_location(self) -> None:
        """
        @brief Checks the capture location and creates a folder if it does not exist.
        """
        if not os.path.exists(self._capture_dir):
            os.makedirs(self._capture_dir) # If it does not exist, create it

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
    def start_automation(self, image_name:str, core_length:float, shift_length:float):
        """
        @brief Starts the automation process. Non-blocking,
        @param image_name   Name to Save Image under (with image count added).
        @param core_length  Core size (in mm).
        @param shift_length Length to shift motor each turn (in cm).
        """

        self._status_message = "Automation Started..."

        self.change_status(True)

        motor_shifts_needed = int(core_length * 10  / (shift_length))
        self._arduino.update_shift_length(shift_length)

        self._counter = 0
        for self._counter in range(motor_shifts_needed):
            self._status_message = f"Automation Started...  Shifting {self._counter} / {motor_shifts_needed} time(s) by  {shift_length} mm"
            while (self._IS_PAUSED and self.is_active()): pass
            if not self.is_active(): break

            self.get_picture(image_name)

            while (self._IS_PAUSED and self.is_active()): pass
            if not self.is_active(): break
            self.shift_sample()
            time.sleep(1.5)
        
        time.sleep(1.5)
        self.get_picture(image_name)

        self.change_status(False)
        self._status_message = "Automation Stopped."


    def get_picture(self, image_name:str):
        """
        @brief    Gets and Stores the image from the camera
        """
        self.check_capture_location()
        img = self._camera.get_image()

        image_number = str(self._counter).zfill(3) # Add 0s in front so 3 digits long
        if img is not None:
            img.save(f'{self._capture_dir}/{image_name}_{image_number}.jpg')


    def shift_sample(self):
        """
        @brief  Rotates motor to shift sample. Rotates by 3mm each shift
        @param shift_length   Length to shift motor each turn (in cm).
        """
        self._arduino.shift_right()













