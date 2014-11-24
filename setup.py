#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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
    version = '0.6'
    extra_commands = i18n_aware_commands()
    setuptools.setup(
        name = 'pycerberus',
        version = version,
        description = 'Highly flexible, no magic input validation library',
        long_description=(read('description.txt') + read('Changelog.txt')),
        license = 'MIT',
        author = 'Felix Schwarz',
        author_email = 'felix.schwarz@oss.schwarz.eu',
        url = 'http://www.schwarz.eu/opensource/projects/pycerberus',
        download_url = 'http://www.schwarz.eu/opensource/projects/pycerberus/download/%(version)s/pycerberus-%(version)s.tar.gz' % dict(version=version),
        
        extras_require = {
            'Babel': ['Babel>=0.9.5'],
        },
                     
        tests_require = ['Babel'],
        test_suite = 'nose.collector',
        
        # simple_super is not zip_safe, neither is the current gettext 
        # implementation
        zip_safe=False,
        packages=setuptools.find_packages(exclude=['tests']),
        # setuptools bug when using Python 2 + unicode literals
        # It only accepts plain strings (not unicode) for package_data so we
        # need to convert these explicitely.
        # http://stackoverflow.com/a/23175194/138526
        package_data = {
            str('pycerberus'): [str('locales/*/LC_MESSAGES/pycerberus.mo')],
        },
        classifiers = (
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ),
        cmdclass=extra_commands,
    )


