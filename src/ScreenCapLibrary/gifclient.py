import imageio
import threading

from .client import Client, run_in_background
from .pygtk import _take_gtk_screen_size, _grab_gtk_pb, _convert_pixbuf_to_numpy, is_gdk
from .utils import _norm_path

from mss import mss
from robot.utils import is_truthy

try:
    import cv2
    import numpy as np
except ImportError:
    raise ImportError('Importing cv2 failed. Make sure you have opencv-python installed.')


class GifClient(Client):

    def __init__(self, screenshot_module, screenshot_directory):
        Client.__init__(self)
        self.screenshot_module = screenshot_module
        self._given_screenshot_dir = _norm_path(screenshot_directory)
        self._stop_condition = threading.Event()

    def start_gif_recording(self, name, size_percentage,
                            embed, embed_width):
        self.name = name
        self.embed = embed
        self.embed_width = embed_width
        self.path = self._save_screenshot_path(basename=self.name, format='gif')
        self.futures = self.grab_frames(size_percentage, self._stop_condition)
        self.clear_thread_queues()

    def stop_gif_recording(self):
        self._stop_thread()
        if is_truthy(self.embed):
            self._embed_screenshot(self.path, self.embed_width)
        return self.path

    @run_in_background
    def grab_frames(self, size_percentage, stop):
        if self.screenshot_module and self.screenshot_module.lower() == 'pygtk':
            self._grab_frames_gtk(size_percentage, stop)
        else:
            self._grab_frames_mss(size_percentage, stop)

    def _grab_frames_gtk(self, size_percentage, stop):
        width, height = _take_gtk_screen_size()
        w = int(width * size_percentage)
        h = int(height * size_percentage)
        with imageio.get_writer(self.path, mode='I') as writer:
            while not stop.isSet():
                pb = _grab_gtk_pb()
                if is_gdk():
                    numpy_array = _convert_pixbuf_to_numpy(pb)
                else:
                    numpy_array = pb.get_pixels_array()
                resized_array = cv2.resize(numpy_array, dsize=(w, h), interpolation=cv2.INTER_AREA) \
                    if size_percentage != 1 else numpy_array
                frame = cv2.cvtColor(resized_array, cv2.COLOR_RGB2BGR)
                writer.append_data(frame)

    def _grab_frames_mss(self, size_percentage, stop):
        with mss() as sct:
            width = int(sct.grab(sct.monitors[0]).width * size_percentage)
            height = int(sct.grab(sct.monitors[0]).height * size_percentage)
            with imageio.get_writer(self.path, mode='I') as writer:
                while not stop.isSet():
                    sct_img = sct.grab(sct.monitors[0])
                    numpy_array = np.array(sct_img)
                    resized_array = cv2.resize(numpy_array, dsize=(width, height), interpolation=cv2.INTER_AREA) \
                        if size_percentage != 1 else numpy_array
                    frame = cv2.cvtColor(resized_array, cv2.COLOR_RGB2BGR)
                    writer.append_data(frame)
