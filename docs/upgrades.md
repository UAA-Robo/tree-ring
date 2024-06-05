# Upgrade Instructions
This guide provides easy-to-follow instructions on upgrading components of the TRIM software
solution.

## Camera
TRIM was originally designed for AmScope cameras, and so it utilizes the AmScope SDK. This means that AmScope cameras are preferred. As a backup, TRIM also supports cameras covered by the OpenCV library, but the advanced features are not supported for these cameras and they will take images at their default resolutions. It recommended to stay within the AmScope family, __.

The SDK used is specific to the camera, however. This means that it is necessary to install a new SDK on a new camera upgrade. These are the steps to upgrade the camera:

1. The new camera comes with a USB flash drive containing drivers. It also contains an up-to-date SDK that supports the new camera.
    - Plug the flash drive in and open the folder. First install the drivers. This can be done by either executing the `AmScopeMicroDshowSetup.exe` in the SDK folder, or installing the drivers manually (located in SDK/amcamsdk.20231217.zip/win/drivers/). The former method also installs the official AmScope software.
2. After installing the drivers, open a new window to the tree-ring source code folder.
3. Remove (keep somewhere else in case) the following files: `amcam.py`, `amcam.dll`, and `libamcam.dylib`.
4. Open up SDK/amcamsdk.20231217.zip and unzip it. Inside this directory, copy the following files into the root folder of the tree-ring source code folder:
    - `python/amcam.py`
    - `win/x64/amcam.dll`
    - `mac/x64+arm64/libamcam.dylib`

That should be it! The camera should be detected by the software now.