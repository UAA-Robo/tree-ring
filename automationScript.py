class Automation:

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
        return

    def shift_sample(self):
        """
        @brief    Calls Arduino to turn motor
        """
        return
    

if __name__ == "__main__":
    Automation = Automation()
    Automation.start_automation()