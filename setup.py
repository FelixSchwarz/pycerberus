#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import setup

if __name__ == '__main__':
    setup(
        name            = 'pycerberus',
        version         = '0.1',
        description     = 'Highly flexible, no magic input validation library',
        author          = 'Felix Schwarz',
        author_email    = 'felix.schwarz@oss.schwarz.eu',
        url             = 'http://www.schwarz.eu/oss/projects/pycerberus/',
        packages        = ('pycerberus',),
        license         = 'MIT',
        
        install_requires = ('setuptools',)
    )


