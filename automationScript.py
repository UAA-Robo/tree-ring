from camera import Camera
import serial.tools.list_ports
import serial
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
        self.IS_CONNECTED = self.connect_to_arduino()


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
                raise
            
        except:
            print("ERROR Could not connect to arduino!")
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
        @param shift_length   Length to shift motor each turn (in mm).
        """
        print("Started Automation")

        motor_shifts_needed = int(core_length / shift_length)
        print(f"    Shifting {motor_shifts_needed} times by  {shift_length} mm")

        for self.counter in range(motor_shifts_needed):
            self.get_picture()
            time.sleep(3)
            self.shift_sample(shift_length)


    def get_picture(self):
        """
        @brief    Gets and Stores the image from the camera
        """
        folder_path = 'captures'
        # Check if the folder exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path) # If it does not exist, create it

        img = self.camera.get_image()
        img.save(f'{folder_path}/image_{self.counter}.jpg')


    def shift_sample(self, shift_length):
        """
        @brief  Rotates motor to shift sample. Rotates by 3mm each shift
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


if __name__ == "__main__":
    Automation = Automation()
    Automation.start_automation()










