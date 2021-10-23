# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.errors import InvalidArgumentsError
from pycerberus.lib.form_data import FieldData
from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator


class IntegerValidatorTest(ValidationTest):
    
    validator_class = IntegerValidator
    
    def test_can_convert_string_to_int(self):
        self.assert_is_valid('42', expected=42)
        self.assert_is_valid(u'42', expected=42)
        self.assert_is_valid('-5', expected=-5)

    def test_validator_accepts_integer(self):
        self.assert_is_valid('4', expected=4)

    def test_fail_for_non_digit_strings(self):
        self.assert_error_with_key('invalid_number', 'invalid')

    def test_validator_rejects_bad_types(self):
        for _input in ([], {}, object, int):
            self.assert_error_with_key('invalid_type', _input)

    def test_validator_rejects_none_if_value_is_required(self):
        # Actually this functionality seems to be pretty basic and is 
        # implemented in the Validator class - however it was broken because of
        # a bug in simple_super ("self.super()" vs. "self.super(*args, **kwargs)")
        self.assert_error_with_key('empty', None)

    def test_can_specify_minimum_value(self):
        self.init_validator(min=20)
        self.assert_is_valid(20)
        self.assert_is_valid(40)
        error = self.assert_error_with_key('too_low', 4, _return_error=True)
        assert_equals('Number must be 20 or greater.', error.msg())

    def test_can_specify_maximum_value(self):
        self.init_validator(max=12)
        self.assert_is_valid(12)
        self.assert_is_valid(-5)
        error = self.assert_error_with_key('too_big', 13, _return_error=True)
        assert_equals('Number must be 12 or smaller.', error.msg())

    def test_can_use_min_and_max_together(self):
        self.init_validator(min=3, max=12)
        self.assert_is_valid(5)
        self.assert_error_with_key('too_low', 2)
        self.assert_error_with_key('too_big', 13)

    def test_minium_value_must_be_smaller_or_equal_to_maximum(self):
        e = assert_raises(InvalidArgumentsError, lambda: self.init_validator(min=13, max=12))
        assert_equals('min must be smaller or equal to max (13 > 12)', e.msg())

    def test_treats_empty_string_as_empty_value(self):
        self.init_validator(required=False)
        self.assert_is_valid('', expected=None)

    # --- revert_conversion() -------------------------------------------------
    def test_revert_conversion(self):
        assert_equals(1, self.revert_conversion(1))
        assert_equals(1, self.revert_conversion('1'))
        assert_equals('1.9', self.revert_conversion('1.9'))
        assert_equals(u'ö', self.revert_conversion(u'ö'))
        assert_equals(None, self.revert_conversion(None))
        assert_equals([], self.revert_conversion([]))

    def test_no_reversion_to_int_for_boolean_values(self):
        true_result = self.revert_conversion(True)
        assert true_result is True
        false_result = self.revert_conversion(False)
        assert false_result is False

    def test_can_use_field_data_to_revert_conversion(self):
        data = FieldData('foo', initial_value='bar')
        assert_equals('bar', self.revert_conversion(data))

    # --- results instead of exceptions ---------------------------------------
    def test_can_return_result_for_valid_input(self):
        self.init_validator(IntegerValidator(exception_if_invalid=False))
        result = self.assert_is_valid('6', expected=6)
        assert_equals('6', result.initial_value)

    def test_can_return_result_for_invalid_input(self):
        self.init_validator(IntegerValidator(exception_if_invalid=False))
        result = self.assert_error_with_key('invalid_number', 'invalid')
        assert_equals('invalid', result.initial_value)
        assert_none(result.value)

    def test_can_return_result_from_validate(self):
        self.init_validator(IntegerValidator(min=10, max=20, exception_if_invalid=False))
        result = self.assert_error('5')
        assert_true(result.contains_error())

        result = self.assert_error('40')
        assert_true(result.contains_error())

    def test_can_skip_validate_if_convert_found_errors(self):
        self.init_validator(IntegerValidator(min=10, exception_if_invalid=False))
        result = self.assert_error_with_key('invalid_number', 'invalid')
        assert_equals('invalid', result.initial_value)
        assert_none(result.value)
        assert_length(1, result.errors)

    def test_can_return_error_result_from_convert(self):
        self.init_validator(exception_if_invalid=False)
        with assert_not_raises():
            result = self.process('invalid', ensure_valid=False)
        assert_equals('invalid', result.initial_value)
        assert_equals(None, result.value)

        assert_true(result.contains_error())
        assert_length(1, result.errors)
        error = result.errors[0]
        assert_equals('invalid_number', error.key)
        assert_equals('Please enter a number.', error.message)

    def test_can_return_error_result_from_validate(self):
        self.init_validator(max=10, exception_if_invalid=False)
        with assert_not_raises():
            result = self.process(20, ensure_valid=False)
        assert_equals(20, result.initial_value)
        assert_equals(None, result.value)

        assert_true(result.contains_error())
        assert_length(1, result.errors)
        error = result.errors[0]
        assert_equals('too_big', error.key)
        assert_equals('Number must be 10 or smaller.', error.message)

