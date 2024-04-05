import io
import sys, amcam, time, enum
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QMessageBox, QWidget
from PIL import Image
import cv2
import threading

# Code borrowed from https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv

class camera_type(enum.Enum):
    """Class for containing the different types of cameras the program may interact with."""
    UNKNOWN = 0
    MICROSCOPE = 1
    WEBCAM = 2

class CriticalIOError(IOError):
    """An IOError that should stop launch of the program."""
    def __init__(self, message: str) -> None:
        self.msg = message

class CriticalCameraError(CriticalIOError): pass

class WarningIOError(IOError):
    """An IOError that should pop up as a warning message."""
    def __init__(self, message: str) -> None:
        self.msg = message

class WarningCameraError(WarningIOError): pass

class Camera:
    def __init__(self) -> None:
        """
        @brief Camera class that runs the camera operations and modifies camera settings.
        """
        self._hcam = None
        self._buffer = None
        self._width = 0 # Video width
        self._height = 0 # Video height
        self._cam_name = ''
        self._image = None
        self._cam_type = camera_type.UNKNOWN
        # self.stream_enabled = True
        self._capture_dir = ""
        # self.error_box = QWidget()
        try:
            self.load_camera()
        except Exception as e:
            print(e)


    def is_microscope(self) -> bool:
        """
        @brief Used to determine if the camera loaded is the microscope camera.
        @return True if the camera is the microscope camera, false otherwise.
        """

        if self._cam_type == camera_type.MICROSCOPE: return True
        else: return False

    def load_camera(self) -> None:
        available_cameras = amcam.Amcam.EnumV2()
        if len(available_cameras) <= 0:
            # raise CriticalCameraError("Microscope camera not connected")
            print("No microscope found, defaulting to webcam...")
            self._cam_type = camera_type.WEBCAM
            self._cam_name = 'Webcam'
            starttime = time.time()
            self._hcam = cv2.VideoCapture(0)
            print(f"Webcam took {(time.time() - starttime):.2f} seconds to open.")
            # raise WarningCameraError("Microscope camera not connected, \ndefaulting to next camera")

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
                print("Number of still resolutions supported:",self._hcam.StillResolutionNumber())
                try:
                    if sys.platform == 'win32':
                        self._hcam.put_Option(amcam.AMCAM_OPTION_BYTEORDER, 0) # QImage.Format_RGB888
                         
                except amcam.HRESULTException as e: print(e)
        
        self.connect_stream()
    
    def connect_stream(self) -> None:
        """
        @brief Starts the camera's stream.
        """
        if self._cam_type == camera_type.MICROSCOPE:
            try:
                self.reset_camera_image_settings()
                self.set_camera_image_settings(saturation=0.3764705882352941) # Reduces yellow image quality
                self._hcam.StartPullModeWithCallback(self.camera_callback, self)
                self._hcam.put_Option(amcam.AMCAM_OPTION_SHARPENING, 500)
                # self._hcam.put_Option(amcam.AMCAM_OPTION_DENOISE, 100)
                self._hcam.put_Option(amcam.AMCAM_OPTION_LINEAR, 0)
                self._hcam.put_Option(amcam.AMCAM_OPTION_CURVE, 1)
                # self._hcam.put_Option(amcam.AMCAM_OPTION_DEMOSAIC, 2)

            except amcam.HRESULTException as e: print(e)

        elif self._cam_type == camera_type.WEBCAM:
            def run_stream(_self: 'Camera'):
                while(True):
                    _self.stream()
                    time.sleep(0.001)

            th = threading.Thread(target=run_stream, args=[self], daemon=True)
            th.start()
    
