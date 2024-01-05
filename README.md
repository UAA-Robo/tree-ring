This code controls the Amscope camera (our model is the MU500).

The following files are taken from the SDK provided by AmScope [here](https://amscope.com/pages/software-downloads) when you select your camera and model.

AmScope provides the following files in Python:
* amcam.py - this file provides an API for the camera. For more information about the API, see [API.pdf](API.pdf).
* simplest.py - this file provides a simple example that opens the camera and grabs frames from the camera, though it does not display these frames.
* qt.py - this file provides an example that grabs frames from the camera and renders them in a GUI.
* libamacam.dylib - needed for mac
* win/ - contains drivers needed for windows


TODO:
- QT application (gui.py):
    - Displays video
    - Lets you start/stop automation program
    - Select where to store photos?

- Wrapper for camera(s) (camera.py)?

- Automation program that (automationScript.py):
    1. Takes picture + stores it
    2. Calls arduino to shift motor
    3. Stops when hits limit switch?



