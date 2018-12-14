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
try:
    from gtk import gdk
except ImportError:
    gdk = None

try:
    from gi import require_version
    require_version('Gdk', '3.0')
    from gi.repository import Gdk
except ImportError:
    Gdk = None


def _gtk_quality(format, quality):
    quality_setting = {}
    if format == 'png':
        quality_setting['compression'] = str(quality)
    else:
        quality_setting['quality'] = str(quality)
    return quality_setting


def _grab_screenshot_gtk_py2():
    window = gdk.get_default_root_window()
    if not window:
        raise RuntimeError('Taking screenshot failed.')
    width, height = window.get_size()
    pb = gdk.Pixbuf(gdk.COLORSPACE_RGB, False, 8, width, height)
    pb = pb.get_from_drawable(window, window.get_colormap(),
                              0, 0, 0, 0, width, height)
    if not pb:
        raise RuntimeError('Taking screenshot failed.')
    else:
        return pb


def _take_gtk_screenshot(path, format, quality):
    if not gdk and not Gdk:
        raise RuntimeError('PyGTK not installed/supported on this platform.')
    if gdk:
        return _take_gtk_screenshot_py2(path, format, quality)
    elif Gdk:
        return _take_gtk_screenshot_py3(path, format, quality)


def _take_gtk_screenshot_py2(path, format, quality):
    pb = _grab_screenshot_gtk_py2()
    quality_setting = _gtk_quality(format, quality)
    pb.save(path, format, quality_setting)
    return path


def _take_gtk_screenshot_py3(path, format, quality):
    window = Gdk.get_default_root_window()
    if not window:
        raise RuntimeError('Taking screenshot failed.')
    width = window.get_width()
    height = window.get_height()
    pb = Gdk.pixbuf_get_from_window(window, 0, 0, width, height)
    if not pb:
        raise RuntimeError('Taking screenshot failed.')
    quality_setting = _gtk_quality(format, quality)
    pb.savev(path, format, [list(quality_setting.keys())[0]], [list(quality_setting.values())[0]])
    return path


def _take_gtk_screen_size():
    if not gdk and not Gdk:
        raise RuntimeError('PyGTK not installed/supported on this platform.')
    if gdk:
        window = gdk.get_default_root_window()
        if not window:
            raise RuntimeError('Taking screenshot failed.')
        width, height = window.get_size()
        return width, height
    elif Gdk:
        window = Gdk.get_default_root_window()
        if not window:
            raise RuntimeError('Taking screenshot failed.')
        width = window.get_width()
        height = window.get_height()
        return width, height

def _take_partial_gtk_screenshot(path, format, quality, left, top, width, height):
    if not gdk and not Gdk:
        raise RuntimeError('PyGTK not installed/supported on this platform.')
    if gdk:
        return _take_partial_gtk_screenshot_py2(path, format, quality, left, top, width, height)
    elif Gdk:
        return _take_partial_gtk_screenshot_py3(path, format, quality, left, top, width, height)


def _take_partial_gtk_screenshot_py2(path, format, quality, left, top, width, height):
    source_pb = _grab_screenshot_gtk_py2()
    quality_setting = _gtk_quality(format, quality)
    cropped_pb = source_pb.subpixbuf(left, top, width, height)
    if not cropped_pb:
        raise RuntimeError('Taking screenshot failed.')
    cropped_pb.save(path, format, quality_setting)
    return path


def _take_partial_gtk_screenshot_py3(path, format, quality, left, top, width, height):
    window = Gdk.get_default_root_window()
    if not window:
        raise RuntimeError('Taking screenshot failed.')
    cropped_pb = Gdk.pixbuf_get_from_window(window, left, top, width, height)
    if not cropped_pb:
        raise RuntimeError('Taking screenshot failed.')
    quality_setting = _gtk_quality(format, quality)
    cropped_pb.savev(path, format, [list(quality_setting.keys())[0]], [list(quality_setting.values())[0]])
    return path
