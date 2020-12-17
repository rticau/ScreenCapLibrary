======================
ScreenCapLibrary 1.5.0
======================


.. default-role:: code


ScreenCapLibrary is a `Robot Framework`_ test library for taking screenshots on the machine where tests are run.
ScreenCapLibrary 1.5.0 is a new release with support for pausing and resuming video captures, displaying cursor
and several enhancements and bug fixes.
All issues targeted for ScreenCapLibrary v1.5.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-screencaplibrary

to install the latest release or use

::

   pip install robotframework-screencaplibrary==1.5.0

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

ScreenCapLibrary 1.5.0 was released on Thursday December 17, 2020.

.. _Robot Framework: http://robotframework.org
.. _ScreenCapLibrary: https://github.com/mihaiparvu/ScreenCapLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-screencaplibrary
.. _issue tracker: https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.5.0


.. contents::
   :depth: 2
   :local:

Acknowledgements
================

Thank you for your great contribution:

- @davesliu: Display mouse cursor during the video recording (`#50`_, rc 1)

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#50`_
      - enhancement
      - medium
      - Display mouse cursor during the video recording
      - rc 1
    * - `#56`_
      - bug
      - medium
      - redundant embedded snapshot when using take_partial_screenshot
      - rc 1
    * - `#63`_
      - enhancement
      - medium
      - Add Pause/Resume keywords
      - rc 1


Altogether 3 issues. View on the `issue tracker <https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.5.0>`__.

.. _#50: https://github.com/mihaiparvu/ScreenCapLibrary/issues/50
.. _#56: https://github.com/mihaiparvu/ScreenCapLibrary/issues/56
.. _#63: https://github.com/mihaiparvu/ScreenCapLibrary/issues/63
