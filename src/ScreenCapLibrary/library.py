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

from .version import VERSION
from .client import Client

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


    For video recording, [https://github.com/skvark/opencv-python/blob/master/README.md | OpenCV-Python] is used and
    the output file is in WebM format.

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

    def __init__(self, screenshot_module=None, screenshot_directory=None, format='png', quality=50, delay=0, fps=8):
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
        self._client = Client(
            screenshot_module=screenshot_module,
            screenshot_directory=screenshot_directory,
            format=format,
            quality=quality,
            delay=delay,
            fps=fps
        )

    def set_screenshot_directory(self, path):
        """Sets the directory where screenshots are saved.

        It is possible to use ``/`` as a path separator in all operating
        systems. Path to the old directory is returned.

        The directory can also be set in `importing`.
        """
        return self._client.set_screenshot_directory(path)

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
        | `Take Screenshot` |                  |            | # LOGDIR/screenshot_1.png (index automatically incremented) |
        | `Take Screenshot` | mypic            |            | # LOGDIR/mypic_1.png (index automatically incremented) |
        | `Take Screenshot` | ${TEMPDIR}/mypic |            | # /tmp/mypic_1.png (index automatically incremented) |
        | `Take Screenshot` | pic.jpg          |            | # LOGDIR/pic.jpg (always uses this file) |
        | `Take Screenshot` | images/login.jpg | 300px      | # Specify both name and width. |
        | `Take Screenshot` | width=550px      |            | # Specify only width. |
        | `Take Screenshot` | format=jpg       | quality=15 | # Specify both image format and quality |

        The path where the screenshot is saved is returned.
        """
        return self._client.take_screenshot(name, format, quality, width, delay)

    def start_gif_recording(self, name="screenshot", size_percentage=0.5,
                            embed=True, embed_width='800px'):
        """
        Starts the recording of a GIF in the background with the specified ``name``.
        The recording can be stopped by calling the `Stop Gif Recording` keyword.

        ``name`` specifies the name by which the screenshot will be saved.

        ``size_percentage`` is used to reduce the size of the GIFs a resize of the
        screencaptures. It will specify how much this reduction is with respect to
        screen resolution. By default this parameter is set to resize the images to
        0.5 of the screen resolution.

        ``embed`` specifies if the screenshot should be embedded in the log file
        or not. See `Boolean arguments` section for more details.

        ``embed_width`` specifies the size of the screenshot that is
        embedded in the log file.

        Examples:
        | `Start Gif Recording` |            |  # Starts the GIF recording in background |
        | `Sleep`               | 10 seconds |  # Here should be the actions that will be recorded |
        | `Stop Gif Recording`  |            |  # Will create the GIF containing the screen recording \
        since `Start Gif Recording` was called. |
        """
        return self._client.start_gif_recording(name, size_percentage, embed, embed_width)

    def stop_gif_recording(self):
        """
        Stops the GIF recording and generates the file. If ``embed`` argument was set to ``True`` the
        GIF will be displayed in the log file.
        """
        self._client.stop_gif_recording()

    def take_partial_screenshot(self, name='screenshot', format=None, quality=None,
                                left=0, top=0, width=700, height=300, embed=True, embed_width='800px'):
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
        return self._client.take_partial_screenshot(name, format, quality,
                                                    left, top, width, height, embed, embed_width)

    def take_screenshot_without_embedding(self, name="screenshot", format=None, quality=None, delay=0):
        """Takes a screenshot and links it from the log file.
        This keyword is otherwise identical to `Take Screenshot` but the saved
        screenshot is not embedded into the log file. The screenshot is linked
        so it is nevertheless easily available.
        """
        return self._client.take_screenshot_without_embedding(name, format, quality, delay)

    def take_multiple_screenshots(self, name="screenshot", format=None, quality=None,
                                  screenshot_number=2, delay_time=0):
        """Takes the specified number of screenshots in the specified format
        at library import and embeds it into the log file (PNG by default).

        This keyword is similar with `Take Screenshot` but has some extra
        parameters listed below:

        ``screenshot_number`` specifies the number of screenshots to be taken.
        By default this number is 2.

        ``delay_time`` specifies the waiting time before taking another
        screenshot. See `Time format` section for more information. By
        default the delay time is 0.
        """
        return self._client.take_multiple_screenshots(name, format, quality, screenshot_number, delay_time)

    def start_video_recording(self, name="recording", fps=8, embed=True, embed_width='800px'):
        """Starts the recording of a video in the background with the specified ``name``.
        The recording can be stopped by calling the `Stop Video Recording` keyword.

        ``name`` specifies the name by which the record will be saved.

        ``fps`` specifies the frame rate at which the video is displayed.
        By default frame rate is 8.

        ``embed`` specifies if the record should be embedded in the log file
        or not. See `Boolean arguments` section for more details.

        ``embed_width`` specifies the size of the video record that is
        embedded in the log file.

        Examples:
        | `Start Video Recording` |            |  # Starts the video recording in background |
        | `Sleep`                 | 10 seconds |  # Here should be the actions that will be recorded |
        | `Stop Video Recording`  |            |  # Will create the video containing the screen recording \
        since `Start Video Recording` was called. |
        """
        return self._client.start_video_recording(name, fps, embed, embed_width)

    def stop_video_recording(self):
        """Stops the video recording and generates the file in WebM format. If ``embed`` argument
        was set to ``True`` the video will be displayed in the log file.
        """
        self._client.stop_video_recording()
