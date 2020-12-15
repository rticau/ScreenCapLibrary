import os
import threading
import time

from .client import Client, run_in_background
from .pygtk import _record_gtk, benchmark_recording_performance_gtk, _take_gtk_screen_size
from .utils import _norm_path, suppress_stderr
from mss import mss
from robot.utils import get_link_path, is_truthy
from robot.api import logger

try:
    import pyautogui
except:
    pass

try:
    import cv2
    import numpy as np
except ImportError:
    raise ImportError('Importing cv2 failed. Make sure you have opencv-python installed.')

cursor_x_list = [0, 8, 6, 14, 12, 4, 2, 0]
cursor_y_list = [0, 2, 4, 12, 14, 6, 8, 0]


class VideoClient(Client):

    def __init__(self, screenshot_module, screenshot_directory, fps, display_cursor):
        Client.__init__(self)
        self.screenshot_module = screenshot_module
        self._given_screenshot_dir = _norm_path(screenshot_directory)
        self.display_cursor = is_truthy(display_cursor)
        self._stop_condition = threading.Event()
        self.alias = None
        try:
            if not fps:
                with suppress_stderr():
                    if self.screenshot_module and self.screenshot_module.lower() == 'pygtk':
                        width, height = _take_gtk_screen_size(monitor=1)
                        self.fps = benchmark_recording_performance_gtk(width, height, 1, monitor=1)
                    else:
                        with mss() as sct:
                            width = int(sct.grab(sct.monitors[1]).width)
                            height = int(sct.grab(sct.monitors[1]).height)
                            self.fps = self.benchmark_recording_performance(width, height, 1, monitor=1)
            else:
                self.fps = int(fps)
        except ValueError:
            raise ValueError('The fps argument must be of type integer.')

    def start_video_recording(self, alias, name, size_percentage, embed, embed_width, monitor):
        self.alias = alias
        self.name = name
        self.embed = embed
        self.embed_width = embed_width
        self.path = self._save_screenshot_path(basename=self.name, format='webm')
        self.futures = self.capture_screen(self.path, self.fps, size_percentage, int(monitor))
        self.clear_thread_queues()

    def stop_video_recording(self):
        self._stop_thread()
        if is_truthy(self.embed):
            self._embed_video(self.path, self.embed_width)
        return self.path

    @run_in_background
    def capture_screen(self, path, fps, size_percentage, monitor):
        if self.screenshot_module and self.screenshot_module.lower() == 'pygtk':
            _record_gtk(path, fps, size_percentage, self._stop_condition, self._pause_condition, monitor,
                        self.display_cursor)
        else:
            self._record_mss(path, fps, size_percentage, monitor)

    def _record_mss(self, path, fps, size_percentage, monitor):
        fourcc = cv2.VideoWriter_fourcc(*'VP08')
        with mss() as sct:
            mon = sct.monitors[monitor]
            if not sct.grab(mon):
                raise Exception('Monitor not available.')
            width = sct.grab(mon).width
            height = sct.grab(mon).height
        with suppress_stderr():
            if not fps:
                fps = self.benchmark_recording_performance(width, height, size_percentage, monitor)
            vid = cv2.VideoWriter('%s' % path, fourcc, fps,
                                  (int(width * size_percentage), int(height * size_percentage)))
        while not self._stop_condition.isSet():
            if self._pause_condition.isSet():
                continue
            self.record(vid, width, height, size_percentage, monitor, display_cursor=self.display_cursor)
        vid.release()
        cv2.destroyAllWindows()

    @staticmethod
    def record(vid, width, height, size_percentage, monitor, display_cursor=False):
        with mss() as sct:
            sct_img = sct.grab(sct.monitors[monitor])
            if display_cursor:
                mouse_x, mouse_y = pyautogui.position()
        numpy_array = np.array(sct_img)
        resized_array = cv2.resize(numpy_array, dsize=(int(width * size_percentage), int(height * size_percentage)),
                                   interpolation=cv2.INTER_AREA) if size_percentage != 1 else numpy_array
        frame = cv2.cvtColor(resized_array, cv2.COLOR_RGBA2RGB)
        if display_cursor:
            cursor_x = [x+mouse_x for x in cursor_x_list]
            cursor_y = [y+mouse_y for y in cursor_y_list]
            cursor_points = list(zip(cursor_x, cursor_y))
            cursor_points = np.array(cursor_points, 'int32')
            cv2.fillPoly(frame, [cursor_points], color=[0, 255, 255])
        vid.write(frame)

    def _embed_video(self, path, width):
        link = get_link_path(path, self._log_dir)
        logger.info('<a href="%s"><video width="%s" autoplay><source src="%s" type="video/webm"></video></a>' %
                    (link, width, link), html=True)

    def benchmark_recording_performance(self, width, height, size_percentage, monitor):
        fps = 0
        last_time = time.time()
        fourcc = cv2.VideoWriter_fourcc(*'VP08')
        # record a dummy video to compute optimal fps
        vid = cv2.VideoWriter('benchmark_%s.webm' % last_time, fourcc, 24, (int(width * size_percentage),
                              int(height * size_percentage)))

        # count the number of frames captured in 2 seconds
        while time.time() - last_time < 2:
            fps += 1
            self.record(vid, width, height, size_percentage, monitor, self.display_cursor)

        vid.release()
        cv2.destroyAllWindows()
        if os.path.exists("benchmark_%s.webm" % last_time):
            os.remove('benchmark_%s.webm' % last_time)  # delete the dummy file
        logger.info('Automatically setting a fps of %s' % str(fps / 2))
        return fps / 2  # return the number of frames per second

    def pause_video_recording(self):
        self._pause_thread()

    def resume_video_recording(self):
        self._resume_thread()
