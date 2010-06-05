#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

import setuptools


def is_babel_available():
    try:
        import babel
    except ImportError:
        return False
    return True

def commands_for_babel_support():
    if not is_babel_available():
        print 'not available'
        return {}
    from babel.messages import frontend as babel
    
    extra_commands = {
        'extract_messages': babel.extract_messages,
        'init_catalog':     babel.init_catalog,
        'update_catalog':   babel.update_catalog,
        'compile_catalog':  babel.compile_catalog,
    }
    return extra_commands

if __name__ == '__main__':
    execfile(os.path.join('pycerberus', 'release.py'))
    
    extra_commands = commands_for_babel_support()
    
    setuptools.setup(
          name=name,
          version=version,

          description=description,
          long_description=long_description,
          author=author,
          author_email=email,
          url=url,
          download_url=download_url,
          license=license,
          
          extras_require = {
              'Babel': ['Babel>=0.9.5'],
          },
            
          zip_safe=True,
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
    )


