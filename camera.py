import io
import sys, amcam, time, enum
from PyQt5.QtGui import QImage
from PIL import Image
import cv2
import threading

# Code borrowed from https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv

class camera_type(enum.Enum):
    UNKNOWN = 0
    MICROSCOPE = 1
    WEBCAM = 2

class Camera:
    def __init__(self) -> None:
        """
        @brief    Camera class that runs the camera operations and modifies camera settings

        @throws IOError    Throws an IOError if no camera can be opened.
        """
        self._hcam = None
        self._buffer = None
        self._width = 0 # Video width
        self._height = 0 # Video height
        self._cam_name = ''
        self._image = None
        self._cam_type = camera_type.UNKNOWN
        available_cameras = amcam.Amcam.EnumV2()
        if len(available_cameras) <= 0:
            # raise IOError #TODO: Eventually
            print("No microscope found, defaulting to webcam...")
            self._cam_type = camera_type.WEBCAM
            self._cam_name = 'Webcam'
            starttime = time.time()
            self._hcam = cv2.VideoCapture(0)
            print(f"Webcam took {(time.time() - starttime):.2f} seconds to open.")

        else:
            self._cam_name = available_cameras[0].displayname
            self._cam_type = camera_type.MICROSCOPE
            try:
                self._hcam = amcam.Amcam.Open(available_cameras[0].id)
            except amcam.HRESULTException as e: print(e)
            else:
                self._width, self._height = self._hcam.get_Size()
                buffer_size = ((self._width * 24 + 31) // 32 * 4) * self._height
                self._buffer = bytes(buffer_size)
                try:
                    if sys.platform == 'win32':
                        self._hcam.put_Option(amcam.AMCAM_OPTION_BYTEORDER, 0) # QImage.Format_RGB888
                        
                except amcam.HRESULTException as e: print(e)
        
        self.connect_stream()
    
    def connect_stream(self):
        """
        @brief    Starts the camera's stream.
        """
        if self._cam_type == camera_type.MICROSCOPE:
            try:
                self._hcam.StartPullModeWithCallback(self.camera_callback, self)
                
            except amcam.HRESULTException as e: print(e)

        elif self._cam_type == camera_type.WEBCAM:
            def run_stream(_self: 'Camera'):
                while(True):
                    _self.stream()
                    time.sleep(0.001)

            th = threading.Thread(target=run_stream, args=[self], daemon=True)
            th.start()
    
    @staticmethod
    def camera_callback(event, _self: 'Camera'):
        if event == amcam.AMCAM_EVENT_IMAGE:
            _self.stream()
        
    def name(self): return self._cam_name

    def type(self): return self._cam_type

    def stream(self) -> None:
        """
        @brief    Streams the image received by the camera in real time.
        
        @throws IOError    Throws an IOError if no camera could be opened.
        """

        # Use Microscope camera
        if self._hcam and self._cam_type == camera_type.MICROSCOPE:
            try:
                self._hcam.PullImageV2(self._buffer, 24, None)
            except amcam.HRESULTException as e: print(e)
            else:
                self._image = QImage(self._buffer, self._width, self._height, (self._width * 24 + 31) // 32 * 4, QImage.Format_RGB888)

            
        # Use webcam
        elif self._hcam and self._cam_type == camera_type.WEBCAM:
            success, frame = self._hcam.read()
            if success:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                self._image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)

        else:
            raise IOError("No camera opened to stream from.")

    def get_image(self) -> QImage:
        """
        @brief    Takes an image from the camera to store.

        @return    Returns a QImage from the camera.
        """
        return self._image

    def close(self):
        """
        @brief    Closes the camera.
        """
        if self._hcam is not None and self._cam_type == camera_type.MICROSCOPE:
            self._hcam.Close() # Amcam camera close method
        elif self._hcam is not None and self._cam_type == camera_type.WEBCAM:
            self._hcam.release() # cv2 VideoCapture close method
        self._hcam = None
        
# Driver test code
# try:
#     my_camera = Camera()
#     my_camera.set_save_path()
# except IOError as e: print(e)
# else:
#     # while True:
#     #     my_camera.take_picture()
#     #     time.sleep(0.5)
#     my_camera.take_picture()