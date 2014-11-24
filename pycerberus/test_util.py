# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2009-2010, 2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pycerberus import InvalidDataError
from pycerberus.lib.simple_super import SuperProxy
from pycerberus.lib.pythonic_testcase import *


class ValidationTest(PythonicTestCase):
    
    super = SuperProxy()
    # don't initialize '_validator' attribute in 'setUp()' so that subclasses
    # can initialize the validator themself before calling this 'setUp()'.
    # This is important if the validator to be tested requires mandatory 
    # arguments for initialization.
    _validator = None
    
    def setUp(self):
        self.super()
        if hasattr(self, 'validator_class'):
            # this will set up the validator with the correct arguments 
            # specified in the testcase
            self.validator()
    
    def init_validator(self, validator=None, *args, **kwargs):
        if (validator is None) and hasattr(self, 'validator_class'):
            # FIXME: This won't work as args filled means that validator != None
            validator = self.validator_class(*args, **kwargs)
        self._validator = validator
        return self._validator
    
    def validator(self):
        """Return a validator instance (initializes a new one if none was 
        created yet)."""
        if self._validator is not None:
            return self._validator
        
        args = [None] + list(getattr(self, 'validator_args', ()))
        return self.init_validator(*args)
        
    schema = validator
    
    def process(self, *args, **kwargs):
        if len(args) == 1 and 'context' not in kwargs:
            kwargs['context'] = {}
        return self._validator.process(*args, **kwargs)
    
    def revert_conversion(self, *args, **kwargs):
        if len(args) == 1 and 'context' not in kwargs:
            kwargs['context'] = {}
        return self._validator.revert_conversion(*args, **kwargs)
    
    def assert_error(self, value, *args, **kwargs):
        call = lambda: self.process(value, *args, **kwargs)
        return assert_raises(InvalidDataError, call)
    
    def assert_error_with_locale(self, value, locale='en', *args, **kwargs):
        """Process the given value and assert that this raises a validation
        exception - return that exception."""
        context = {'locale': locale}
        return self.assert_error(value, context=context, *args, **kwargs)
    get_error = assert_error_with_locale
    
    def message_for_key(self, key, locale='de'):
        "Return the error message for the given key."
        exception = self.validator().exception(key, None, {'locale': locale})
        return exception.details().msg()

