# Tree Ring Imaging Machine (TRIM)

Documentation can be viewed at [uaa-robo.github.io/tree-ring](https://uaa-robo.github.io/tree-ring/) and in the docs folder.

This code controls the Amscope camera (our model is the MU500 and MU1000).

The following files are taken from the SDK provided by AmScope [here](https://amscope.com/pages/software-downloads) when you select your camera and model:
* amcam.py - this file provides an API for the camera. For more information about the API, see [API.pdf](API.pdf).
* simplest.py - this file provides a simple example that opens the camera and grabs frames from the camera, though it does not display these frames.
* qt.py - this file provides an example that grabs frames from the camera and renders them in a GUI.
* libamacam.dylib - needed for mac
* win/ - contains drivers and dlls needed for windows

We created the following files:
* camera.py - Interfaces with images from the amcam or the webcam if no amcam is present.
* gui.py - Displays a gui that the user can use to run the automation script. Displays camera feed.
* automationScript.py -  Script that rotates the motor to shift the platform and trigger the camera to take pctures.


## Setup & Running
For setup, run `python -m pip install -r requirements.txt` to install the python requirements needed.

To execute this program run `python gui.py` in this directory.

## Bundle program into an executable for Windows
To compile this program, double-click on the `build.bat` script. An executable will be generated
in the dist folder.

Note: When building the program in "windowed" mode or "noconsole", Windows thinks its a virus. Building
it with the console window attached when running prevents that from happening.

<!-- Old instructions -->
<!-- To compile this program go open the terminal in the directory of gui.py and run `python -m PyInstaller gui.py --onefile --windowed`. This will not work on Mac due to strict camera permission.

When building the program into a binary, Windows will throw a 'severe' threat warning. This is
because the software lacks an official Microsoft signature. To bypass this, open Windows Security,
click on 'Virus & threat protection,' and click on the link 'Manage settings' under 'Virus & threat
protection settings.' At the bottom of this menu there is a link to 'Add or remove exclusions.'
Add an exclusion of the type 'Folder,' and select the directory containing the program. Now running
the above command will successfully build the executable. -->
