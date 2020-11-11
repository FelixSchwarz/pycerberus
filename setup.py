#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
from __future__ import absolute_import, unicode_literals

from distutils.command.build import build
import os

import setuptools
from setuptools.command.install_lib import install_lib


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def i18n_aware_commands():
    def is_babel_available():
        try:
            import babel
        except ImportError:
            return False
        return True

    def commands_for_babel_support():
        if not is_babel_available():
            return {}
        from babel.messages import frontend as babel
        return {
            'extract_messages': babel.extract_messages,
            'init_catalog':     babel.init_catalog,
            'update_catalog':   babel.update_catalog,
            'compile_catalog':  babel.compile_catalog,
        }

    if not is_babel_available():
        # setup(..., cmdclass={}) will use just the built-in commands
        return dict()

    class i18n_build(build):
        sub_commands = [('compile_catalog', None)] + build.sub_commands

    # before doing an 'install' (which can also be a 'bdist_egg'), compile the catalog
    class i18n_install_lib(install_lib):
        def run(self):
            self.run_command('compile_catalog')
            install_lib.run(self)
    command_dict = dict(build=i18n_build, install_lib=i18n_install_lib)
    command_dict.update(commands_for_babel_support())
    return command_dict


if __name__ == '__main__':
    extra_commands = i18n_aware_commands()
    setuptools.setup(
        long_description=(read('README.md') + read('Changelog.txt')),
        cmdclass=extra_commands,
    )


