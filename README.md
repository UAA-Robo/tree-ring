# Tree Grabber Nabber

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
    - Stop automation program (maybe pause) -> Dawson (by 1/23)
    - Select where to store photos -> Dawson (by 1/23)
    - Adjust movement length -> Mya, Anthony (by 1/23)
    - Input core length  TO CM -> Mya (by 1/23)
    - Make pretty (Make image smaller, or app bigger)  -> Mya (by 1/23)
    - Error handleing -> Dawson
    - App downloading -> Mya

- Camera
    - Adjust exposure options

- Automation program (automationScript.py):
    - Automatic image stitching

- Arduino Code:
    - Zero unstutter  -> Anthony
    - Adjust limit switch so sample doesn't move when pressed  -> Anthony
    - merge readme and code into main

- Hardware:
    - Print camera mount -> Dawson (by 1/23)
    - start PCB -> Anthony (by 1/23)
    - Print Motor mount
    - Print limit switch mount

    - Get new hardware working -> Anthony (by 1/23)

- Documentation w/ docsify
    - Step by step instructions 
    - Code guide
    - Trouble Shooting (start by 1/23) -> Dawson

