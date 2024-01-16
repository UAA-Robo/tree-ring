from camera import Camera
import serial.tools.list_ports
import serial
import time
import threading


class Arduino:
    def __init__(self) -> None:
        """
        @brief  Starts Arduino class.
        """

        self.port = None
        self.arduino = None
        self.connect_to_arduino()


    def connect_to_arduino(self):
        """
        @brief  Connects to arduino port.
        """
        for p in list(serial.tools.list_ports.comports()):
            if "CH340" in p.description:
                self.port = p.device
                break

        self.arduino = serial.Serial(port=self.port,  baudrate=9600, timeout=.1)


    def write_to_arduino(self, char):
        """
        @brief  Writes to the arduino via serial.
        @param char     Character to send to arduino to trigger functions.
        """
        self.arduino.write(bytes(char,  'utf-8'))


    def turn_motor_left(self):
        """
        @brief  Sends command to arduino to turn the motor left by 3 revolutions. Blocking.
        """
        self.arduino.write(bytes('L',  'utf-8'))
        self.arduino.write(bytes('R',  'utf-8'))
        time.sleep(2)  # Waits for motor to finish. TODO: get response back instead


    def zero_platform(self):
        """
        @brief  Sends command to arduino to turn the motor until the limit switch is hit.
        """
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

    def run_in_thread(*args):
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
    def start_automation(self):
        """
        @brief    Starts the automation process. Non-blocking
        """
        print("Started Automation")

        for self.counter in range(10):
            self.get_picture()
            time.sleep(3)
            self.shift_sample()


    def get_picture(self):
        """
        @brief    Gets and Stores the image from the camera
        """
        img = self.camera.get_image()
        img.save(f'captures/image_{self.counter}.jpg')


    def shift_sample(self):
        """
        @brief  Rotates motor to shift sample.
        """
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










