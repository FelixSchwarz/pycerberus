# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import operator

from pythonic_testcase import *

from pycerberus import InvalidDataError
from pycerberus.lib.form_data import is_result


__all__ = [
    'assert_all_errors_critical',
    'assert_no_critical_errors',
    'error_keys',
    'ValidationTest'
]

def error_keys(errors):
    return tuple(map(operator.attrgetter('key'), errors))

def assert_all_errors_critical(errors):
    for error in errors:
        assert_true(error.is_critical, message='Non-critical error found %r' % (error,))

def assert_no_critical_errors(errors):
    for error in errors:
        assert_false(error.is_critical, message='Critical error found %r' % (error,))


class ValidationTest(PythonicTestCase):
    # don't initialize '_validator' attribute in 'setUp()' so that subclasses
    # can initialize the validator themself before calling this 'setUp()'.
    # This is important if the validator to be tested requires mandatory 
    # arguments for initialization.
    _validator = None
    
    def setUp(self):
        super(ValidationTest, self).setUp()
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
            initial_value = args[0]
            result = self._validator.new_result(initial_value)
            kwargs['context'] = {'result': result}
        ensure_valid = kwargs.pop('ensure_valid', True)
        result = self._validator.process(*args, **kwargs)
        if ensure_valid and is_result(result):
            assert_false(result.contains_errors())
        return result
    
    def revert_conversion(self, *args, **kwargs):
        if len(args) == 1 and 'context' not in kwargs:
            kwargs['context'] = {}
        return self._validator.revert_conversion(*args, **kwargs)

    def assert_is_valid(self, *args, **kwargs):
        kwargs['ensure_valid'] = True
        return self.process(*args, **kwargs)

    def assert_error(self, value, *args, **kwargs):
        message = kwargs.pop('message', None)
        kwargs['ensure_valid'] = False
        try:
            result = self.process(value, *args, **kwargs)
        except InvalidDataError as e:
            return e
        if (not is_result(result)) or (not result.contains_errors()):
            default_message = 'InvalidDataError not raised!'
            if message is None:
                raise AssertionError(default_message)
            raise AssertionError(default_message + ' ' + message)
        return result

    def assert_error_with_key(self, error_key, *args, **kwargs):
        message = kwargs.get('message', None)
        result_or_exc = self.assert_error(*args, **kwargs)

        if is_result(result_or_exc):
            errors = result_or_exc.errors
            _exc_keys = error_keys(errors)
        else:
            exc = result_or_exc
            _exc_keys = (exc.details().key(),)

        if error_key in _exc_keys:
            return
        fail_msg = 'No error with key %s (found %s)' % (error_key, ', '.join(_exc_keys))
        if message:
            fail_msg += ': ' + message
        self.fail(fail_msg)

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

