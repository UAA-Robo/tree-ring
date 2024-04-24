import io
import sys, amcam, time, enum
import yaml
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
        self._runtime = 0
        try:
            self.load_camera()
        except Exception as e:
            print(e)
        
        # self._hcam_exposure = None
        # self._hcam_temp = None
        # self._hcam_tint = None
        # self._hcam_level_range_low = None
        # self._hcam_level_range_high = None
        # self._hcam_contrast = None
        # self._hcam_hue = None
        # self._hcam_saturation = None
        # self._hcam_brightness = None
        # self._hcam_gamma = None
        # self._hcam_wbgain = None


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
                print('loading microscope')
                self.reset_camera_image_settings()
                # self.set_camera_image_settings(saturation=0.3764705882352941) # Reduces yellow image quality
                self.set_camera_image_settings(saturation=96)
                self.load_camera_image_settings()
                self.set_camera_image_settings()
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
#   | Parameter                | Range         | Default              |
#   |-----------------------------------------------------------------|
#   | Auto Exposure Target     | 16~235        | 120                  |
#   | Temp                     | 2000~15000    | 6503                 |
#   | Tint                     | 200~2500      | 1000                 |
#   | LevelRange               | 0~255         | Low = 0, High = 255  |
#   | Contrast                 | -100~100      | 0                    |
#   | Hue                      | -180~180      | 0                    |
#   | Saturation               | 0~255         | 128                  |
#   | Brightness               | -64~64        | 0                    |
#   | Gamma                    | 20~180        | 100                  |
#   | WBGain                   | -127~127      | 0                    |
#   | Sharpening               | 0~500         | 0                    |
#   | Linear Tone Mapping      | 1/0           | 1                    |
#   | Curved Tone Mapping      | 2/1/0         | 2                    |
#   '-----------------------------------------------------------------'

    def reset_camera_image_settings(self) -> None:
        """
        @brief Resets the camera's image settings back to default values. To apply changes to the
            camera one must invoke `set_camera_image_settings()` with no arguments.
        """
        self._hcam_exposure = 50 # Originally 120
        self._hcam_temp = 6503
        self._hcam_tint = 1000
        self._hcam_level_range_low = (0, 0, 0, 0)
        self._hcam_level_range_high = (255, 255, 255, 255)
        self._hcam_contrast = 0
        self._hcam_hue = 0
        self._hcam_saturation = 128
        self._hcam_brightness = 16 # Originally 0
        self._hcam_gamma = 100
        self._hcam_wbgain = (0, 0, 0)
        self._hcam_sharpening = 500
        self._hcam_linear = 0
        self._hcam_curve = 1

    def load_camera_image_settings(self) -> None: # With code borrowed from https://stackoverflow.com/questions/1773805/how-can-i-parse-a-yaml-file-in-python
        try:
            with open("camera_configuration.yaml", "r") as stream:
                try:
                    settings = yaml.safe_load(stream)
                    self._hcam_exposure = settings['exposure']
                    self._hcam_temp = settings['temp']
                    self._hcam_tint = settings['tint']
                    self._hcam_level_range_low = settings['levelrange_low']
                    self._hcam_level_range_high = settings['levelrange_high']
                    self._hcam_contrast = settings['contrast']
                    self._hcam_hue = settings['hue']
                    self._hcam_saturation = settings['saturation']
                    self._hcam_brightness = settings['brightness']
                    self._hcam_gamma = settings['gamma']
                    self._hcam_wbgain = settings['wbgain']
                    self._hcam_sharpening = settings['sharpening']
                    self._hcam_linear = settings['linear']
                    self._hcam_curve = settings['curve']
                except yaml.YAMLError as e:
                    print('YAML ERROR >', e)
                except OSError as e:
                    print('OS ERROR >', e)
        except Exception as e:
            print('GENERAL ERROR >', e)


    def get_slider_values(self) -> tuple:
        # if not self.is_microscope(): raise ValueError("Could not load camera settings")
        return (
            self._hcam_temp,
            self._hcam_tint,
            self._hcam_contrast,
            self._hcam_hue,
            self._hcam_saturation,
            self._hcam_brightness,
            self._hcam_sharpening,
            self._hcam_linear,
            self._hcam_curve
        )

    def set_camera_image_settings(self, **kwargs) -> None:
        """
        @brief Modifies the microscope camera's image settings.
        @kwargs
         - exposure: The auto exposure target (16 ~ 235).
         - temp: The temperature value of the image (2000 ~ 15000).
         - tint: The tint of the image (200 ~ 2500).
         - levelrange_low: The low end of the level range
                           (0~255, 0~255, 0~255, 0~255).
         - levelrange_high: The high end of the level range
                            (0~255, 0~255, 0~255, 0~255).
         - contrast: The contrast value of the image (-100 ~ 100).
         - hue: The hue value of the image (-180 ~ 180).
         - saturation: The saturation value of the image (0 ~ 255).
         - brightness: The brightness value of the image (-64 ~ 64).
         - gamma: The gamma value of the image (20 ~ 180).
         - wbgain: The white balance rgb-triplet of the image
                   (-127~127, -127~127, -127~127).
         - sharpness: The amount of sharpness to use on the image (0~500).
         - linear: Whether to use linear (...) or not (1/0).
         - curve: Whether to use curve (...) or not (2/1/0).

        """

        if 'exposure' in kwargs:
            self._hcam_exposure = kwargs.get('exposure', '')
        if 'temp' in kwargs:
            self._hcam_temp = kwargs.get('temp', '')
        if 'tint' in kwargs:
            self._hcam_tint = kwargs.get('tint', '')
        if 'levelrange_low' in kwargs:
            self._hcam_level_range_low = (
                kwargs.get('levelrange_low', '')[0],
                kwargs.get('levelrange_low', '')[1],
                kwargs.get('levelrange_low', '')[2],
                kwargs.get('levelrange_low', '')[3]
            )
        if 'levelrange_high' in kwargs:
            self._hcam_level_range_high = (
                kwargs.get('levelrange_high', '')[0],
                kwargs.get('levelrange_high', '')[1],
                kwargs.get('levelrange_high', '')[2],
                kwargs.get('levelrange_high', '')[3]
            )
        if 'contrast' in kwargs:
            self._hcam_contrast = kwargs.get('contrast', '')
        if 'hue' in kwargs:
            self._hcam_hue = kwargs.get('hue', '')
        if 'saturation' in kwargs: 
            self._hcam_saturation = kwargs.get('saturation', '')
        if 'brightness' in kwargs:
            self._hcam_brightness = kwargs.get('brightness', '')
        if 'gamma' in kwargs:
            self._hcam_gamma = kwargs.get('gamma', '')
        if 'wbgain' in kwargs:
            self._hcam_wbgain = (
                kwargs.get('wbgain', '')[0],
                kwargs.get('wbgain', '')[1],
                kwargs.get('wbgain', '')[2]
            )
        if 'sharpening' in kwargs:
            self._hcam_sharpening = int(kwargs.get('sharpening', ''))
        if 'linear' in kwargs:
            self._hcam_linear = int(kwargs.get('linear', ''))
        if 'curve' in kwargs:
            self._hcam_curve = int(kwargs.get('curve', ''))

        if kwargs: print(kwargs)
        # print('setting temp', self._hcam_temp)
        # print('expo', self._hcam_exposure)
        # print('temp', self._hcam_temp)
        # print('tint', self._hcam_tint)
        # print('levelrangelow', self._hcam_level_range_low)
        # print('levelrangehigh', self._hcam_level_range_high)
        # print('contrast', self._hcam_contrast)
        # print('hue', self._hcam_hue)
        # print('saturation', self._hcam_saturation)
        # print('brightness', self._hcam_brightness)
        # print('gamma', self._hcam_gamma)
        # print('wbgain', self._hcam_wbgain)
        if self._runtime % 2 == 0:
            try:
                if self._hcam_exposure is not None: self._hcam.put_AutoExpoTarget(self._hcam_exposure)
                if self._hcam_temp is not None and\
                    self._hcam_tint is not None: self._hcam.put_TempTint(self._hcam_temp, self._hcam_tint)
                if self._hcam_level_range_high is not None and\
                    self._hcam_level_range_low is not None: self._hcam.put_LevelRange(self._hcam_level_range_low, self._hcam_level_range_high)
                if self._hcam_contrast is not None: self._hcam.put_Contrast(self._hcam_contrast)
                if self._hcam_hue is not None: self._hcam.put_Hue(self._hcam_contrast)
                if self._hcam_saturation is not None: self._hcam.put_Saturation(self._hcam_saturation)
                if self._hcam_brightness is not None: self._hcam.put_Brightness(self._hcam_brightness)
                if self._hcam_gamma is not None: self._hcam.put_Gamma(self._hcam_gamma)
                if self._hcam_sharpening is not None: self._hcam.put_Option(amcam.AMCAM_OPTION_SHARPENING, self._hcam_sharpening)
                if self._hcam_linear is not None: self._hcam.put_Option(amcam.AMCAM_OPTION_LINEAR, self._hcam_linear)
                if self._hcam_curve is not None: self._hcam.put_Option(amcam.AMCAM_OPTION_CURVE, self._hcam_curve)
                #if self._hcam_wbgain is not None: self._hcam.put_WhiteBalanceGain(self._hcam_wbgain) ! Not implemented yet
            except amcam.HRESULTException as e:
                print(e)
            except AttributeError as e:
                print(e)
        
    def save_camera_settings(self):
        settings: dict = {
            'exposure': self._hcam_exposure,
            'temp': self._hcam_temp,
            'tint': self._hcam_tint,
            'levelrange_low': [
                self._hcam_level_range_low[0],
                self._hcam_level_range_low[1],
                self._hcam_level_range_low[2],
                self._hcam_level_range_low[3]
            ],
            'levelrange_high': [
                self._hcam_level_range_high[0],
                self._hcam_level_range_high[1],
                self._hcam_level_range_high[2],
                self._hcam_level_range_high[3]
            ],
            'contrast': self._hcam_contrast,
            'hue': self._hcam_hue,
            'saturation': self._hcam_saturation,
            'brightness': self._hcam_brightness,
            'gamma': self._hcam_gamma,
            'wbgain': [
                self._hcam_wbgain[0],
                self._hcam_wbgain[1],
                self._hcam_wbgain[2]
            ],
            'sharpening': self._hcam_sharpening,
            'linear': self._hcam_linear,
            'curve': self._hcam_curve,
        }
        output = open("camera_configuration.yaml","w")
        yaml.dump(settings, output)


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