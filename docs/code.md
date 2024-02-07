# Code Explanations
Refer to the comments in our code in our github for more in-depth explanations of each function. Below iss an overview.


## GUI 
* gui.py
The GUI class contains all the logic for displaying the user interface. It has a callback to Camera to display the camera video stream to the user. The GUI will display any warnings or errors that show up as popups.The user can enter the following information:
* **Image/Core name**: This is used to name the images when saving, with a prepended image number. For example if `core_alpha` is entered, the images would be named `core_alpha_1.jpg`, `core_alpha_2.jpg`, etc.

* **Core Length (cm)**:

* **Shift Length (cm)**:




Then they can start the automation program  in the Automation class. On Windows, the user will be prompted to select a folder to save the images to (on Mac, images will save to a `tree-ring` desktop folder). After selection, the automation immediately starts. If there is a camera connected but no arduino connected, the automation program will take pictures without sending signals to the arduino to move the motor.

TODO: ADD picture of GUI

## Automation 
* automationScript.py

The Automation class contains all the code for automating the tree ring process. It references the Camera class (in camera.py) to save images and the Arduino class (in the same file) to send signals to the arduino to connect and rotate the motor. The primary method of this class is start_automation. It calculates the number of times to move the tree ring based on the inputed length 



## Camera 
* camera.py
* Amcam API (win drivers)

The Camera class holds all properties for the camera and wraps all interactions with it. When the program begins and initializes the Camera, a callback method is loaded into the Amcam API. The Amcam API controls the camera, and by manipulating the contents of this callback method, we can choose to act on the events being sent from the camera (in this case we use `AMCAM_EVENT_IMAGE`). The microscope image quality is left as default in all settings but the saturation, which is adjusted to around 37.6% of its range (96 / 255).

### Using the Microscope Camera
The Amcam camera starts its own thread, seen by `StartPullModeWithCallback()` in `connect_stream`, and runs the callback method first loaded in the init method. From then on, the camera runs asynchronously to the main thread, calling the static method, `camera_callback`. This callback pulls the camera's image into a byte array, converts it to a QImage, and saves it in the class for extraction by the program later.

### No Microscope Camera
If the microscope camera could not be loaded in the first place, the **cv2** library is used to load the next available camera (called `WEBCAM` in the camera type). In this case the Amcam API is not running its own thread, so instead of using the callback method, `connect_stream` starts a new thread for streaming from this camera, paralleling the Amcam API's behavior.



## Arduino 
    * arduino/tree-ring/tree-ring.ino


