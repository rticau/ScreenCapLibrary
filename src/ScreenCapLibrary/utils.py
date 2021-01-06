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
import cv2
import numpy as np

cursor_x_list = [0, 8, 6, 14, 12, 4, 2, 0]
cursor_y_list = [0, 2, 4, 12, 14, 6, 8, 0]


def _norm_path(path):
    if not path:
        return path
    return os.path.normpath(path.replace('/', os.sep))


def _compression_value_conversion(value):
    """
    PNG compression values are within range [0, 9]. This value must
    be mapped to a [0-100] interval.
    """
    try:
        if int(value) < 0 or int(value) > 100:
            raise RuntimeError("Quality argument must be of between 0 and 100.")
        return 0 if int(value) == 100 else int(9 - (int(value) / 11))
    except ValueError:
        raise RuntimeError("Quality argument must be of type integer.")


def _pil_quality_conversion(value):
    """
    The quality in Pillow is between [1, 95] and must be converted to
    a [0-100] interval.
    """
    try:
        if int(value) < 0 or int(value) > 100:
            raise RuntimeError("Quality argument must be of between 0 and 100.")
        if int(value) < 1:
            return 1
        elif int(value) >= 95:
            return 95
        return int(value)
    except ValueError:
        raise RuntimeError("The image quality argument must be of type integer.")


def resize_array(width, height, numpy_array, size_percentage):
    resized_array = cv2.resize(numpy_array, dsize=(int(width * size_percentage), int(height * size_percentage)),
                               interpolation=cv2.INTER_AREA) \
        if size_percentage != 1 else numpy_array
    return resized_array


def draw_cursor(frame, mouse_x, mouse_y):
    cursor_x = [x + mouse_x for x in cursor_x_list]
    cursor_y = [y + mouse_y for y in cursor_y_list]
    cursor_points = list(zip(cursor_x, cursor_y))
    cursor_points = np.array(cursor_points, 'int32')
    cv2.fillPoly(frame, [cursor_points], color=[0, 255, 255])


def is_pygtk(screenshot_module):
    return screenshot_module and screenshot_module.lower() == 'pygtk'


class suppress_stderr(object):

    def __init__(self):
        # Open a null file
        self.null_fd = os.open(os.devnull, os.O_RDWR)
        # Save the actual stderr (2) file descriptor.
        self.save_fd = os.dup(2)

    def __enter__(self):
        # Assign the null pointer to stderr.
        os.dup2(self.null_fd, 2)

    def __exit__(self, *_):
        # Re-assign the real stderr back to (2)
        os.dup2(self.save_fd, 2)
        # Close all file descriptors
        os.close(self.null_fd)
        os.close(self.save_fd)
