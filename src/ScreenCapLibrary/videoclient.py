import sys
import threading

from .client import Client, run_in_background, _THREAD_POOL
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

    def __init__(self, screenshot_module, screenshot_directory):
        Client.__init__(self)
        self.screenshot_module = screenshot_module
        self._given_screenshot_dir = _norm_path(screenshot_directory)
        self._stop_condition = threading.Event()
        self.alias = None
        self.thread_name = None

    def _get_thread_index(self, thread_element):
        if sys.version_info[0] < 3:
            return (thread_element.name.rsplit(_THREAD_POOL._thread_name_prefix, 1)[1]).replace('_', '',)
        else:
            return (thread_element._name.rsplit(_THREAD_POOL._thread_name_prefix, 1)[1]).replace('_', '',)

    def start_video_recording(self, alias, name, fps, embed, embed_width):
        self.alias = alias
        self.name = name
        try:
            self.fps = int(fps)
        except ValueError:
            raise ValueError('The fps argument must be of type integer.')
        self.embed = embed
        self.embed_width = embed_width
        self.path = self._save_screenshot_path(basename=self.name, format='webm')
        old_prefix = _THREAD_POOL._thread_name_prefix
        if alias:
            _THREAD_POOL._thread_name_prefix = alias
        self.futures = self.capture_screen(self.path, self.fps)
        if alias:
            _THREAD_POOL._thread_name_prefix = old_prefix
        else:
            thread_list = list(_THREAD_POOL._threads)
            last_thread_index = self._get_thread_index(thread_list[0])
            for element in thread_list:
                element_index = self._get_thread_index(element)
                if int(element_index) >= int(last_thread_index):
                    last_thread_index = element_index
            self.thread_name = _THREAD_POOL._thread_name_prefix + '_' + last_thread_index

    def stop_video_recording(self, alias):
        self._stop_condition.set()
        if alias:
            self._close_threads(alias)
        else:
            self._close_threads(self.thread_name)
        if is_truthy(self.embed):
            self._embed_video(self.path, self.embed_width)
        return self.path

    @run_in_background
    def capture_screen(self, path, fps):
        if self.screenshot_module and self.screenshot_module.lower() == 'pygtk':
            _record_gtk(path, fps, stop=self._stop_condition)
        else:
            self._record_mss(path, fps)

    def _record_mss(self, path, fps):
        fourcc = cv2.VideoWriter_fourcc(*'VP08')
        with mss() as sct:
            sct_img = sct.grab(sct.monitors[1])
        width = int(sct_img.width)
        height = int(sct_img.height)
        with suppress_stderr():
            vid = cv2.VideoWriter('%s' % path, fourcc, fps, (width, height))
        while not self._stop_condition.isSet():
            with mss() as sct:
                sct_img = sct.grab(sct.monitors[1])
            numpy_array = np.array(sct_img)
            frame = cv2.cvtColor(numpy_array, cv2.COLOR_RGBA2RGB)
            vid.write(frame)
        vid.release()
        cv2.destroyAllWindows()

    def _embed_video(self, path, width):
        link = get_link_path(path, self._log_dir)
        logger.info('<a href="%s"><video width="%s" autoplay><source src="%s" type="video/webm"></video></a>' %
                    (link, width, link), html=True)
