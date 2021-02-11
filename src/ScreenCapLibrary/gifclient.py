import imageio
import threading

from .client import Client, run_in_background
from .pygtk import _take_gtk_screen_size, _grab_gtk_pb, _convert_pixbuf_to_numpy, is_gdk
from .utils import _norm_path, resize_array, is_pygtk
from mss import mss
from PIL import Image, ImageSequence
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
        self.optimize = None

    def start_gif_recording(self, name, size_percentage,
                            embed, embed_width, monitor, optimize):
        self.name = name
        self.embed = embed
        self.embed_width = embed_width
        self.optimize = optimize
        self.path = self._save_screenshot_path(basename=self.name, format='gif')
        self.futures = self.grab_frames(size_percentage, self._stop_condition, int(monitor))
        self.clear_thread_queues()

    def stop_gif_recording(self):
        self._stop_thread()
        if is_truthy(self.embed):
            self._embed_screenshot(self.path, self.embed_width)
        if is_truthy(self.optimize):
            frames = []
            for frame in ImageSequence.Iterator(Image.open(self.path)):
                frame = frame.copy()
                frames.append(frame)
            frames[0].save(self.path, save_all=True, append_images=frames[1:], optimize=True)
        return self.path

    @run_in_background
    def grab_frames(self, size_percentage, stop, monitor):
        if is_pygtk(self.screenshot_module):
            self._grab_frames_gtk(size_percentage, stop, monitor)
        else:
            self._grab_frames_mss(size_percentage, stop, monitor)

    def _grab_frames_gtk(self, size_percentage, stop, monitor):
        w, h = _take_gtk_screen_size(monitor)
        width = int(w * size_percentage)
        height = int(h * size_percentage)
        with imageio.get_writer(self.path, mode='I') as writer:
            while not stop.isSet():
                pb = _grab_gtk_pb(monitor)
                if is_gdk():
                    numpy_array = _convert_pixbuf_to_numpy(pb)
                else:
                    numpy_array = pb.get_pixels_array()
                resized_array = resize_array(width, height, numpy_array, size_percentage)
                frame = cv2.cvtColor(resized_array, cv2.COLOR_RGBA2RGB)
                writer.append_data(frame)

    def _grab_frames_mss(self, size_percentage, stop, monitor):
        with mss() as sct:
            mon = sct.monitors[monitor]
            width = int(sct.grab(mon).width * size_percentage)
            height = int(sct.grab(mon).height * size_percentage)
            with imageio.get_writer(self.path, mode='I') as writer:
                while not stop.isSet():
                    sct_img = sct.grab(mon)
                    resized_array = resize_array(width, height, np.array(sct_img), size_percentage)
                    frame = cv2.cvtColor(resized_array, cv2.COLOR_RGB2BGR)
                    writer.append_data(frame)
