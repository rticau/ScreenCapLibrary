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
import os
import time
import numpy as np

try:
    import pyautogui
except:
    pass

from .utils import suppress_stderr, resize_array, draw_cursor
from robot.api import logger

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
    from gi import require_version

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


def _grab_screenshot_gtk_py2(monitor):
    window = gdk.get_default_root_window()
    if not window:
        raise RuntimeError('Taking screenshot failed.')
    width, height = window.get_size()
    pb = gdk.Pixbuf(gdk.COLORSPACE_RGB, False, 8, width, height)
    if not pb:
        raise RuntimeError('Taking screenshot failed.')
    if monitor == 0:
        pb = pb.get_from_drawable(window, window.get_colormap(),
                                  0, 0, 0, 0, width, height)
    else:
        monitors = _get_monitors(window)
        pb = pb.get_from_drawable(window, window.get_colormap(),
                                  monitors[monitor - 1].x, monitors[monitor - 1].y, 0, 0,
                                  monitors[monitor - 1].width, monitors[monitor - 1].height)
    return pb


def _grab_screenshot_gtk_py3(monitor):
    window = Gdk.get_default_root_window()
    if not window:
        raise RuntimeError('Taking screenshot failed.')
    if monitor == 0:
        pb = Gdk.pixbuf_get_from_window(window, 0, 0, window.get_width(), window.get_height())
    else:
        monitors = _get_monitors(window)
        pb = Gdk.pixbuf_get_from_window(window, monitors[monitor - 1].x, monitors[monitor - 1].y,
                                        monitors[monitor - 1].width, monitors[monitor - 1].height)
    if not pb:
        raise RuntimeError('Taking screenshot failed.')
    return pb


def _grab_gtk_pb(monitor):
    if not gdk and not Gdk:
        raise RuntimeError('PyGTK not installed/supported on this platform.')
    if gdk:
        return _grab_screenshot_gtk_py2(monitor)
    elif Gdk:
        return _grab_screenshot_gtk_py3(monitor)


def _take_gtk_screenshot(path, format, quality, monitor):
    if not gdk and not Gdk:
        raise RuntimeError('PyGTK not installed/supported on this platform.')
    if gdk:
        return _take_gtk_screenshot_py2(path, format, quality, int(monitor))
    elif Gdk:
        return _take_gtk_screenshot_py3(path, format, quality, int(monitor))


def _take_gtk_screenshot_py2(path, format, quality, monitor):
    pb = _grab_screenshot_gtk_py2(monitor)
    quality_setting = _gtk_quality(format, quality)
    pb.save(path, format, quality_setting)
    return path


def _take_gtk_screenshot_py3(path, format, quality, monitor):
    pb = _grab_screenshot_gtk_py3(monitor)
    quality_setting = _gtk_quality(format, quality)
    pb.savev(path, format, [list(quality_setting.keys())[0]], [list(quality_setting.values())[0]])
    return path


def _take_gtk_screen_size(monitor):
    if not gdk and not Gdk:
        raise RuntimeError('PyGTK not installed/supported on this platform.')
    window = get_default_root_window()
    if not window:
        raise RuntimeError('Taking screenshot failed.')
    if monitor == 0:
        return get_window_size(window)
    else:
        monitors = _get_monitors(window)
        return monitors[monitor - 1].width, monitors[monitor - 1].height


def get_default_root_window():
    if gdk:
        return gdk.get_default_root_window()
    elif Gdk:
        return Gdk.get_default_root_window()


def get_window_size(window):
    if gdk:
        return window.get_size()
    elif Gdk:
        return window.get_width(), window.get_height()


def _get_monitors(window):
    monitors = []
    screen = window.get_screen()
    nmons = screen.get_n_monitors()
    for m in range(nmons):
        mg = screen.get_monitor_geometry(m)
        monitors.append(mg)
    return monitors


def _take_partial_gtk_screenshot(path, format, quality, left, top, width, height, monitor):
    if not gdk and not Gdk:
        raise RuntimeError('PyGTK not installed/supported on this platform.')
    if gdk:
        return _take_partial_gtk_screenshot_py2(path, format, quality, left, top, width, height, monitor)
    elif Gdk:
        return _take_partial_gtk_screenshot_py3(path, format, quality, left, top, width, height, monitor)


