# Code Explanations
Refer to the comments in our code in our github for more in-depth explanations of each function. Below iss an overview.


## GUI 
    * gui.py


## Camera 
* camera.py
* Amcam API (win drivers)

The Camera class holds all properties for the camera and wraps all interactions with it. When the program begins and initializes the Camera, a callback method is loaded into the Amcam API. The Amcam API controls the camera, and by manipulating the contents of this callback method, we can choose to act on the events being sent from the camera (in this case we use `AMCAM_EVENT_IMAGE`).

### Using the Microscope Camera
The Amcam camera starts its own thread, seen by `StartPullModeWithCallback()` in `connect_stream`, and runs the callback method first loaded in the init method. From then on, the camera runs asynchronously to the main thread, calling the static method, `camera_callback`. This callback pulls the camera's image into a byte array, converts it to a QImage, and saves it in the class for extraction by the program later.

### No Microscope Camera
If the microscope camera could not be loaded in the first place, the **cv2** library is used to load the next available camera (called `WEBCAM` in the camera type). In this case the Amcam API is not running its own thread, so instead of using the callback method, `connect_stream` starts a new thread for streaming from this camera, paralleling the Amcam API's behavior.

## Automation 
    * automationScript.py


## Arduino 
    * arduino/tree-ring/tree-ring.ino


