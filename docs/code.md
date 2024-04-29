# Code Explanations
Refer to the comments in our code in our github for more in-depth explanations of each function. Below iss an overview.


## GUI 
* gui.py
The GUI class contains all the logic for displaying the user interface. It has a callback to Camera to display the camera video stream to the user. The GUI will display any warnings or errors that show up as popups.The user can enter the following information:
* **Image/Core name**: This is used to name the images when saving, with a prepended image number. For example if `core_alpha` is entered, the images would be named `core_alpha_1.jpg`, `core_alpha_2.jpg`, etc
* **Core Length (cm)**: This is the length of the core in cm.
* **Shift Length (mm)**: This is the length to shift the core sample after taking a picture.


Then the user can start the automation program  in the Automation class. On Windows, the user will be prompted to select a folder to save the images to (on Mac, images will save to a `tree-ring` desktop folder). After selection, the automation immediately starts. If there is a camera connected but no arduino connected, the automation program will take pictures without sending signals to the arduino to move the motor. The user can stop the program at any time (a pause button is in the works of being implemented).

TODO: ADD picture of GUI

### Camera Options

Pressing the **Advanced Camera Options** button will open a new window that allows the user to adjust camera video and save options. Pressing **Save** will save them to a file called `camera_configuration.yaml` in the directory where the program is located. By default, the program loads the settings from this file on startup. Pressing **Reset** will reset any changes back to this file, or if it is missing, the defaults. The default settings are not optimal, so if the original configuration file is lost, go to [this link](troubleshooting/optimal_settings.md) to get the original file.

## Automation 
* automationScript.py

The Automation class contains all the code for automating the tree ring process. It references the Camera class (in camera.py) to save images and the Arduino class (in the same file) to send signals to the arduino to connect and rotate the motor. The primary method of this class is start_automation. It calculates the number of times to move the tree ring based on the length input. Then it moves the platform that many times by that length, taking and saving a picture before each shift. 

The Arduino Class is a wrapper for the commands sent to the Arduino. The Arduino defaults to a shift length of 3mm and the following commands are Currently the following high level methods are implemented:
* `connect_to_arduino` - Attempts to connect to the arduino.
* `update_shift_length` - Updates the shift length that the arduino spins the motor (defaults to 3mm).
* `shift_right` - Spins the motor left to shift the platform RIGHT by the shift length.

## Camera 
* camera.py
* amcam.py (Amcam API)
* amcam.dll, libamcam.dylib (compiled C code used by amcam.py)
* /win (windows drivers)


The Camera class holds all properties for the camera and wraps all interactions with it. When the program begins and initializes the Camera, a callback method is loaded into the Amcam API. The Amcam API controls the camera, and by manipulating the contents of this callback method, we can choose to act on the events being sent from the camera (in this case we use `AMCAM_EVENT_IMAGE` and `AMCAM_EVENT_STILLIMAGE). The microscope image quality is left as default in all settings but the saturation, which is adjusted to around 37.6% of its range (96 / 255).

### Using the Microscope Camera
The Amcam camera starts its own thread, seen by `StartPullModeWithCallback()` in `connect_stream`, and runs the callback method first loaded in the init method. From then on, the camera runs asynchronously to the main thread, calling the static method, `camera_callback`. This callback pulls the camera's image into a byte array, converts it to a QImage, and saves it in the class for extraction by the program later. When an image is taken, the camera pauses the preview to take a still image (a full-resolution picture). The callback waits for a signal from the camera that it is done before saving the image to the specified directory.

### No Microscope Camera
If the microscope camera could not be loaded in the first place, the **cv2** library is used to load the next available camera (called `WEBCAM` in the camera type). In this case the Amcam API is not running its own thread, so instead of using the callback method, `connect_stream` starts a new thread for streaming from this camera, paralleling the Amcam API's behavior.



## Arduino 
* arduino/tree-ring/tree-ring.ino

The tree-ring.ino file holds the entirety of the code on the arduino. When powered on the arduino first runs the `setup()` function and once that is complete it will immediately start the `loop()` function. From there the arduino waits for a signal from the computer to start doing any actions.

Arguments that can be passed to Arduino  
`H`  Make Motor Turn Clockwise  
`L`  Make Motor Turn CounterClockwise  
`R`  Move Motor 1 Increment  
`+`  Increase Motor Turn Length by 1/10  
`-`  Decrease Motor Turn Length by 1/10  
`=`  Get Motor Turn Length  

