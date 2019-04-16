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

from mss import mss
from PIL import Image
from robot.api import logger

from robot.utils import get_link_path, abspath, timestr_to_secs, is_truthy
from robot.libraries.BuiltIn import BuiltIn
from .pygtk import _take_gtk_screenshot, _take_partial_gtk_screenshot, _take_gtk_screen_size
from .utils import _norm_path, _compression_value_conversion, _pil_quality_conversion


class Client:

    def __init__(self, screenshot_module=None, screenshot_directory=None, format='png', quality=50, delay=0):
        self._screenshot_module = screenshot_module
        self._given_screenshot_dir = _norm_path(screenshot_directory)
        self._format = format
        self._quality = quality
        self._delay = delay

    @property
    def _screenshot_dir(self):
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
        old = self._screenshot_dir
        self._given_screenshot_dir = path
        return old

    def _get_screenshot_path(self, basename, format, directory):
        directory = _norm_path(directory) if directory else self._screenshot_dir
        if basename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
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

    def _save_screenshot_path(self, basename, format, directory=None):
        path = self._get_screenshot_path(basename, format, directory)
        return self._validate_screenshot_path(path)

    def take_screenshot(self, name, format, quality, width='800px', delay=0):
        delay = delay or self._delay
        if delay:
            time.sleep(timestr_to_secs(delay))
        path = self._take_screenshot_client(name, format, quality)
        self._embed_screenshot(path, width)
        return path

    def _take_screenshot_client(self, name, format, quality):
        format = (format or self._format).lower()
        quality = quality or self._quality
        if self._screenshot_module and self._screenshot_module.lower() == 'pygtk':
            return self._take_screenshot_client_gtk(name, format, quality)
        else:
            return self._take_screenshot_client_mss(name, format, quality)

    def _take_screenshot_client_gtk(self, name, format, quality):
        format = 'jpeg' if format == 'jpg' else format
        if format == 'png':
            quality = _compression_value_conversion(quality)
        path = self._save_screenshot_path(name, format)
        if format == 'webp':
            png_img = _take_gtk_screenshot(path, 'png', _compression_value_conversion(100))
            im = Image.open(png_img)
            im.save(path, format, quality=quality)
            return path
        return _take_gtk_screenshot(path, format, quality)

    def _take_screenshot_client_mss(self, name, format, quality):
        if format in ['jpg', 'jpeg', 'webp']:
            with mss() as sct:
                sct_img = sct.grab(sct.monitors[0])
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

    def take_multiple_screenshots(self, name, format, quality, screenshot_number, delay_time,
                                  embed, embed_width):
        paths = []
        try:
            for i in range(int(screenshot_number)):
                path = self._take_screenshot_client(name, format, quality)
                if delay_time:
                    time.sleep(timestr_to_secs(delay_time))
                paths.append(path)
                if is_truthy(embed):
                    self._embed_screenshot(path, embed_width)
        except ValueError:
            raise RuntimeError("Screenshot number argument must be of type integer.")
        return paths

    def take_partial_screenshot(self, name, format, quality,
                                left, top, width, height, embed, embed_width):
        left = int(left)
        top = int(top)
        width = int(width)
        height = int(height)
        format = (format or self._format).lower()
        quality = quality or self._quality

        if self._screenshot_module and self._screenshot_module.lower() == 'pygtk':
            format = 'jpeg' if format == 'jpg' else format
            if format == 'png':
                quality = _compression_value_conversion(quality)
            path = self._save_screenshot_path(name, format)
            path = _take_partial_gtk_screenshot(path, format, quality, left, top, width, height)
        else:
            try:
                original_image = self.take_screenshot(name, format, quality)
                image = Image.open(original_image)
                box = (left, top, width, height)
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

    def take_gif(self, name, duration, frame_time, size_percentage,
                 embed, embed_width):
        start_time = time.time()
        if self._screenshot_module and self._screenshot_module.lower() == 'pygtk':
            frames = self._take_gif_gtk(name, duration, size_percentage, start_time)
        else:
            frames = self._take_gif_mss(duration, size_percentage, start_time)
        path = self._save_screenshot_path(basename=name, format='gif')
        frames[0].save(path, save_all=True, append_images=frames[1:], optimize=True, duration=frame_time, loop=0)
        if is_truthy(embed):
            self._embed_screenshot(path, embed_width)
        return path

    def _take_gif_gtk(self, name, duration, size_percentage, start_time):
        frames = []
        width, height = _take_gtk_screen_size()
        gif_width = int(width * size_percentage)
        gif_height = int(height * size_percentage)
        quality = _compression_value_conversion(100)
        while time.time() <= start_time + int(duration):
            path = self._save_screenshot_path(name + repr(time.time()), 'png')
            pygtk_img = _take_gtk_screenshot(path, 'png', quality)
            im = Image.open(pygtk_img).resize((gif_width, gif_height))
            frames.append(im)
            os.remove(pygtk_img)
        return frames

    @staticmethod
    def _take_gif_mss(duration, size_percentage, start_time):
        frames = []
        with mss() as sct:
            gif_width = int(sct.grab(sct.monitors[0]).size.width * size_percentage)
            gif_height = int(sct.grab(sct.monitors[0]).size.height * size_percentage)
            while time.time() <= start_time + int(duration):
                sct_img = sct.grab(sct.monitors[0])
                img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX').resize((gif_width, gif_height))
                frames.append(img)
            return frames

    def take_screenshot_without_embedding(self, name, format, quality, delay):
        delay = delay or self._delay
        if delay:
            time.sleep(timestr_to_secs(delay))
        path = self._take_screenshot_client(name, format, quality)
        self._link_screenshot(path)
        return path

    def _embed_screenshot(self, path, width):
        link = get_link_path(path, self._log_dir)
        logger.info('<a href="%s"><img src="%s" width="%s"></a>' % (link, link, width), html=True)

    def _link_screenshot(self, path):
        link = get_link_path(path, self._log_dir)
        logger.info("Screenshot saved to '<a href=\"%s\">%s</a>'." % (link, path), html=True)
