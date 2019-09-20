import threading
import time

from .client import Client, run_in_background
from .pygtk import _take_gtk_screen_size, _grab_gtk_pb
from .utils import _norm_path

from mss import mss
from PIL import Image
from robot.utils import is_truthy, timestr_to_secs


class GifClient(Client):

    def __init__(self, screenshot_module, screenshot_directory):
        Client.__init__(self)
        self.screenshot_module = screenshot_module
        self._given_screenshot_dir = _norm_path(screenshot_directory)
        self._stop_condition = threading.Event()
        self.gif_frame_time = 125

    def start_gif_recording(self, name, size_percentage,
                            embed, embed_width):
        self.name = name
        self.embed = embed
        self.embed_width = embed_width
        self.futures = self.grab_frames(size_percentage, self._stop_condition)
        self.clear_thread_queues()

    def stop_gif_recording(self):
        self._stop_thread()
        path = self._save_screenshot_path(basename=self.name, format='gif')
        self.frames[0].save(path, save_all=True, append_images=self.frames[1:],
                            duration=self.gif_frame_time, optimize=True, loop=0)
        if is_truthy(self.embed):
            self._embed_screenshot(path, self.embed_width)
        del self.frames[:]
        return path

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
        while not stop.isSet():
            pb = _grab_gtk_pb()
            img = Image.frombuffer('RGB', (width, height), pb.get_pixels(), 'raw', 'RGB')
            if size_percentage != 1:
                img.resize((w, h))
            self.frames.append(img)
            time.sleep(self.gif_frame_time / 1000)

    def _grab_frames_mss(self, size_percentage, stop):
        with mss() as sct:
            width = int(sct.grab(sct.monitors[0]).width * size_percentage)
            height = int(sct.grab(sct.monitors[0]).height * size_percentage)
            while not stop.isSet():
                sct_img = sct.grab(sct.monitors[0])
                img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
                if size_percentage != 1:
                    img.resize((width, height))
                self.frames.append(img)
                time.sleep(self.gif_frame_time / 1000)
