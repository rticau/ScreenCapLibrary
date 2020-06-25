#!/usr/bin/env python

import re
import sys
from os.path import abspath, dirname, join
from setuptools import setup

CURDIR = dirname(abspath(__file__))
REQUIREMENTS = ['robotframework >= 3.0', 'mss >= 3.2.1', 'pillow >= 5.2.0', 'opencv-python >= 4.0.0.21',
                'imageio==2.6.1']
with open(join(CURDIR, 'src', 'ScreenCapLibrary', 'version.py')) as f:
    VERSION = re.search("\nVERSION = '(.*)'", f.read()).group(1)
with open(join(CURDIR, 'README.rst')) as f:
    DESCRIPTION = f.read()
if sys.version_info[0] < 3:
    REQUIREMENTS.append('futures >= 3.2.0')
CLASSIFIERS = '''
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Topic :: Software Development :: Testing
Framework :: Robot Framework
Framework :: Robot Framework :: Library
'''.strip().splitlines()

setup(
    name='robotframework-screencaplibrary',
    version=VERSION,
    description='Robot Framework test library for taking screenshots',
    long_description=DESCRIPTION,
    author=u'Mihai Pârvu',
    author_email='mihai-catalin.parvu@nokia.com',
    url='https://github.com/mihaiparvu/ScreenCapLibrary',
    license='Apache License 2.0',
    keywords='robotframework testing testautomation screenshot screencap',
    platforms='any',
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    package_dir={'': 'src'},
    packages=['ScreenCapLibrary']
)
