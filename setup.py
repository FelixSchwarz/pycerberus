#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
from __future__ import absolute_import, unicode_literals

import os

import setuptools

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

if __name__ == '__main__':
    setuptools.setup(
        long_description=(read('README.md') + read('Changelog.txt')),
    )

