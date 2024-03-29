# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import warnings

from pythonic_testcase import *

from pycerberus.api import Validator
from pycerberus.errors import Error, InvalidArgumentsError, InvalidDataError
from pycerberus.lib.form_data import FieldData
from pycerberus.test_util import ValidationTest
from pycerberus.validators import StringValidator


class ValidatorWithErrorResults(Validator):
    def __init__(self, exception_if_invalid=False, **kwargs):
        super(ValidatorWithErrorResults, self).__init__(exception_if_invalid=exception_if_invalid, **kwargs)

    def messages(self):
        return {
            'div2': 'divisible by 2',
            'div5': 'divisible by 5',
            'small': 'below 0',
        }

    def convert(self, value, context):
        if (value % 2) == 0:
            self.new_error('div2', value, context)
        if (value % 5) == 0:
            self.new_error('div5', value, context)
        return value

    def validate(self, value, context):
        if value < 0:
            self.new_error('small', value, context)


class RaisingValidator(Validator):
    exception_if_invalid = True

    def messages(self):
        return {'foo': 'foobar'}

    def validate(self, value, context):
        self.new_error('foo', value, context)


class ValidatorWithErrorResultsTest(ValidationTest):

    validator_class = ValidatorWithErrorResults

    # --- initialization -------------------------------------------------------
    def test_vanilla_validators_default_to_use_exceptions(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            validator = Validator()
        assert_true(validator._exception_if_invalid)

        validator = Validator(exception_if_invalid=False)
        assert_false(validator._exception_if_invalid)

    def test_custom_validators_can_switch_the_default(self):
        validator = ValidatorWithErrorResults(exception_if_invalid=True)
        # validate test setup - validator should raise exceptions
        with assert_raises(InvalidDataError):
            validator.process(2)

        validator = ValidatorWithErrorResults(exception_if_invalid=False)
        with assert_not_raises(InvalidDataError):
            result = validator.process(2)
        assert_true(result.contains_error())

    def test_can_reject_attempt_to_override_setting_for_custom_validators(self):
        # use RaisingValidator as that one should be hard-coded to use
        # exceptions
        validator = RaisingValidator()
        # validate test setup - validator should raise exceptions
        with assert_raises(InvalidDataError):
            validator.process(2)

        with assert_raises(InvalidArgumentsError):
            RaisingValidator(exception_if_invalid=False)

    # --- validation returns results ------------------------------------------
    def test_can_return_result_for_valid_input(self):
        context = {}
        result = self.assert_is_valid(1, context=context)

        assert_not_equals(1, result, message='should return FieldData instance')
        assert_equals(1, result.value)
        assert_equals(1, result.initial_value)
        assert_equals({}, context, message='context should not be modified')

    def test_can_return_converted_values_even_though_result_contained_errors(self):
        # This test is not really useful on its own because it seems somewhat
        # pathological to pass in a result in a simple FieldValidator.
        # However this was the simplest test I was able to come up to ensure
        # that Validator ignores pre-existing errors.
        # That behavior will be required to run FormValidators properly which
        # can be executed even though some (unrelated) fields are invalid. This
        # functionality is currently only available out-of-tree.
        result = self.validator().new_result(21)
        result.errors = (Error(u'foo', u'some text', 21, {}, is_critical=False), )
        assert_true(result.contains_error())

        context = {u'result': result}
        result = self.assert_error(1, context=context)
        assert_equals(1, result.value)

    def test_can_return_result_for_empty_input(self):
        validator = StringValidator(required=False, exception_if_invalid=False)
        self.init_validator(validator)
        context = {'result': validator.new_result(None)}
        result = self.assert_is_valid('', expected=None, context=context)
        assert_equals('', result.initial_value)

    def test_can_return_error_from_convert(self):
        context = {}
        result = self.assert_error(2, context=context)

        assert_equals(2, result.initial_value)
        assert_none(result.value)

        assert_length(1, result.errors)
        error = result.errors[0]
        assert_equals('div2', error.key)
        assert_equals(2, error.value)
        assert_equals('divisible by 2', error.msg)
        assert_equals({}, context, message='context should not be modified')

    def test_can_return_error_from_validate(self):
        result = self.assert_error(-1)

        assert_equals(-1, result.initial_value)
        assert_none(result.value)
        assert_length(1, result.errors)
        error = result.errors[0]
        assert_equals('small', error.key)

    def test_can_use_error_from_validate_as_exception(self):
        self.init_validator(RaisingValidator())
        e = self.assert_error('foo', _return_error=True)
        # the validator did return an InvalidDataError otherwise the result
        # instance has no ".details()" method
        assert_equals('foo', e.details().key())

    def test_can_return_multiple_errors_in_process(self):
        result = self.assert_error(10)
        assert_equals(10, result.initial_value)
        assert_none(result.value)

        assert_true(result.contains_error())
        assert_length(2, result.errors)
        error1, error2 = result.errors
        assert_equals('div2', error1.key)
        assert_equals('div5', error2.key)

    def test_can_skip_validate_if_convert_detected_errors(self):
        result = self.assert_error(-2)
        assert_equals(-2, result.initial_value)
        assert_none(result.value)

        assert_true(result.contains_error())
        assert_length(1, result.errors)
        error = result.errors[0]
        assert_equals('div2', error.key, message='validate would add "small" key')

    def test_can_return_error_for_empty_values_in_required_validator(self):
        result = self.assert_error(None)
        assert_equals(None, result.initial_value)
        assert_none(result.value)

        assert_length(1, result.errors)
        error = result.errors[0]
        assert_equals('empty', error.key)

    def test_can_return_context_without_permanent_modifications(self):
        source_context = {'foo': [1, 2, 3]}
        context = source_context.copy()
        result = self.assert_error(-2, context=context)
        assert_equals(-2, result.initial_value)
        assert_equals(source_context, context)

    # --- revert_conversion() -------------------------------------------------

    def test_can_use_field_data_to_revert_conversion(self):
        validator = Validator(exception_if_invalid=False)
        data = FieldData('foo', initial_value='bar')
        assert_equals('bar', validator.revert_conversion(data))
