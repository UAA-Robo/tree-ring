import amcam
import enum, os, time
from pathlib import Path
import cv2
from PIL import Image

class camera_type(enum.Enum):
    UNKNOWN = 0
    MICROSCOPE = 1
    WEBCAM = 2

#-----------------------------------------------------------
# STILL TO DO:
#  - Store all images in a vector
#  - Test microscope camera
#  - Provide methods for retrieving current image for GUI
#-----------------------------------------------------------

class Camera:
    def __init__(self, file_extension: str='jpg') -> None:
        """
        Camera class for handling taking pictures and saving images. Be sure to set the save path
        before taking any pictures if you don't want to save to the current directory!

        :param file_extension: The type of image to save, defaults to 'jpg'.
        :raises IOError: Throws an IO exception if no camera can be opened.
        """
        self.file_ext = file_extension
        self.cam = None
        self.cam_name = None
        self.buffer = None
        self.cam_type = camera_type.UNKNOWN
        available_cameras = amcam.Amcam.EnumV2()
        if len(available_cameras) <= 0: # Use webcam
            start_time = time.time()
            self.cam = cv2.VideoCapture(0)
            time_elapsed = time.time() - start_time
            print("No microscope found, defaulting to webcam.")
            if not self.cam.isOpened(): raise IOError("Failed to open webcam")
            else:
                self.cam_type = camera_type.WEBCAM
                print(f"Webcam took {time_elapsed:.2f} seconds to open.")

        else: # Use microscope
            self.cam_name = available_cameras[0].displayname
            self.cam_type = camera_type.MICROSCOPE
            print(self.cam_name) #! Remove later
            try:
                self.cam = amcam.Amcam.Open(available_cameras[0].id) #TODO: <-- Check this
            except amcam.HRESULTException as e:
                print(e)
            else:
                self._w, self._h = self.cam.get_Size() #TODO: <-- Check this
                buffer_size = ((self._w * 24 + 31) // 32 * 4) * self._h #TODO: <-- Check this
                self.buffer = bytes(buffer_size) #TODO: <-- Check this
        
        self._current_image = None
        self._capture_dir = "captures"
        self._frame_count = 0

    def set_save_path(self, path=None):
        """
        Sets the file path to the capture directory for the camera.

        :param path: The absolute file path to the captures directory. If left blank, it
                     will default to saving images to a 'captures' folder in the current directory.
        """
        if path != None:
            if path[-1] == '/': self._capture_dir = path
            else: self._capture_dir = path + '/'
            Path(path).mkdir(exist_ok=True)
        elif path == None:
            os.chdir(os.path.dirname(os.path.abspath(__file__))) # <-- Sets current directory to file path origin
            Path(os.path.dirname(os.path.abspath(__file__))+\
                 '/'+self._capture_dir+'/').mkdir(exist_ok=True)
            self._capture_dir += '/'

    def num_frames(self): return self._frame_count

    def get_current_frame(self): return self._frame_count - 1

    def take_picture(self):
        """Takes a picture with the available camera and stores it."""
        self._frame_count += 1
        if self.cam_type == camera_type.MICROSCOPE:
            if not self.microscope_picture():
                print(f"Failed to take picture for frame {self.get_current_frame()}.")
        if self.cam_type == camera_type.WEBCAM:
            if not self.webcam_picture():
                print(f"Failed to take picture for frame {self.get_current_frame()}.")
        
        self._current_image = None

    def microscope_picture(self) -> bool: #TODO: Check this method with actual camera!!
        """
        Captures and stores a picture from the microscope.

        :returns: True on success, false otherwise.
        """
        try:
            self.cam.PullImageV2(self.buffer, 24, None) #TODO: <-- Check this
        except amcam.HRESULTException as e:
            print(e)
            return False
        else:
            try:
                img = Image.frombytes("L",(self._w, self._h), self.buffer, "L", 0, 1) #TODO: <-- Check this
                img.save(self._capture_dir + f'image_{self.get_current_frame()}.' + self.file_ext) #TODO: <-- Check this
            except OSError as e:
                print(e)
                return False
        return True

    def webcam_picture(self) -> bool:
        """
        Captures and stores a picture from the webcam.
        
        :returns: True on success, false otherwise.
        """
        success, frame = self.cam.read()
        if not success: return False
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        out = cv2.imwrite(self._capture_dir + f'image_{self.get_current_frame()}.' + self.file_ext,
                          frame)
        if not out: return False
        self._current_image = frame
        return True



# Driver test code
try:
    my_camera = Camera()
    my_camera.set_save_path()
except IOError as e: print(e)
else:
    while True:
        my_camera.take_picture()
        time.sleep(0.5)