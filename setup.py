#!/usr/bin/env python
"""
Scribd client library distutils setup script.

Copyright (c) 2009, Arkadiusz Wahlig <arkadiusz.wahlig@gmail.com>

Distributed under the BSD License, see the
accompanying LICENSE file for more information.
"""

from distutils.core import setup
from setup_wikidoc import *

# Import scribd distribution package.
import scribd

# start the distutils setup
setup(name='python-scribd',
      version=scribd.__version__,
      description='Scribd client library for Python.',
      long_description='A library providing a high-level object oriented interface to the scribd.com website RESTful API.',
      author='Arkadiusz Wahlig',
      author_email='arkadiusz.wahlig@gmail.com',
      url='http://code.google.com/p/python-scribd',
      license='New BSD License',
      packages=['scribd'],
      package_data={'scribd': ['LICENSE']},
      provides=['scribd'],
      cmdclass={'wikidoc': wikidoc})
