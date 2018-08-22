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
from mss import mss
from PIL import Image
from robot.api import logger
from robot.utils import get_link_path, abspath
from robot.libraries.BuiltIn import BuiltIn
from .version import VERSION

__version__ = VERSION


class ScreenCapLibrary:
    """ Test Library for taking screenshots on the machine where tests are run.

    Note that successfully taking screenshots requires tests to be run with
    a physical or virtual display.

    = Usage =

    How screenshots are taken when using Python depends on the chosen format.
    There are two formats supported: PNG and JPG/JPEG. If no format is specified
    the screenshots will have the PNG format.

    For taking screenshots the following modules are used:

    - [https://python-mss.readthedocs.io| mss ] a fast cross-platform module used for taking screenshots and saving
     them in PNG format.

    - [https://pillow.readthedocs.io | Pillow] used on top of ``mss`` in order to save the screenshots in JPG/JPEG format.

    = Where screenshots are saved =

    By default screenshots are saved into the same directory where the Robot
    Framework log file is written. If no log is created, screenshots are
    saved into the directory where the XML output file is written.

    It is possible to specify a custom location for screenshots using
    ``screenshot_directory`` argument when `importing` the library and using
    `Set Screenshot Directory` keyword during execution. It is also possible
    to save screenshots using an absolute path.
    """

    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self, screenshot_directory=None, format='png', quality=50):
        """Configure where screenshots are saved.

        If ``screenshot_directory`` is not given, screenshots are saved into
        same directory as the log file. The directory can also be set using
        `Set Screenshot Directory` keyword.

        ``format`` specifies the format in which the screenshots will be saved.
        Possible values are ``png``,  ``jpeg`` and ``jpg``, case-insensitively.
        If no value is given the format is set by default to ``png``.

        ``quality`` can take values in range [0, 100]. Value 0 is lowest quality,
        while value 100 is maximum quality. The quality is directly proportional
        with file size. Because PNG uses lossless compression its size
        may be larger than the size of the JPG file. The default value is 50.

        Examples (use only one of these):
        | =Setting= |  =Value=   |  =Value=   |
        | Library   | Screenshot |            |
        | Library   | Screenshot | ${TEMPDIR} |
        | Library   | Screenshot | format=jpg |
        | Library   | Screenshot | quality=0  |
        """
        self._given_screenshot_dir = self._norm_path(screenshot_directory)
        self._format = format
        self._quality = quality

    @staticmethod
    def _norm_path(path):
        if not path:
            return path
        return os.path.normpath(path.replace('/', os.sep))

    @property
    def _screenshot_dir(self):
        return self._given_screenshot_dir or self._log_dir

    @property
    def _log_dir(self):
        variables = BuiltIn().get_variables()
        outdir = variables['${OUTPUTDIR}']
        log = variables['${LOGFILE}']
        log = os.path.dirname(log) if log != 'NONE' else '.'
        return self._norm_path(os.path.join(outdir, log))

    def set_screenshot_directory(self, path):
        """Sets the directory where screenshots are saved.

        It is possible to use ``/`` as a path separator in all operating
        systems. Path to the old directory is returned.

        The directory can also be set in `importing`.
        """
        path = self._norm_path(path)
        if not os.path.isdir(path):
            raise RuntimeError("Directory '%s' does not exist." % path)
        old = self._screenshot_dir
        self._given_screenshot_dir = path
        return old

    @staticmethod
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

    @staticmethod
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

    def _get_screenshot_path(self, basename, format, directory):
        directory = self._norm_path(directory) if directory else self._screenshot_dir
        if basename.lower().endswith(('.jpg', '.jpeg', '.png')):
            return os.path.join(directory, basename)
        index = 0
        while True:
            index += 1
            path = os.path.join(directory, "%s_%d.%s" % (basename, index, format))
            if not os.path.exists(path):
                return path

    def _validate_screenshot_path(self, path):
        path = abspath(self._norm_path(path))
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("Directory '%s' where to save the screenshot "
                               "does not exist" % os.path.dirname(path))
        return path

    def _save_screenshot_path(self, basename, format, directory=None):
        path = self._get_screenshot_path(basename, format, directory)
        return self._validate_screenshot_path(path)

    def _take_png_screenshot(self, name, format, quality):
        with mss() as sct:
            path_name = self._save_screenshot_path(name, format)
            sct.compression_level = self._compression_value_conversion(quality)
            path = sct.shot(mon=-1, output='%s' % path_name)
        return path

    def _take_jpg_screenshot(self, name, format, quality):
        with mss() as sct:
            sct_img = sct.grab(sct.monitors[0])
            img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
            path = self._save_screenshot_path(name, format)
            img.save(path, quality=self._pil_quality_conversion(quality))
        return path

    def take_screenshot(self, name='screenshot', format=None, quality=None, width='800px'):
        """Takes a screenshot in the specified format at library import and
        embeds it into the log file (PNG by default).

        Name of the file where the screenshot is stored is derived from the
        given ``name``. If the ``name`` ends with extension ``.jpg``, ``.jpeg``
        or ``.png``, the screenshot will be stored with that exact name.
        Otherwise a unique name is created by adding an underscore, a running
        index and an extension to the ``name``.

        The name will be interpreted to be relative to the directory where
        the log file is written. It is also possible to use absolute paths.
        Using ``/`` as a path separator works in all operating systems.

        ``format`` specifies the format in which the screenshot is saved. If
        no format is provided the library import value will be used which is
        ``png`` by default. Can be either ``jpg``, ``jpeg`` or ``png``, case
        insensitive.

        ``quality`` can take values in range [0, 100]. In case of JPEG format
        it can drastically reduce the file size of the image.

        ``width`` specifies the size of the screenshot in the log file.

        Examples: (LOGDIR is determined automatically by the library)
        | Take Screenshot |                  |            | # LOGDIR/screenshot_1.png (index automatically incremented) |
        | Take Screenshot | mypic            |            | # LOGDIR/mypic_1.png (index automatically incremented) |
        | Take Screenshot | ${TEMPDIR}/mypic |            | # /tmp/mypic_1.png (index automatically incremented) |
        | Take Screenshot | pic.jpg          |            | # LOGDIR/pic.jpg (always uses this file) |
        | Take Screenshot | images/login.jpg | 300px      | # Specify both name and width. |
        | Take Screenshot | width=550px      |            | # Specify only width. |
        | Take Screenshot | format=jpg       | quality=15 | # Specify both image format and quality |

        The path where the screenshot is saved is returned.
        """
        path = self._take_screenshot(name, format, quality)
        self._embed_screenshot(path, width)
        return path

    def _take_screenshot(self, name, format, quality):
        format = (format or self._format).lower()
        quality = quality or self._quality
        if format == 'png':
            path = self._take_png_screenshot(name, format, quality)
        elif format in ['jpg', 'jpeg']:
            path = self._take_jpg_screenshot(name, format, quality)
        else:
            raise RuntimeError("Invalid screenshot format.")
        return path

    def _embed_screenshot(self, path, width):
        link = get_link_path(path, self._log_dir)
        logger.info('<a href="%s"><img src="%s" width="%s"></a>' % (link, link, width), html=True)

    def take_screenshot_without_embedding(self, name="screenshot", format=None, quality=None):
        """Takes a screenshot and links it from the log file.
        This keyword is otherwise identical to `Take Screenshot` but the saved
        screenshot is not embedded into the log file. The screenshot is linked
        so it is nevertheless easily available.
        """
        path = self._take_screenshot(name, format, quality)
        self._link_screenshot(path)
        return path

    def _link_screenshot(self, path):
        link = get_link_path(path, self._log_dir)
        logger.info("Screenshot saved to '<a href=\"%s\">%s</a>'." % (link, path), html=True)
