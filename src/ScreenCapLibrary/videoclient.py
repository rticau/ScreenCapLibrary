import threading

from .client import Client, run_in_background
from .pygtk import _record_gtk
from .utils import _norm_path, suppress_stderr
from mss import mss
from robot.utils import get_link_path, is_truthy
from robot.api import logger

try:
    import cv2
    import numpy as np
except ImportError:
    raise ImportError('Importing cv2 failed. Make sure you have opencv-python installed.')


class VideoClient(Client):

    def __init__(self, screenshot_module, screenshot_directory, fps):
        Client.__init__(self)
        self.screenshot_module = screenshot_module
        self._given_screenshot_dir = _norm_path(screenshot_directory)
        self._stop_condition = threading.Event()
        self.alias = None
        try:
            self.fps = int(fps)
        except ValueError:
            raise ValueError('The fps argument must be of type integer.')

    def start_video_recording(self, alias, name, size_percentage, embed, embed_width):
        self.alias = alias
        self.name = name
        self.embed = embed
        self.embed_width = embed_width
        self.path = self._save_screenshot_path(basename=self.name, format='webm')
        self.futures = self.capture_screen(self.path, self.fps, size_percentage=size_percentage)
        self.clear_thread_queues()

    def stop_video_recording(self):
        self._stop_thread()
        if is_truthy(self.embed):
            self._embed_video(self.path, self.embed_width)
        return self.path

    @run_in_background
    def capture_screen(self, path, fps, size_percentage):
        if self.screenshot_module and self.screenshot_module.lower() == 'pygtk':
            _record_gtk(path, fps, size_percentage, stop=self._stop_condition)
        else:
            self._record_mss(path, fps, size_percentage)

    def _record_mss(self, path, fps, size_percentage):
        fourcc = cv2.VideoWriter_fourcc(*'VP08')
        with mss() as sct:
            if not sct.grab(sct.monitors[1]):
                raise Exception('Monitor not available.')
            width = int(sct.grab(sct.monitors[1]).width * size_percentage)
            height = int(sct.grab(sct.monitors[1]).height * size_percentage)
        with suppress_stderr():
            vid = cv2.VideoWriter('%s' % path, fourcc, fps, (width, height))
        while not self._stop_condition.isSet():
            with mss() as sct:
                sct_img = sct.grab(sct.monitors[1])
            numpy_array = np.array(sct_img)
            resized_array = cv2.resize(numpy_array, dsize=(width, height), interpolation=cv2.INTER_AREA) \
                if size_percentage != 1 else numpy_array
            frame = cv2.cvtColor(resized_array, cv2.COLOR_RGBA2RGB)
            vid.write(frame)
        vid.release()
        cv2.destroyAllWindows()

    def _embed_video(self, path, width):
        link = get_link_path(path, self._log_dir)
        logger.info('<a href="%s"><video width="%s" autoplay><source src="%s" type="video/webm"></video></a>' %
                    (link, width, link), html=True)
