from camera import Camera
import serial.tools.list_ports
import serial
import time
import threading

# Code borrowed from https://python.hotexamples.com/examples/PyQt5.Qt/QImage/save/python-qimage-save-method-examples.html

class Automation:
    def __init__(self, camera: Camera) -> None:
        self.camera = camera
        
        self.port = ""
        # Connect to arduino
        for p in list(serial.tools.list_ports.comports()):
            if "CH340" in p.description:
                self.port = p.device
                break
        self.counter = 0

        self.arduino = serial.Serial(port=self.port,  baudrate=9600, timeout=.1)
    

    def start_automation(self):
        """
        @brief    Starts the automation process.
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



    def write_to_arduino(self, x):
            self.arduino.write(bytes(x,  'utf-8'))
            time.sleep(2)
            data = self.arduino.readline()
            return  data

    def shift_sample(self):
        """
        @brief    Calls Arduino to turn motor
        """
        self.arduino.write(bytes('L',  'utf-8'))
        self.arduino.write(bytes('R',  'utf-8'))
        print("Shifted Sample")
        time.sleep(2)

    def zero_platform(self):
        """
        @brief   Zeros the platform to the left
        """

        def run(_self: 'Automation'):
            _self.arduino.write(bytes('Z',  'utf-8'))
            
            while( _self.arduino.readline != 'Zeroed'): pass
            print("Zeroed Sample")
        

        th = threading.Thread(target=run, args=[self], daemon=True)
        th.start()



    

if __name__ == "__main__":
    Automation = Automation()
    Automation.start_automation()










