==========================================
ScreenCapLibrary 1.3.0 Release Candidate 2
==========================================


.. default-role:: code


ScreenCapLibrary is a `Robot Framework`_ test library for taking screenshots and recordings on the machine
where tests are run.
ScreenCapLibrary 1.3.0rc2 is a new release with WebM video capture support and background capturing. The
release candidate 2 contains some small fixes when capturing using pygtk module and documentation enhancements.
All issues targeted for ScreenCapLibrary v1.3.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-screencaplibrary

to install the latest release or use

::

   pip install robotframework-screencaplibrary==1.3.0rc2

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

ScreenCapLibrary 1.3.0rc2 was released on Wednesday May 29, 2019.

.. _Robot Framework: http://robotframework.org
.. _ScreenCapLibrary: https://github.com/mihaiparvu/ScreenCapLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-screencaplibrary
.. _issue tracker: https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.3.0


.. contents::
   :depth: 2
   :local:

Most important update
=====================

- The most important issue is the WebM video capture support (`#20`_, rc 1).

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#20`_
      - enhancement
      - high
      - Possibility for video screen capture
      - rc 1
    * - `#18`_
      - enhancement
      - high
      - Run keywords in background
      - rc 1

Altogether 2 issues. View on the `issue tracker <https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.3.0>`__.

.. _#20: https://github.com/mihaiparvu/ScreenCapLibrary/issues/20
.. _#18: https://github.com/mihaiparvu/ScreenCapLibrary/issues/18
