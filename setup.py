#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

import setuptools

from pycerberus.distribution_helpers import commands_for_babel_support, information_from_file


if __name__ == '__main__':
    extra_commands = commands_for_babel_support()
    externally_defined_parameters= information_from_file(os.path.join('pycerberus', 'release.py'))
    
    setuptools.setup(
          extras_require = {
              'Babel': ['Babel>=0.9.5'],
          },
          
          # simple_super is not zip_safe, neither is the current gettext 
          # implementation
          zip_safe=False,
          packages=setuptools.find_packages(),
          classifiers = (
              'Development Status :: 4 - Beta',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: MIT License',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Topic :: Software Development :: Libraries :: Python Modules',
          ),
          test_suite = 'nose.collector',
          cmdclass=extra_commands,
          **externally_defined_parameters
    )


