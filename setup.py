#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import setuptools


# I want to define some information in the code so it's accessible at runtime
# using standard Python. The downside is that these Python files need to be
# converted to valid Python 3 code before we can load them in setup.
# As the 2to3 parameter in setuptools.setup only works *after+ this whole file
# has been parsed, the MetaDataExtractor will take care of converting some 
# special files before importing them.
class MetaDataExtractor(object):
    
    releasefile_name = os.path.join('pycerberus', 'release.py')
    preconversion_files = ('distribution_helpers.py', releasefile_name)
    
    # --- Python 3 conversion --------------------------------------------------
    
    def this_dir(self):
        return os.path.dirname(os.path.abspath(__file__))
    
    def convert_file_to_python3(self, filename):
        # Python 2.3 does not have subprocess, so just importing it here…
        import subprocess
        
        absolute_pathname = os.path.join(self.this_dir(), filename)
        exit_code = subprocess.call(['2to3', '--write', absolute_pathname], 
                                    cwd=self.this_dir(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert exit_code == 0, 'Conversion of %s failed: error code %s' % (absolute_pathname, exit_code)
    
    def revert_file_to_python2_version(self, filename):
        absolute_pathname = os.path.join(self.this_dir(), filename)
        os.rename(absolute_pathname + '.bak', absolute_pathname)
    
    def convert_files_to_python3(self):
        for filename in self.preconversion_files:
            self.convert_file_to_python3(filename)
    
    def revert_files_to_python2(self):
        for filename in self.preconversion_files:
            self.revert_file_to_python2_version(filename)
    
    # --------------------------------------------------------------------------
    
    def uses_python3(self):
        major = sys.version_info[0]
        return major == 3
    
    def setup_parameters(self):
        if self.uses_python3():
            self.convert_files_to_python3()
        
        # With Python 3 we can only import this after applying the Python 3 fixes.
        # The file is not in the libary because the __init__.py files for the 
        # module pull in other modules which need to be converted just to import
        # the module containing release metadata
        from distribution_helpers import i18n_aware_commands, information_from_file
        extra_commands = i18n_aware_commands()
        externally_defined_parameters = information_from_file(self.releasefile_name)
        
        if self.uses_python3():
            self.revert_files_to_python2()
            externally_defined_parameters['use_2to3'] =  True
        return extra_commands, externally_defined_parameters



if __name__ == '__main__':
    extra_commands, externally_defined_parameters = MetaDataExtractor().setup_parameters()
    
    setuptools.setup(
        extras_require = {
            'Babel': ['Babel>=0.9.5'],
        },
        
        tests_require = ['Babel'],
        test_suite = 'nose.collector',
        
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
        cmdclass=extra_commands,
        **externally_defined_parameters
    )


