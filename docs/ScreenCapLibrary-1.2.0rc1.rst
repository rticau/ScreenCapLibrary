==========================================
ScreenCapLibrary 1.2.0 Release Candidate 1
==========================================


.. default-role:: code


ScreenCapLibrary is a `Robot Framework`_ test library for taking screenshots on the machine where tests are run.
ScreenCapLibrary 1.2.0rc1 is a new release with WebP support and several other enhancements.
All issues targeted for ScreenCapLibrary v1.2.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-screencaplibrary

to install the latest release or use

::

   pip install robotframework-screencaplibrary==1.2.0rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

ScreenCapLibrary 1.2.0rc1 was released on Friday December 14, 2018.

.. _Robot Framework: http://robotframework.org
.. _ScreenCapLibrary: https://github.com/mihaiparvu/ScreenCapLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-screencaplibrary
.. _issue tracker: https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.2.0


.. contents::
   :depth: 2
   :local:

Most important update
=====================

- The most important issue is the WebP screenshot format support (`#3`_, rc 1).

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#8`_
      - enhancement
      - medium
      - Possibility to take gifs
      - rc 1
    * - `#6`_
      - enhancement
      - medium
      - Take partial screen capture
      - rc 1
    * - `#5`_
      - enhancement
      - medium
      - Take multiple screenshots
      - rc 1
    * - `#4`_
      - enhancement
      - medium
      - Take screenshot after delay
      - rc 1
    * - `#3`_
      - enhancement
      - high
      - Add support for WebP screenshot format
      - rc 1

Altogether 5 issues. View on the `issue tracker <https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.2.0>`__.

.. _#8: https://github.com/mihaiparvu/ScreenCapLibrary/issues/8
.. _#6: https://github.com/mihaiparvu/ScreenCapLibrary/issues/6
.. _#5: https://github.com/mihaiparvu/ScreenCapLibrary/issues/5
.. _#4: https://github.com/mihaiparvu/ScreenCapLibrary/issues/4
.. _#3: https://github.com/mihaiparvu/ScreenCapLibrary/issues/3
