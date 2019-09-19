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
        self.futures = self.grab_frames(name, size_percentage=size_percentage, stop=self._stop_condition)
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
    def grab_frames(self, name, format=None, quality=None, size_percentage=0.5, delay=0, shot_number=None, stop=None):
        if self.screenshot_module and self.screenshot_module.lower() == 'pygtk':
            self._grab_frames_gtk(size_percentage, delay, shot_number, stop)
        else:
            self._grab_frames_mss(size_percentage, delay, shot_number, stop)
        if shot_number:
            for img in self.frames:
                path = self._save_screenshot_path(basename=name, format=format)
                img.save(path, format=format, quality=quality, compress_level=quality)

    def _grab_frames_gtk(self, size_percentage, delay, shot_number, stop):
        width, height = _take_gtk_screen_size()
        w = int(width * size_percentage)
        h = int(height * size_percentage)
        while not stop.isSet():
            pb = _grab_gtk_pb()
            img = Image.frombuffer('RGB', (width, height), pb.get_pixels(), 'raw', 'RGB').resize((w, h))
            self.frames.append(img)
            if delay:
                time.sleep(timestr_to_secs(delay))
            if shot_number and len(self.frames) == int(shot_number):
                break
            time.sleep(self.gif_frame_time / 1000)

    def _grab_frames_mss(self, size_percentage, delay, shot_number, stop):
        with mss() as sct:
            width = int(sct.grab(sct.monitors[0]).width * size_percentage)
            height = int(sct.grab(sct.monitors[0]).height * size_percentage)
            while not stop.isSet():
                sct_img = sct.grab(sct.monitors[0])
                img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX').resize((width, height))
                self.frames.append(img)
                if delay:
                    time.sleep(timestr_to_secs(delay))
                if shot_number and len(self.frames) == int(shot_number):
                    break
                time.sleep(self.gif_frame_time / 1000)
