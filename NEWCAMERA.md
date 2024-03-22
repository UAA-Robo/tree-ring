Since the still image capture is different, the following modifications must be made to the
class system:
1. Place a method, `take_still_image()` in Camera, figure out was `hResolutionIndex` is
2. Make automationScript call this method instead of getting an image from the camera and saving
it
3. Make the Camera class save the image (so must pass path at some point and have a default)