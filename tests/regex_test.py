# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.test_util import assert_no_critical_errors, error_keys, ValidationTest
from pycerberus.validators import RegexValidator



class RegexTest(ValidationTest):
    validator_class = RegexValidator

    def setUp(self):
        self.init_validator(regex=r'\d+')
        super(RegexTest, self).setUp()

    def test_accepts_input_matching_the_pattern(self):
        self.assert_is_valid('42', expected='42')

    def test_rejects_input_not_matching_the_pattern(self):
        self.assert_error_with_key('bad_pattern', 'invalid')

    def test_can_return_error_results_from_convert(self):
        self.init_validator(
            regex=r'\d+',
            exception_if_invalid=False,
            use_match_for_conversion=True
        )
        error = self.assert_error_with_key('bad_pattern', 'invalid', _return_error=True)
        # error in convert should be treated as critical as the input for
        # .validate() is different
        assert_true(error.is_critical)

    def test_can_handle_critical_errors_from_string_conversion(self):
        # RegexValidator must check if its superclass (StringValidator) detected
        # an error during ".convert()" - otherwise we will trigger exceptions
        # as the re module can only work on strings.
        self.init_validator(
            regex=r'\d+',
            exception_if_invalid=False,
            use_match_for_conversion=True
        )
        error = self.assert_error_with_key('invalid_type', [], _return_error=True)
        # error in convert should be treated as critical as the input for
        # .validate() is different
        assert_true(error.is_critical)

    def test_can_return_error_results_from_validate(self):
        self.init_validator(
            regex=r'\d+',
            exception_if_invalid=False,
            use_match_for_conversion=False
        )
        error = self.assert_error_with_key('bad_pattern', 'invalid', _return_error=True)
        assert_false(error.is_critical)

    def test_can_add_custom_errors_in_validate_even_if_superclass_already_found_errors(self):
        self.init_validator(
            regex=r'\d+',
            # this is used to trigger a non-critical error in string ".validate()"
            min_length=5,
            # ensure RegexValidator runs its checks in ".validate()" as well
            use_match_for_conversion=False,
            # otherwise we can have only a single error
            exception_if_invalid=False,
        )
        result = self.assert_error('abcd')
        assert_equals(('too_short', 'bad_pattern'), error_keys(result.errors))
        assert_no_critical_errors(result.errors)

    def test_can_return_translated_messages(self):
        self.init_validator(
            regex=r'\d+',
            exception_if_invalid=False,
            use_match_for_conversion=False
        )

        # message from super class (Validator)
        context = {'locale': 'de'}
        error = self.assert_error('invalid', _return_error=True, context=context)
        assert_equals(
            'Die Eingabe "invalid" entspricht nicht dem erwarteten Muster.',
            error.message
        )

