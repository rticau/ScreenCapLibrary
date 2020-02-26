==========================================
ScreenCapLibrary 1.3.2 Release Candidate 1
==========================================


.. default-role:: code


ScreenCapLibrary is a `Robot Framework`_ test library for taking screenshots on the machine where tests are run.
ScreenCapLibrary 1.3.2rc1 is a hotfix release that fixes a problem when recording tests that log messages with 
WARN level.
All issues targeted for ScreenCapLibrary v1.3.2 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework-screencaplibrary

to install the latest release or use

::

   pip install robotframework-screencaplibrary==1.3.2rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

ScreenCapLibrary 1.3.2rc1 was released on Wednesday February 26, 2020.

.. _Robot Framework: http://robotframework.org
.. _ScreenCapLibrary: https://github.com/mihaiparvu/ScreenCapLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-screencaplibrary
.. _issue tracker: https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.3.2


.. contents::
   :depth: 2
   :local:

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#40`_
      - bug
      - medium
      - ValueError: I/O operation on closed file.
      - rc 1

Altogether 1 issues. View on the `issue tracker <https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.3.2>`__.

.. _#40: https://github.com/mihaiparvu/ScreenCapLibrary/issues/40
