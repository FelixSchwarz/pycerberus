# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus import InvalidDataError
from pycerberus.errors import InvalidArgumentsError
from pycerberus.lib.form_data import FieldData
from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator


class IntegerValidatorTest(ValidationTest):
    
    validator_class = IntegerValidator
    
    def test_can_convert_string_to_int(self):
        assert_equals(42, self.process('42'))
        assert_equals(42, self.process(u'42'))
        assert_equals(-5, self.process('-5'))

    def test_validator_accepts_integer(self):
        assert_equals(4, self.process(4))

    def test_fail_for_non_digit_strings(self):
        with assert_raises(InvalidDataError):
            self.process('invalid_number')

    def test_validator_rejects_bad_types(self):
        with assert_raises(InvalidDataError):
            self.process([])
        with assert_raises(InvalidDataError):
            self.process({})
        with assert_raises(InvalidDataError):
            self.process(object)
        with assert_raises(InvalidDataError):
            self.process(int)

    def test_validator_rejects_none_if_value_is_required(self):
        # Actually this functionality seems to be pretty basic and is 
        # implemented in the Validator class - however it was broken because of
        # a bug in simple_super ("self.super()" vs. "self.super(*args, **kwargs)")
        with assert_raises(InvalidDataError):
            self.process(None)

    def test_can_specify_minimum_value(self):
        self.init_validator(min=20)
        self.process(20)
        self.process(40)
        e = assert_raises(InvalidDataError, lambda: self.process(4))
        assert_equals('Number must be 20 or greater.', e.msg())

    def test_can_specify_maximum_value(self):
        self.init_validator(max=12)
        self.process(12)
        self.process(-5)
        e = assert_raises(InvalidDataError, lambda: self.process(13))
        assert_equals('Number must be 12 or smaller.', e.msg())

    def test_can_use_min_and_max_together(self):
        self.init_validator(min=3, max=12)
        self.process(5)
        with assert_raises(InvalidDataError):
            self.process(2)
        with assert_raises(InvalidDataError):
            self.process(13)

    def test_minium_value_must_be_smaller_or_equal_to_maximum(self):
        e = assert_raises(InvalidArgumentsError, lambda: self.init_validator(min=13, max=12))
        assert_equals('min must be smaller or equal to max (13 > 12)', e.msg())

    def test_treats_empty_string_as_empty_value(self):
        self.init_validator(required=False)
        assert_none(self.process(''))

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
        result = self.process('6')
        assert_false(result.contains_errors())
        assert_equals('6', result.initial_value)
        assert_equals(6, result.value)

    def test_can_return_result_for_invalid_input(self):
        self.init_validator(IntegerValidator(exception_if_invalid=False))
        result = self.process('invalid', ensure_valid=False)
        assert_true(result.contains_errors())
        assert_equals('invalid', result.initial_value)
        assert_none(result.value)

    def test_can_return_result_from_validate(self):
        self.init_validator(IntegerValidator(min=10, max=20, exception_if_invalid=False))
        result = self.process('5', ensure_valid=False)
        assert_true(result.contains_errors())

        result = self.process('40', ensure_valid=False)
        assert_true(result.contains_errors())

    def test_can_skip_validate_if_convert_found_errors(self):
        self.init_validator(IntegerValidator(min=10, exception_if_invalid=False))
        result = self.process('invalid', ensure_valid=False)
        assert_true(result.contains_errors())
        assert_equals('invalid', result.initial_value)
        assert_none(result.value)
        assert_length(1, result.errors)

    def test_can_return_error_result_from_convert(self):
        self.init_validator(exception_if_invalid=False)
        with assert_not_raises():
            result = self.process('invalid', ensure_valid=False)
        assert_equals('invalid', result.initial_value)
        assert_equals(None, result.value)

        assert_true(result.contains_errors())
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

        assert_true(result.contains_errors())
        assert_length(1, result.errors)
        error = result.errors[0]
        assert_equals('too_big', error.key)
        assert_equals('Number must be 10 or smaller.', error.message)

