ScreenCapLibrary
================

.. contents::

Introduction
------------

ScreenCapLibrary_ is a `Robot Framework`_ test
library for taking screenshots.  The project is hosted on GitHub_
and downloads can be found from PyPI_.

ScreenCapLibrary is operating system independent and supports Python_ 2.7 as well
as Python_ 3.4 or newer.

The library is based on RobotFramework's standard Screenshot_ library. It has almost
the same functionality, except that the screenshots are captured in PNG by default.

ScreenCapLibrary has the following extra features:
    - Taking screenshots in PNG, JPG/JPEG, GIF and WebP formats
    - Video capture in WebM format, embeddable in log files
    - Adjusting the compression/quality of the screenshots
    - Support for GIFs
    - Taking multiple screenshots in a given amount of time
    - Support for partial screen captures
    - Configurable monitor screen grabbing for screenshots and recording

Documentation
-------------

See `keyword documentation`_ for available keywords and more information
about the library in general.

For general information about using test libraries with Robot Framework, see
`Robot Framework User Guide`_.

Installation
------------

The recommended installation method is using pip_::

    pip install --upgrade robotframework-screencaplibrary

Running this command installs also the latest Robot Framework, mss_,
pillow_, opencv-python_ and imageio_ versions. The minimum supported mss version is
``3.2.1`` and the minimum supported pillow version is ``5.2.0``.
For video capture at least version ``4.0.0.21`` of opencv-python_ is required.
The ``--upgrade`` option can be omitted when installing the library for the
first time.

With recent versions of ``pip`` it is possible to install directly from the
GitHub_ repository. To install latest source from the master branch, use
this command::

    pip install git+https://github.com/mihaiparvu/ScreenCapLibrary.git

Alternatively you can download the source distribution from PyPI_, extract
it, and install it::

    python setup.py install

Usage
-----

To use ScreenCapLibrary in Robot Framework tests, the library needs to first be
imported using the Library setting as any other library.

When using Robot Framework, it is generally recommended to write as
easy-to-understand tests as possible.

.. code:: robotframework

    *** Settings ***
    Documentation          This example demonstrates capturing a screenshot on the local
    ...                    machine.

    Library                ScreenCapLibrary
    Library                OperatingSystem
    Test Teardown          Remove File  screenshot_1.jpg

    *** Test Cases ***
    Take A Low File Size Jpg Screenshot
        Take Screenshot    name=screenshot  format=jpg  quality=0
        File Should Exist  screenshot_1.jpg


Using with VNC
--------------

At the time of this release ``mss``, does not work on GNU/Linux with VNC virtual desktop.
As a workaround you can change the ``screenshot_module`` value at library import to ``PyGTK``.

.. code:: robotframework

    *** Settings ***
    Library                ScreenCapLibrary  screenshot_module=PyGTK

For this to work you need to have the following dependencies installed.

- With Python 2::

    sudo apt install python-gtk2

- With Python 3::

    sudo apt install python-gi python-gi-cairo python3-gi python3-gi-cairo gir1.2-gtk-3.0

Support
-------

If the provided documentation is not enough, there are various support forums
available:

- `robotframework-users`_ mailing list
- channels in Robot Framework `Slack community`_
- ScreenCapLibrary `issue tracker`_ for bug reports and concrete enhancement
  requests

.. _Robot Framework: http://robotframework.org
.. _Robot Framework User Guide: http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#using-test-libraries
.. _ScreenCapLibrary: https://github.com/mihaiparvu/ScreenCapLibrary
.. _GitHub: https://github.com/mihaiparvu/ScreenCapLibrary
.. _Python: http://python.org
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-screencaplibrary
.. _mss: https://python-mss.readthedocs.io
.. _pillow: https://pillow.readthedocs.io
.. _opencv-python: https://opencv-python-tutroals.readthedocs.io
.. _imageio: https://imageio.github.io/
.. _Screenshot: http://robotframework.org/robotframework/latest/libraries/Screenshot.html
.. _Keyword Documentation: https://mihaiparvu.github.io/ScreenCapLibrary/ScreenCapLibrary.html
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack community: https://robotframework-slack-invite.herokuapp.com
.. _issue tracker: https://github.com/mihaiparvu/ScreenCapLibrary/issues
