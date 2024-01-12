from camera import Camera

# Code borrowed from https://python.hotexamples.com/examples/PyQt5.Qt/QImage/save/python-qimage-save-method-examples.html

class Automation:
    def __init__(self, camera: Camera) -> None:
        self.camera = camera

    def start_automation(self):
        """
        @brief    Starts the automation process.
        """
        print("Started Automation")
        self.get_picture()
        self.shift_sample()
        return
    
    def get_picture(self):
        """
        @brief    Gets and Stores the image from the camera
        """
        img = self.camera.image()
        img.save('image.jpg')
        # img.save("image.jpg")


    def shift_sample(self):
        """
        @brief    Calls Arduino to turn motor
        """
        return
    

if __name__ == "__main__":
    Automation = Automation()
    Automation.start_automation()