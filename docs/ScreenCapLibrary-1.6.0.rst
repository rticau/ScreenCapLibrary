======================
ScreenCapLibrary 1.6.0
======================


.. default-role:: code


ScreenCapLibrary is a `Robot Framework`_ test library for taking screenshots on the machine where tests are run.
ScreenCapLibrary 1.6.0 is a new release with possibility to embed screenshots/videos directly into log.html and
several other enhancements and bug fixes.
All issues targeted for ScreenCapLibrary v1.6.0 can be found from
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework-screencaplibrary

to install the latest release or use

::

   pip install robotframework-screencaplibrary==1.6.0

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually.

ScreenCapLibrary 1.6.0 was released on Monday February 21, 2022.

.. _Robot Framework: http://robotframework.org
.. _ScreenCapLibrary: https://github.com/mihaiparvu/ScreenCapLibrary
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework-screencaplibrary
.. _issue tracker: https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.6.0


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
    * - `#71`_
      - enhancement
      - medium
      - Add possibilty to embed screenshots directly into log.html
    * - `#68`_
      - enhancement
      - low
      - Capsulate events to videoclient and eliminate busy loops

Altogether 2 issues. View on the `issue tracker <https://github.com/mihaiparvu/ScreenCapLibrary/issues?q=milestone%3Av1.6.0>`__.

.. _#71: https://github.com/mihaiparvu/ScreenCapLibrary/issues/71
.. _#68: https://github.com/mihaiparvu/ScreenCapLibrary/issues/68
