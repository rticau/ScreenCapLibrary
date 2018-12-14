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
from .version import VERSION
from .pygtk import _take_gtk_screenshot, _take_gtk_screen_size


from mss import mss
from PIL import Image
from robot.api import logger

from robot.utils import get_link_path, abspath, timestr_to_secs, is_truthy
from robot.libraries.BuiltIn import BuiltIn
from .version import VERSION
from .pygtk import _take_gtk_screenshot, _take_partial_gtk_screenshot, _take_gtk_screen_size

__version__ = VERSION


class ScreenCapLibrary:
    """ Test Library for taking screenshots on the machine where tests are run.

    Note that successfully taking screenshots requires tests to be run with
    a physical or virtual display.

    = Usage =

    How screenshots are taken when using Python depends on the chosen format.
    There are several supported formats: PNG, JPG/JPEG, GIF and WebP. If no format
    is specified the screenshots will have the PNG format.

    For taking screenshots the following modules are used:

    - [https://python-mss.readthedocs.io| mss ] a fast cross-platform module used for taking screenshots and saving
     them in PNG format.

    - [https://pillow.readthedocs.io | Pillow] used on top of ``mss`` in order to save the screenshots in JPG/JPEG/WebP format.

    - [http://pygtk.org/ | PyGTK] is an alternative to ``mss`` for taking screenshots when using VNC.

    = Where screenshots are saved =

    By default screenshots are saved into the same directory where the Robot
    Framework log file is written. If no log is created, screenshots are
    saved into the directory where the XML output file is written.

    It is possible to specify a custom location for screenshots using
    ``screenshot_directory`` argument when `importing` the library and using
    `Set Screenshot Directory` keyword during execution. It is also possible
    to save screenshots using an absolute path.

    = Time format =

    All delays and time intervals can be given as numbers considered seconds
    (e.g. ``0.5`` or ``42``) or in Robot Framework's time syntax
    (e.g. ``1.5 seconds`` or ``1 min 30 s``). For more information about
    the time syntax see the
    [http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#time-format|Robot Framework User Guide].

    = Boolean arguments =

    Some keywords accept arguments that are handled as Boolean values true or
    false. If such an argument is given as a string, it is considered false if
    it is either an empty string or case-insensitively equal to ``false``,
    ``none`` or ``no``. Other strings are considered true regardless
    their value, and other argument types are tested using the same
    [http://docs.python.org/2/library/stdtypes.html#truth-value-testing|rules
    as in Python].

    True examples:
    | `Take Partial Screenshot` | embed=True    | # Strings are generally true.    |
    | `Take Partial Screenshot` | embed=yes     | # Same as the above.             |
    | `Take Partial Screenshot` | embed=${TRUE} | # Python ``True`` is true.       |
    | `Take Partial Screenshot` | embed=${42}   | # Numbers other than 0 are true. |
    False examples:
    | `Take Partial Screenshot` | embed=False    | # String ``false`` is false.   |
    | `Take Partial Screenshot` | embed=no       | # Also string ``no`` is false. |
    | `Take Partial Screenshot` | embed=${EMPTY} | # Empty string is false.       |
    | `Take Partial Screenshot` | embed=${FALSE} | # Python ``False`` is false.   |
    """

    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self, screenshot_module=None, screenshot_directory=None, format='png', quality=50, delay=0):
        """
        ``screenshot_module`` specifies the module or tool to use when taking screenshots using this library.
        If no tool or module is specified, ``mss`` will be used by default. For running
        on Linux with VNC, use ``PyGTK``.

        To configure where screenshots are saved use ``screenshot_directory``. If no value is given,
        screenshots are saved into same directory as the log file. The directory can also be set using
        `Set Screenshot Directory` keyword.

        ``format`` specifies the format in which the screenshots will be saved.
        Possible values are ``png``,  ``jpeg``, ``jpg`` and ``webp``, case-insensitively.
        If no value is given the format is set by default to ``png``.

        ``quality`` can take values in range [0, 100]. Value 0 is lowest quality,
        while value 100 is maximum quality. The quality is directly proportional
        with file size. Because PNG uses lossless compression its size
        may be larger than the size of the JPG file. The default value is 50.

        ``delay`` specifies the waiting time before taking a screenshot. See
        `Time format` section for more information. By default the delay is 0.

        Examples (use only one of these):
        | =Setting= |  =Value=   |  =Value=                        |
        | Library   | Screenshot |                                 |
        | Library   | Screenshot | PyGTK                           |
        | Library   | Screenshot | screenshot_directory=${TEMPDIR} |
        | Library   | Screenshot | format=jpg                      |
        | Library   | Screenshot | quality=0                       |

        """
        self._screenshot_module = screenshot_module
        self._given_screenshot_dir = self._norm_path(screenshot_directory)
        self._format = format
        self._quality = quality
        self._delay = delay

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
        if basename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
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

    def _take_webp_screenshot(self, name, format, quality):
        with mss() as sct:
            sct_img = sct.grab(sct.monitors[0])
            img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
            path = self._save_screenshot_path(name, format)
            img.save(path, quality=quality)
        return path

    def _take_screenshot(self, name, format, quality):
        format = (format or self._format).lower()
        quality = quality or self._quality
        if self._screenshot_module and self._screenshot_module.lower() == 'pygtk':
            format = 'jpeg' if format == 'jpg' else format
            if format == 'png':
                quality = self._compression_value_conversion(quality)
            path = self._save_screenshot_path(name, format)
            if format == 'webp':
                png_img = _take_gtk_screenshot(path, 'png', self._compression_value_conversion(100))
                im = Image.open(png_img)
                im.save(path, format, quality=quality)
                return path
            return _take_gtk_screenshot(path, format, quality)
        else:
            if format == 'png':
                return self._take_png_screenshot(name, format, quality)
            elif format in ['jpg', 'jpeg']:
                return self._take_jpg_screenshot(name, format, quality)
            elif format == 'webp':
                return self._take_webp_screenshot(name, format, quality)
            else:
                raise RuntimeError("Invalid screenshot format.")

    def take_gif(self, name="screenshot", duration=10, frame_time=100, size_percentage=0.25,
                            embed=None, embed_width='800px'):
        """
        Takes a GIF with the specified ``name``.

        ``name`` specifies the name by which the screenshot will be saved.

        ``duration`` specifies the time (seconds) in which the screen will be captured.
        Default value for this parameter is 10.

        ``frame_time`` When replaying a GIF this parameter indicates how much time (milliseconds)
        will pass until switching to another frame of the GIF.

        ``size_percentage`` is used to reduce the size of the GIFs a resize of the
        screencaptures. It will specify how much this reduction is with respect to
        screen resolution. By default this parameter is set to resize the images to
        0.25 of the screen resolution.

        ``embed`` specifies if the screenshot should be embedded in the log file
        or not. See `Boolean arguments` section for more details.

        ``embed_width`` specifies the size of the screenshot that is
        embedded in the log file.
        """
        frames = []
        start_time = time.time()
        if self._screenshot_module and self._screenshot_module.lower() == 'pygtk':
            width, height = _take_gtk_screen_size()
            gif_width = int(width * size_percentage)
            gif_height = int(height * size_percentage)
            quality = self._compression_value_conversion(100)
            while time.time() <= start_time + int(duration):
                path = self._save_screenshot_path(name + repr(time.time()), 'png')
                pygtk_img = _take_gtk_screenshot(path, 'png', quality)
                im = Image.open(pygtk_img).resize((gif_width, gif_height))
                frames.append(im)
                os.remove(pygtk_img)
        else:
            with mss() as sct:
                gif_width = int(sct.grab(sct.monitors[0]).size.width * size_percentage)
                gif_height = int(sct.grab(sct.monitors[0]).size.height * size_percentage)
                while time.time() <= start_time + int(duration):
                    sct_img = sct.grab(sct.monitors[0])
                    img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX').resize((gif_width, gif_height))
                    frames.append(img)
        path = self._save_screenshot_path(basename=name, format='gif')
        frames[0].save(path, save_all=True, append_images=frames[1:], optimize=True, duration=frame_time, loop=0)
        if is_truthy(embed):
            self._embed_screenshot(path, embed_width)
        return path

    def take_screenshot(self, name='screenshot', format=None, quality=None, width='800px', delay=0):
        """Takes a screenshot in the specified format at library import and
        embeds it into the log file (PNG by default).

        Name of the file where the screenshot is stored is derived from the
        given ``name``. If the ``name`` ends with extension ``.jpg``, ``.jpeg``,
        ``.png`` or ``.webp``, the screenshot will be stored with that exact name.
        Otherwise a unique name is created by adding an underscore, a running
        index and an extension to the ``name``.

        The name will be interpreted to be relative to the directory where
        the log file is written. It is also possible to use absolute paths.
        Using ``/`` as a path separator works in all operating systems.

        ``format`` specifies the format in which the screenshot is saved. If
        no format is provided the library import value will be used which is
        ``png`` by default. Can be either ``jpg``, ``jpeg``, ``png``, or ``webp``,
        case insensitive.

        ``quality`` can take values in range [0, 100]. In case of JPEG format
        it can drastically reduce the file size of the image.

        ``width`` specifies the size of the screenshot in the log file.

        ``delay`` specifies the waiting time before taking a screenshot. See
        `Time format` section for more information. By default the delay is 0.

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
        delay = delay or self._delay
        if delay:
            time.sleep(timestr_to_secs(delay))
        path = self._take_screenshot(name, format, quality)
        self._embed_screenshot(path, width)
        return path

    def take_partial_screenshot(self, name='screenshot', format=None, quality=None,
                                left=0, top=0, width=700, height=300, embed=False, embed_width='800px'):
        """
        Takes a partial screenshot in the specified format and dimensions at
        library import and embeds it into the log file (PNG by default).

        This keyword is similar with `Take Screenshot` but has some extra parameters listed below:.

        ``left`` specifies the cropping distance on the X axis from the left of the screen capture.

        ``top`` specifies the cropping distance on the Y axis from the top of the screen capture.

        ``width`` specifies the width of a screen capture when using partial screen captures.

        ``height`` specifies the height of a screen capture when using partial screen captures.

        ``embed`` specifies if the screenshot should be embedded in the log file or not. See
        `Boolean arguments` section for more details.

        ``embed_width`` specifies the size of the screenshot that is embedded in the log file.
         """
        left = int(left)
        top = int(top)
        width = int(width)
        height = int(height)
        format = (format or self._format).lower()
        quality = quality or self._quality

        if self._screenshot_module and self._screenshot_module.lower() == 'pygtk':
            format = 'jpeg' if format == 'jpg' else format
            if format == 'png':
                quality = self._compression_value_conversion(quality)
            path = self._save_screenshot_path(name, format)
            path = _take_partial_gtk_screenshot(path, format, quality, left, top, width, height)
        else:
            try:
                original_image = self.take_screenshot(name, format, quality)
                image = Image.open(original_image)
                box = (left, top, width, height)
                cropped_image = image.crop(box)
            except IOError:
                raise IOError('File not found.')
            except RuntimeError:
                raise RuntimeError('Taking screenshot failed.')
            except SystemError:
                raise SystemError("Top and left parameters must be lower than screen resolution.")
            os.remove(original_image)
            path = self._save_screenshot_path(basename=name, format=format)
            cropped_image.save(path, format)
        if is_truthy(embed):
            self._embed_screenshot(path, embed_width)
        return path

    def _embed_screenshot(self, path, width):
        link = get_link_path(path, self._log_dir)
        logger.info('<a href="%s"><img src="%s" width="%s"></a>' % (link, link, width), html=True)

    def take_screenshot_without_embedding(self, name="screenshot", format=None, quality=None, delay=0):
        """Takes a screenshot and links it from the log file.
        This keyword is otherwise identical to `Take Screenshot` but the saved
        screenshot is not embedded into the log file. The screenshot is linked
        so it is nevertheless easily available.
        """
        delay = delay or self._delay
        if delay:
            time.sleep(timestr_to_secs(delay))
        path = self._take_screenshot(name, format, quality)
        self._link_screenshot(path)
        return path

    def _link_screenshot(self, path):
        link = get_link_path(path, self._log_dir)
        logger.info("Screenshot saved to '<a href=\"%s\">%s</a>'." % (link, path), html=True)

    def take_multiple_screenshots(self, name="screenshot", format=None, quality=None, screenshot_number=2, delay_time=0,
                                  embed=None, embed_width='800px'):
        """Takes the specified number of screenshots in the specified format
        at library import and embeds it into the log file (PNG by default).

        This keyword is similar with `Take Screenshot` but has some extra
        parameters listed below:

        ``screenshot_number`` specifies the number of screenshots to be taken.
        By default this number is 2.

        ``delay_time`` specifies the waiting time before taking another
        screenshot. See `Time format` section for more information. By
        default the delay time  is 0.

        ``embed`` specifies if the screenshot should be embedded in the log file
        or not. See `Boolean arguments` section for more details.

        ``embed_width`` specifies the size of the screenshot that is
        embedded in the log file.
        """
        paths = []
        try:
            for i in range(int(screenshot_number)):
                path = self.take_screenshot(name, format, quality)
                if delay_time:
                    time.sleep(timestr_to_secs(delay_time))
                paths.append(path)
                if is_truthy(embed):
                    self._embed_screenshot(path, embed_width)
        except ValueError:
            raise RuntimeError("Screenshot number argument must be of type integer.")
        return paths
