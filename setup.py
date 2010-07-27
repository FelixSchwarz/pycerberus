#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

import setuptools

from pycerberus.lib.distribution_helpers import i18n_aware_commands, information_from_file


if __name__ == '__main__':
    extra_commands = i18n_aware_commands()
    release_filename = os.path.join('pycerberus', 'release.py')
    externally_defined_parameters = information_from_file(release_filename)
    
    setuptools.setup(
          extras_require = {
              'Babel': ['Babel>=0.9.5'],
          },
          
          # simple_super is not zip_safe, neither is the current gettext 
          # implementation
          zip_safe=False,
          packages=setuptools.find_packages(exclude=['tests']),
          package_data = {
              'pycerberus': ['locales/*/LC_MESSAGES/pycerberus.mo'],
          },
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


