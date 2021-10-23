# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus import InvalidArgumentsError
from pycerberus.test_util import ValidationTest
from pycerberus.validators import StringValidator



class StringValidatorTest(ValidationTest):
    
    validator_class = StringValidator
    
    def test_accept_string_and_unicode(self):
        self.assert_is_valid('foo', expected='foo')
        self.assert_is_valid(u'bär', expected=u'bär')

    def test_reject_bad_types(self):
        self.assert_error([])
        self.assert_error({})
        self.assert_error(object)
        self.assert_error(5)

    def test_can_reject_bad_types_with_error_result(self):
        self.init_validator(StringValidator(exception_if_invalid=False))
        error = self.assert_error_with_key('invalid_type', [], _return_error=True)
        assert_true(error.is_critical)


    def test_show_class_name_in_error_message(self):
        e = self.assert_error([], _return_error=True)
        assert_contains(u'(expected string, got "list")', e.msg())

    def test_empty_string_is_also_empty(self):
        self.assert_error(None)
        self.assert_error('')
        
        self.init_validator(default='foo', required=False)
        self.assert_is_valid(None, expected='foo')
        self.assert_is_valid('', expected='foo')

    def test_can_specify_min_length(self):
        self.init_validator(StringValidator(min_length=3))
        self.assert_is_valid('foo')
        self.assert_error('fo')
    
    def test_can_specify_max_length(self):
        self.init_validator(StringValidator(max_length=3))
        self.assert_is_valid('foo')
        self.assert_error('foobar')
    
    def test_can_specify_min_and_max_length_together(self):
        self.init_validator(StringValidator(min_length=2, max_length=3))
        self.assert_error('f')
        self.assert_is_valid('fo')
        self.assert_is_valid('foo')
        self.assert_error('foobar')

    def test_can_return_error_results_from_validate(self):
        validator = StringValidator(min_length=2, max_length=3, exception_if_invalid=False)
        self.init_validator(validator)

        error = self.assert_error_with_key('too_short', 'f', _return_error=True)
        assert_false(error.is_critical)

    def test_min_length_must_be_smaller_or_equal_max_length(self):
        with assert_raises(InvalidArgumentsError):
            StringValidator(min_length=2, max_length=1)


class ValidatorsDerivedFromStringTest(ValidationTest):
    class TrueValidator(StringValidator):
        def convert(self, value, context):
            return True
    
    validator_class = TrueValidator
    
    def test_only_test_for_length_if_explicitely_set(self):
        self.assert_is_valid('5')

        self.init_validator(self.validator_class(min_length=0))
        with assert_raises(TypeError):
            self.process('5')