#   (From the API...)
#   .-[ DEFAULT VALUES FOR THE IMAGE ]--------------------------------.
#   | Parameter               |   Range       |   Default             |
#   |-----------------------------------------------------------------|
#   | Auto Exposure Target    |   16~235      |   120                 |
#   | Temp                    |   2000~15000  |   6503                |
#   | Tint                    |   200~2500    |   1000                |
#   | LevelRange              |   0~255       |   Low = 0, High = 255 |
#   | Contrast                |   -100~100    |   0                   |
#   | Hue                     |   -180~180    |   0                   |
#   | Saturation              |   0~255       |   128                 |
#   | Brightness              |   -64~64      |   0                   |
#   | Gamma                   |   20~180      |   100                 |
#   | WBGain                  |   -127~127    |   0                   |
#   '-----------------------------------------------------------------'

    def reset_camera_image_settings(self) -> None:
        """
        @brief Resets the camera's image settings back to default values. To apply changes to the
            camera one must invoke `set_camera_image_settings()` with no arguments.
        """
        self._hcam_exposure = 120 # Note: set to 50
        self._hcam_temp = 6503
        self._hcam_tint = 1000
        self._hcam_level_range_low = (0, 0, 0, 0)
        self._hcam_level_range_high = (255, 255, 255, 255)
        self._hcam_contrast = 0
        self._hcam_hue = 0
        self._hcam_saturation = 128
        self._hcam_brightness = 0 # Note set to 16
        self._hcam_gamma = 100
        self._hcam_wbgain = (0, 0, 0)

    def set_camera_image_settings(self, **kwargs) -> None:
        """
        @brief Modifies the microscope camera's image settings.
        @kwargs
         - exposure: The auto exposure target (0.0 ~ 1.0).
         - temp: The temperature value of the image (0.0 ~ 1.0).
         - tint: The tint of the image (0.0 ~ 1.0).
         - levelrange_low: The low end of the level range
            (0.0~1.0, 0.0~1.0, 0.0~1.0, 0.0~1.0).
         - levelrange_high: The high end of the level range
            (0.0~1.0, 0.0~1.0, 0.0~1.0, 0.0~1.0).
         - contrast: The contrast value of the image (0.0 ~ 1.0).
         - hue: The hue value of the image (0.0 ~ 1.0).
         - saturation: The saturation value of the image (0.0 ~ 1.0).
         - brightness: The brightness value of the image (0.0 ~ 1.0).
         - gamma: The gamma value of the image (0.0 ~ 1.0).
         - wbgain: The white balance rgb-triplet of the image
                (0.0 ~ 1.0, 0.0 ~ 1.0, 0.0 ~ 1.0).
        
        """

        if 'exposure' in kwargs:
            self._hcam_exposure = int(kwargs.get('exposure', '') * 219) + 16
        if 'temp' in kwargs:
            self._hcam_temp = int(kwargs.get('temp', '') * 13000) + 2000
        if 'tint' in kwargs:
            self._hcam_tint = int(kwargs.get('tint', '') * 2300) + 200
        if 'levelrange_low' in kwargs:
            self._hcam_level_range_low = (
                int(kwargs.get('levelrange_low', '')[0] * 255) + 0,
                int(kwargs.get('levelrange_low', '')[1] * 255) + 0,
                int(kwargs.get('levelrange_low', '')[2] * 255) + 0,
                int(kwargs.get('levelrange_low', '')[3] * 255) + 0
            )
        if 'levelrange_high' in kwargs:
            self._hcam_level_range_high = (
                int(kwargs.get('levelrange_high', '')[0] * 255) + 0,
                int(kwargs.get('levelrange_high', '')[1] * 255) + 0,
                int(kwargs.get('levelrange_high', '')[2] * 255) + 0,
                int(kwargs.get('levelrange_high', '')[3] * 255) + 0
            )
        if 'contrast' in kwargs:
            self._hcam_contrast = int(kwargs.get('contrast', '') * 200) - 100
        if 'hue' in kwargs:
            self._hcam_hue = int(kwargs.get('hue', '') * 360) - 180
        if 'saturation' in kwargs: 
            self._hcam_saturation = int(kwargs.get('saturation', '') * 255) + 0
        if 'brightness' in kwargs:
            self._hcam_brightness = int(kwargs.get('brightness', '') * 128) - 64
        if 'gamma' in kwargs:
            self._hcam_gamma = int(kwargs.get('gamma', '') * 160) + 20
        if 'wbgain' in kwargs:
            self._hcam_wbgain = (
                int(kwargs.get('wbgain', '')[0] * 254) - 127,
                int(kwargs.get('wbgain', '')[1] * 254) - 127,
                int(kwargs.get('wbgain', '')[2] * 254) - 127
            )
        
        try:
            self._hcam.put_AutoExpoTarget(self._hcam_exposure)
            self._hcam.put_TempTint(self._hcam_temp, self._hcam_tint)
            self._hcam.put_LevelRange(self._hcam_level_range_low, self._hcam_level_range_high)
            self._hcam.put_Contrast(self._hcam_contrast)
            self._hcam.put_Hue(self._hcam_contrast)
            self._hcam.put_Saturation(self._hcam_saturation)
            self._hcam.put_Brightness(self._hcam_brightness)
            self._hcam.put_Gamma(self._hcam_gamma)
            # self._hcam.put_WhiteBalanceGain(self._hcam_wbgain) ! Not implemented yet
        except amcam.HRESULTException as e:
            print(e)
        


    @staticmethod
    def camera_callback(event, _self: 'Camera'):
        # print(_self._hcam.get_Resolution(0))
        if event == amcam.AMCAM_EVENT_STILLIMAGE:
            print("Got still image!")
            _self.save_still_image() # Save still image!
        elif event == amcam.AMCAM_EVENT_IMAGE:
            # print("streaming!")
            _self.stream()
            # else: print("ignoring stream")
            # pass
        elif event == amcam.AMCAM_EVENT_EXPO_START:
            print("DEBUG> Found expo start!")
        
    def name(self) -> str: return self._cam_name

    def type(self) -> camera_type: return self._cam_type

    def stream(self) -> None:
        """
        @brief Streams the image received by the camera in real time.
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

    def set_capture_dir(self, path:str) -> None:
        self._capture_dir = path

# nResolutionIndex is a resolution supported by the camera.
# For example, UCMOS03100KPA supports the following resolutions:
#     index 0:    2048,   1536
#     index 1:    1024,   768
#     index 2:    680,    510
# so, we can use put_Size(h, 1024, 768) or put_eSize(h, 1). Both have the same effect.

    #* Takes still image triggers save
    def take_still_image(self) -> None:
        if self._hcam and self._cam_type == camera_type.MICROSCOPE:
            print(self._hcam.get_StillResolution(0))
            self._hcam.Snap(0) # Triggers saving with callback
            # self.stream_enabled = False
        elif self._hcam and self._cam_type == camera_type.WEBCAM:
            self.save_still_image()

    #* Save the still image
    def save_still_image(self) -> None:
        if self._hcam and self._cam_type == camera_type.MICROSCOPE:
            width = 2592
            height = 1944
            try:
                buffer_size = ((width * 24 + 31) // 32 * 4) * height # Also equal to 3*w*h
                buffer_size = width * height * 24
                buf = bytes(buffer_size)
                self._hcam.PullStillImageV2(buf, 24, None)
            except amcam.HRESULTException as e: print(e)
            else:
                # width, height = self._hcam.get_Size()
                img = QImage(
                    buf,
                    width,
                    height,
                    (width * 24 + 31) // 32 * 4,
                    QImage.Format_RGB888,
                )

        elif  self._hcam and self._cam_type == camera_type.WEBCAM:
            success, frame = self._hcam.read()
            if success:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                img = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
        try:
            if img:
                img.save(self._capture_dir)
        except IOError as e:
            print(e)

    #!! REMOVE METHOD BELOW
    def get_image(self) -> QImage:
        """
        @brief Takes an image from the camera to store.
        @return Returns a QImage from the camera.
        """
        return self._image

    def close(self) -> None:
        """
        @brief Closes the camera.
        """
        if self._hcam is not None and self._cam_type == camera_type.MICROSCOPE:
            self._hcam.Close() # Amcam camera close method
        elif self._hcam is not None and self._cam_type == camera_type.WEBCAM:
            self._hcam.release() # cv2 VideoCapture close method
        self._hcam = None