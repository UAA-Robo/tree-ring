from camera import Camera
import serial.tools.list_ports
import serial
import time
import threading


class Arduino:
    def __init__(self,) -> None:

        self.port = None
        self.arduino = None
        self.connect_to_arduino()


    def connect_to_arduino(self):
        for p in list(serial.tools.list_ports.comports()):
            if "CH340" in p.description:
                self.port = p.device
                break
        self.counter = 0

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


class Automation:

    def __init__(self, camera: Camera) -> None:
        self.camera = camera
        self.arduino = Arduino()


    def start_automation(self):
        """
        @brief    Starts the automation process. Non-blocking.
        """
        print("Started Automation")

        def run(_self: 'Automation'):
            for _self.counter in range(10):
                _self.get_picture()
                _self.shift_sample()

        th = threading.Thread(target=run, args=[self], daemon=True)
        th.start()


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


    def zero_platform(self):
        """
        @brief   Zeros the platform to the left. Non-blocking.
        """

        def run(_self: 'Automation'):
            _self.arduino.zero_platform()
            print("Zeroed Sample")
        
        th = threading.Thread(target=run, args=[self], daemon=True)
        th.start()


if __name__ == "__main__":
    Automation = Automation()
    Automation.start_automation()