def _take_partial_gtk_screenshot_py2(path, format, quality, left, top, width, height, monitor):
    source_pb = _grab_screenshot_gtk_py2(monitor)
    quality_setting = _gtk_quality(format, quality)
    cropped_pb = source_pb.subpixbuf(left, top, width, height)
    if not cropped_pb:
        raise RuntimeError('Taking screenshot failed.')
    cropped_pb.save(path, format, quality_setting)
    return path


def _take_partial_gtk_screenshot_py3(path, format, quality, left, top, width, height, monitor):
    source_pb = _grab_screenshot_gtk_py3(monitor)
    cropped_pb = source_pb.new_subpixbuf(left, top, width, height)
    if not cropped_pb:
        raise RuntimeError('Taking screenshot failed.')
    quality_setting = _gtk_quality(format, quality)
    cropped_pb.savev(path, format, [list(quality_setting.keys())[0]], [list(quality_setting.values())[0]])
    return path


def _record_gtk(path, fps, size_percentage, stop, pause, monitor, display_cursor):
    if not gdk and not Gdk:
        raise RuntimeError('PyGTK not installed/supported on this platform.')
    window = get_default_root_window()
    if not window:
        raise Exception('Monitor not available.')
    fourcc = cv2.VideoWriter_fourcc(*'VP08')
    if monitor == 0:
        width, height = get_window_size(window)
    else:
        width, height = _take_gtk_screen_size(monitor)

    with suppress_stderr():
        if not fps:
            fps = benchmark_recording_performance_gtk(width, height, size_percentage, monitor, display_cursor)
        vid = cv2.VideoWriter('%s' % path, fourcc, fps, (int(width * size_percentage), int(height * size_percentage)))
    while not stop.isSet():
        if pause.isSet():
            continue
        if gdk:
            record_gtk2(vid, width, height, size_percentage, monitor)
        elif Gdk:
            record_gtk3(vid, width, height, size_percentage, monitor, display_cursor)
    vid.release()
    cv2.destroyAllWindows()


def record_gtk2(vid, width, height, size_percentage, monitor):
    pb = _grab_screenshot_gtk_py2(monitor)
    numpy_array = pb.get_pixels_array()
    resized_array = resize_array(width, height, numpy_array, size_percentage)
    frame = cv2.cvtColor(resized_array, cv2.COLOR_RGB2BGR)
    vid.write(frame)


def record_gtk3(vid, width, height, size_percentage, monitor, display_cursor=False):
    pb = _grab_screenshot_gtk_py3(monitor)
    if display_cursor:
        mouse_x, mouse_y = pyautogui.position()
    numpy_array = _convert_pixbuf_to_numpy(pb)
    resized_array = resize_array(width, height, numpy_array, size_percentage)
    frame = cv2.cvtColor(resized_array, cv2.COLOR_RGB2BGR)
    if display_cursor:
        draw_cursor(frame, mouse_x, mouse_y)
    vid.write(frame)


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


def benchmark_recording_performance_gtk(width, height, size_percentage, monitor, display_cursor=False):
    fps = 0
    last_time = time.time()
    fourcc = cv2.VideoWriter_fourcc(*'VP08')
    # record a dummy video to compute optimal fps
    vid = cv2.VideoWriter('benchmark_%s.webm' % last_time, fourcc, 24,
                          (int(width * size_percentage), int(height * size_percentage)))
    # count the number of frames captured in 2 seconds
    while time.time() - last_time < 2:
        fps += 1
        if Gdk:
            record_gtk3(vid, width, height, size_percentage, monitor, display_cursor)
        else:
            record_gtk2(vid, width, height, size_percentage, monitor)

    vid.release()
    cv2.destroyAllWindows()
    if os.path.exists("benchmark_%s.webm" % last_time):
        os.remove('benchmark_%s.webm' % last_time)  # delete the dummy file
    logger.info('Automatically setting a fps of %s' % str(fps / 2))
    return fps / 2  # return the number of frames per second


def is_gdk():
    return Gdk
