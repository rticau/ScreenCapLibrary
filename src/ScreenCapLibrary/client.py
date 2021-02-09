#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import time
import threading

try:
    import cv2
    import numpy as np
except ImportError:
    raise ImportError('Importing cv2 failed. Make sure you have opencv-python installed.')

from mss import mss
from PIL import Image
from functools import wraps
from robot.api import logger
from robot.utils import get_link_path, abspath, timestr_to_secs, is_truthy
from robot.libraries.BuiltIn import BuiltIn
from .pygtk import _take_gtk_screenshot, _take_partial_gtk_screenshot, _take_gtk_screen_size, _grab_gtk_pb
from .utils import _norm_path, _compression_value_conversion, _pil_quality_conversion, is_pygtk

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.thread import _threads_queues


def run_in_background(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        return ThreadPoolExecutor().submit(f, *args, **kwargs)
    return wrap


class Client:

    def __init__(self, screenshot_module=None, screenshot_directory=None, format='png', quality=50, delay=0,
                 display_cursor=False):
        self.screenshot_module = screenshot_module
        self._given_screenshot_dir = _norm_path(screenshot_directory)
        self._format = format
        self._quality = quality
        self._delay = delay
        self._display_cursor = display_cursor
        self.frames = []
        self.name = 'screenshot'
        self.path = None
        self.embed = False
        self.embed_width = None
        self._stop_condition = threading.Event()
        self._pause_condition = threading.Event()
        self.futures = None

    @property
    def cursor(self):
        return self._display_cursor

    @property
    def screenshot_dir(self):
        return self._given_screenshot_dir or self._log_dir

    @property
    def _log_dir(self):
        variables = BuiltIn().get_variables()
        outdir = variables['${OUTPUTDIR}']
        log = variables['${LOGFILE}']
        log = os.path.dirname(log) if log != 'NONE' else '.'
        return _norm_path(os.path.join(outdir, log))

    def set_screenshot_directory(self, path):
        path = _norm_path(path)
        if not os.path.isdir(path):
            raise RuntimeError("Directory '%s' does not exist." % path)
        old = self.screenshot_dir
        self._given_screenshot_dir = path
        return old

    def _get_screenshot_path(self, basename, format, directory):
        directory = _norm_path(directory) if directory else self.screenshot_dir
        if basename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.webm')):
            return os.path.join(directory, basename)
        index = 0
        while True:
            index += 1
            path = os.path.join(directory, "%s_%d.%s" % (basename, index, format))
            if not os.path.exists(path):
                return path

    @staticmethod
    def _validate_screenshot_path(path):
        path = abspath(_norm_path(path))
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("Directory '%s' where to save the screenshot "
                               "does not exist" % os.path.dirname(path))
        return path

    def _save_screenshot_path(self, basename, format):
        path = self._get_screenshot_path(basename, format, self.screenshot_dir)
        return self._validate_screenshot_path(path)

    def take_screenshot(self, name, format, quality, width, delay, monitor):
        delay = delay or self._delay
        if delay:
            time.sleep(timestr_to_secs(delay))
        path = self._take_screenshot_client(name, format, quality, monitor)
        self._embed_screenshot(path, width)
        return path

    def _take_screenshot_client(self, name, format, quality, monitor):
        format = (format or self._format).lower()
        quality = quality or self._quality
        if is_pygtk(self.screenshot_module):
            return self._take_screenshot_client_gtk(name, format, quality, monitor)
        else:
            return self._take_screenshot_client_mss(name, format, quality, monitor)

    def _take_screenshot_client_gtk(self, name, format, quality, monitor):
        format = 'jpeg' if format == 'jpg' else format
        if format == 'png':
            quality = _compression_value_conversion(quality)
        path = self._save_screenshot_path(name, format)
        if format == 'webp':
            png_img = _take_gtk_screenshot(path, 'png', _compression_value_conversion(100), monitor)
            im = Image.open(png_img)
            im.save(path, format, quality=quality)
            return path
        return _take_gtk_screenshot(path, format, quality, monitor)

    def _take_screenshot_client_mss(self, name, format, quality, monitor):
        if format in ['jpg', 'jpeg', 'webp']:
            with mss() as sct:
                sct_img = sct.grab(sct.monitors[int(monitor)])
                img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
                path = self._save_screenshot_path(name, format)
                img.save(path, quality=quality if format == 'webp' else _pil_quality_conversion(quality))
            return path
        elif format == 'png':
            with mss() as sct:
                path_name = self._save_screenshot_path(name, format)
                sct.compression_level = _compression_value_conversion(quality)
                path = sct.shot(mon=-1, output='%s' % path_name)
            return path
        else:
            raise RuntimeError("Invalid screenshot format.")

    def take_multiple_screenshots(self, name, format, quality, screenshot_number, delay_time, monitor):
        del self.frames[:]
        quality = quality or self._quality
        format = (format or self._format).lower()
        format = 'jpeg' if format == 'jpg' else format
        if format == 'png':
            quality = _compression_value_conversion(quality)
        elif format == 'jpeg':
            quality = _pil_quality_conversion(quality)
        delay_time = timestr_to_secs(delay_time)
        self._take_multiple_screenshots(name, format, quality, delay=delay_time, shot_number=int(screenshot_number),
                                        monitor=monitor)

    @run_in_background
    def _take_multiple_screenshots(self, name, format, quality, delay, shot_number, monitor):
        if is_pygtk(self.screenshot_module):
            self._take_multiple_screenshots_gtk(delay, shot_number, monitor)
        else:
            self._take_multiple_screenshots_mss(delay, shot_number, monitor)
        for img in self.frames:
            path = self._save_screenshot_path(basename=name, format=format)
            img.save(path, format=format, quality=quality, compress_level=quality)

    def _take_multiple_screenshots_mss(self, delay, shot_number, monitor):
        taken = 0
        with mss() as sct:
            while taken < shot_number:
                sct_img = sct.grab(sct.monitors[int(monitor)])
                img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
                self.frames.append(img)
                time.sleep(timestr_to_secs(delay))
                taken += 1

    def _take_multiple_screenshots_gtk(self, delay, shot_number, monitor):
        taken = 0
        width, height = _take_gtk_screen_size(monitor)
        while taken < shot_number:
            pb = _grab_gtk_pb(monitor)
            img = Image.frombuffer('RGB', (width, height), pb.get_pixels(), 'raw', 'RGB')
            self.frames.append(img)
            time.sleep(timestr_to_secs(delay))
            taken += 1

    def take_partial_screenshot(self, name, format, quality,
                                left, top, width, height, embed, embed_width, monitor):
        left = int(left)
        top = int(top)
        width = int(width)
        height = int(height)
        format = (format or self._format).lower()
        quality = quality or self._quality

        if is_pygtk(self.screenshot_module):
            format = 'jpeg' if format == 'jpg' else format
            if format == 'png':
                quality = _compression_value_conversion(quality)
            path = self._save_screenshot_path(name, format)
            path = _take_partial_gtk_screenshot(path, format, quality, left, top, width, height, monitor)
        else:
            try:
                original_image = self._take_screenshot_client(name, format, quality, monitor)
                image = Image.open(original_image)
                right = left + width
                bottom = top + height
                box = (left, top, right, bottom)
                cropped_image = image.crop(box)
                os.remove(original_image)
                path = self._save_screenshot_path(basename=name, format=format)
                cropped_image.save(path, format)
            except IOError:
                raise IOError('File not found.')
            except RuntimeError:
                raise RuntimeError('Taking screenshot failed.')
            except SystemError:
                raise SystemError("Top and left parameters must be lower than screen resolution.")
        if is_truthy(embed):
            self._embed_screenshot(path, embed_width)
        return path

    def take_screenshot_without_embedding(self, name, format, quality, delay, monitor):
        delay = delay or self._delay
        if delay:
            time.sleep(timestr_to_secs(delay))
        path = self._take_screenshot_client(name, format, quality, monitor)
        self._link_screenshot(path)
        return path

    def _stop_thread(self):
        self._stop_condition.set()
        self.futures.result()
        if self.futures._exception:
            raise self.futures._exception

    @staticmethod
    def clear_thread_queues():
        _threads_queues.clear()

    def _embed_screenshot(self, path, width):
        link = get_link_path(path, self._log_dir)
        logger.info('<a href="%s"><img src="%s" width="%s"></a>' % (link, link, width), html=True)

    def _link_screenshot(self, path):
        link = get_link_path(path, self._log_dir)
        logger.info("Screenshot saved to '<a href=\"%s\">%s</a>'." % (link, path), html=True)

    def _pause_thread(self):
        self._pause_condition.set()

    def _resume_thread(self):
        self._pause_condition.clear()
