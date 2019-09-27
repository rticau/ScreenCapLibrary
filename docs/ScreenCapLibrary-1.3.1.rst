======================
ScreenCapLibrary 1.3.1
======================


.. default-role:: code


ScreenCapLibrary is a `Robot Framework`_ test library for taking screenshots on the machine where tests are run.
ScreenCapLibrary 1.3.1 is a new release with possibility for recording multiple instances of videos at the same
time, option to resize video captures, and smaller fixes and enhancements.
All issues targeted for ScreenCapLibrary v1.3.1 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework-screencaplibrary

to install the latest release or use

::

   pip install robotframework-screencaplibrary==1.3.1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

ScreenCapLibrary 1.3.1 was released on Friday September 27, 2019.

.. _Robot Framework: http://robotframework.org
.. _ScreenCapLibrary: https://github.com/mihaiparvu/ScreenCapLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-screencaplibrary
.. _issue tracker: https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.3.1


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

The nested video recording usage (`#28`_) allows the recording of multiple clips in parallel. You
can specify which video to stop recording by using the ``alias`` argument, given when calling
both ``Start Video Recording`` and ``Stop Video Recording`` keywords.

Another major enhancement is the possibility to resize the video captures (`#25`_) by using
``size_percentage`` argument.

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#28`_
      - enhancement
      - high
      - Nested video recording usage
    * - `#25`_
      - enhancement
      - medium
      - Return path for keywords
    * - `#29`_
      - enhancement
      - medium
      - Add size_percentage for video recording 

Altogether 3 issues. View on the `issue tracker <https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.3.1>`__.

.. _#28: https://github.com/mihaiparvu/ScreenCapLibrary/issues/28
.. _#25: https://github.com/mihaiparvu/ScreenCapLibrary/issues/25
.. _#29: https://github.com/mihaiparvu/ScreenCapLibrary/issues/29
