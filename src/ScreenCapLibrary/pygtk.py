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
import cv2
import numpy as np
from .utils import suppress_stderr
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

try:
    from gi.repository import require_version
    require_version('Gdk', '3.0')
    from gi.repository import GdkPixbuf
except ImportError:
    GdkPixbuf = None


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
    return pb


def _grab_screenshot_gtk_py3():
    window = Gdk.get_default_root_window()
    if not window:
        raise RuntimeError('Taking screenshot failed.')
    width = window.get_width()
    height = window.get_height()
    pb = Gdk.pixbuf_get_from_window(window, 0, 0, width, height)
    if not pb:
        raise RuntimeError('Taking screenshot failed.')
    return pb


def _grab_gtk_pb():
    if not gdk and not Gdk:
        raise RuntimeError('PyGTK not installed/supported on this platform.')
    if gdk:
        return _grab_screenshot_gtk_py2()
    elif Gdk:
        return _grab_screenshot_gtk_py3()


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
    pb = _grab_screenshot_gtk_py3()
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


def _record_gtk(path, fps, stop):
    if not gdk and not Gdk:
        raise RuntimeError('PyGTK not installed/supported on this platform.')
    if gdk:
        return _record_gtk_py2(path, fps, stop)
    elif Gdk:
        return _record_gtk_py3(path, fps, stop)


def _record_gtk_py2(path, fps, stop):
    window = gdk.get_default_root_window()
    fourcc = cv2.VideoWriter_fourcc(*'VP08')
    width, height = window.get_size()
    with suppress_stderr():
        vid = cv2.VideoWriter('%s' % path, fourcc, fps, (width, height))
    while not stop:
        pb = gdk.Pixbuf(gdk.COLORSPACE_RGB, False, 8, width, height)
        pb = pb.get_from_drawable(window, window.get_colormap(),
                                   0, 0, 0, 0, width, height)
        numpy_array = pb.get_pixels_array()
        frame = cv2.cvtColor(numpy_array, cv2.COLOR_RGBA2RGB)
        vid.write(frame)
    vid.release()
    cv2.destroyAllWindows()


def _record_gtk_py3(path, fps, stop):
    window = Gdk.get_default_root_window()
    fourcc = cv2.VideoWriter_fourcc(*'VP08')
    width = window.get_width()
    height = window.get_height()
    with suppress_stderr():
        vid = cv2.VideoWriter('%s' % path, fourcc, fps, (width, height))
    while not stop:
        pb = Gdk.pixbuf_get_from_window(window, 0, 0, width, height)
        numpy_array = _convert_pixbuf_to_numpy(pb)
        frame = cv2.cvtColor(numpy_array,  cv2.COLOR_RGB2BGR)
        vid.write(frame)
    vid.release()
    cv2.destroyAllWindows()


def _convert_pixbuf_to_numpy(pixbuf):
    w, h, c, r = (pixbuf.get_width(), pixbuf.get_height(), pixbuf.get_n_channels(), pixbuf.get_rowstride())
    a = np.frombuffer(pixbuf.get_pixels(), dtype=np.uint8)
    if a.shape[0] == w * c * h:
        return a.reshape((h, w, c))
    else:
        b = np.zeros((h, w * c), 'uint8')
        for j in range(h):
            b[j, :] = a[r * j:r * j + w * c]
        return b.reshape((h, w, c))
