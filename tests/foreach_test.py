# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.errors import InvalidArgumentsError, InvalidDataError
from pycerberus.schema import SchemaValidator
from pycerberus.test_util import error_keys, ValidationTest
from pycerberus.validators import ForEach, IntegerValidator



class ForEachTest(ValidationTest):
    
    validator_class = ForEach
    validator_args = (IntegerValidator, )

    def _invalid_message(self):
        return IntegerValidator().message('invalid_number', {})
    
    def test_passes_for_empty_lists(self):
        self.assert_is_valid([])

    def test_passes_if_every_single_item_passes(self):
        self.assert_is_valid((21, 42,))

    def test_applied_validator_can_convert_items(self):
        self.assert_is_valid(('21', '42'), expected=(21, 42))

    def test_applies_validator_to_first_item(self):
        errors = self.assert_error(['bar'], _return_error=True)

        assert_length(1, errors)
        assert_equals(self._invalid_message(), errors[0].msg)
    
    def test_applies_validator_to_every_item(self):
        result = self.assert_error(['bar', 'baz'])

        assert_length(2, result.errors)
        f1_errors, f2_errors = result.errors
        f1_error, = f1_errors
        assert_equals(self._invalid_message(), f1_error.msg)
        f2_error, = f2_errors
        assert_equals(self._invalid_message(), f2_error.msg)

    def test_returns_sparse_error_list(self):
        result = self.assert_error(['bar', '42'])

        errors_bar, errors_42 = result.errors
        assert_equals(self._invalid_message(), errors_bar[0].msg)
        assert_equals(None, errors_42)

    def test_works_with_validator_instances(self):
        # This is important if validators need some configuration in the 
        # constructor
        self.init_validator(ForEach(IntegerValidator()))
        self.assert_is_valid((42,))

    def test_rejects_missing_field(self):
        self.assert_error_with_key('empty', None)
    
    def test_rejects_non_iteratible_types(self):
        self.assert_error_with_key('invalid_type', object())
        self.assert_error_with_key('invalid_type', 42)
    
    def test_can_specify_min_amount_of_items(self):
        self.init_validator(ForEach(IntegerValidator, min_length=2))
        self.assert_is_valid((21, 42))

        self.assert_error_with_key('too_short', ())
        self.assert_error_with_key('too_short', (21,))
    
    def test_can_specify_max_amount_of_items(self):
        self.init_validator(ForEach(IntegerValidator, max_length=2))
        self.assert_is_valid((21, 42))

        self.assert_error_with_key('too_long', (21, 42, 63))

    def test_can_specify_min_length_and_max_lenght(self):
        self.init_validator(ForEach(IntegerValidator, min_length=1, max_length=1))
        self.assert_is_valid((21,))
        self.assert_error_with_key('too_short', ())
        self.assert_error_with_key('too_long', (21, 42,))

    def test_min_length_must_be_smaller_or_equal_max_length(self):
        with assert_raises(InvalidArgumentsError):
            ForEach(IntegerValidator, min_length=2, max_length=1)

    def test_returns_empty_tuple_if_not_required_and_no_value_given(self):
        validator = ForEach(IntegerValidator, required=False)
        assert_equals((), validator.empty_value({}))
    
    def test_can_set_validator_arguments_for_constructor(self):
        self.init_validator(ForEach(IntegerValidator, default=(), required=False))
        self.assert_is_valid(None, expected=())

    def test_can_return_results_from_subvalidators(self):
        validator = ForEach(
            IntegerValidator(exception_if_invalid=False),
        )
        result = validator.process(('invalid',))

        assert_true(result.contains_errors())
        assert_length(1, result.errors) # maybe 2 when we add global errors here?
        int_errors = result.errors[0]

        assert_length(1, int_errors)
        int_error = int_errors[0]
        assert_equals('invalid_number', int_error.key)

    def test_can_return_error_list_from_subvalidator(self):
        schema = SchemaValidator(exception_if_invalid=False)
        schema.add('number', IntegerValidator(exception_if_invalid=False))
        validator = ForEach(schema, exception_if_invalid=True)

        with assert_raises(InvalidDataError) as c:
            validator.process([{'number': '42'}, {'number': 'invalid'}, ])
        e = c.caught_exception
        list_errors = e.errors()
        assert_length(2, list_errors)
        assert_not_equals((None, None), list_errors)

        assert_none(list_errors[0])
        nr2_error = list_errors[1]
        assert_not_none(nr2_error)
        assert_isinstance(nr2_error, InvalidDataError,
            message='Schema raises on error so pycerberus only supports one error per field')
        assert_equals('invalid_number', nr2_error.details().key())

    def test_can_return_errors_from_subschemas(self):
        schema = SchemaValidator(exception_if_invalid=False)
        schema.add('foo', IntegerValidator(exception_if_invalid=False))
        foreach = ForEach(schema)

        result = foreach.process([{'foo': 'invalid'}, ])
        assert_true(result.contains_errors())

        assert_length(1, result.errors)
        item_errors = result.errors[0]
        assert_equals(set(('foo',)), set(item_errors))

    def test_can_return_exceptions_from_subschemas_as_errors(self):
        schema = SchemaValidator(exception_if_invalid=True)
        schema.add('foo', IntegerValidator(exception_if_invalid=True))
        foreach = ForEach(schema)

        with assert_not_raises(message='foreach should be able to return results'):
            result = foreach.process([{'foo': 'invalid'}, ])
        assert_true(result.contains_errors())
        assert_length(1, result.errors)

        schema_error = result.errors[0]
        assert_equals(set(('foo',)), set(schema_error))

    def test_can_return_result_for_empty_input_value(self):
        validator = ForEach(
            IntegerValidator(exception_if_invalid=False)
        )
        result = validator.process(None)

        assert_true(result.contains_errors())
        assert_length(1, result.errors)
        assert_length(1, result.global_errors) # seems to be duplicated?
        assert_equals(('empty', ), error_keys(result.errors))
