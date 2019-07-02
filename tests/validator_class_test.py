# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus import EmptyError, InvalidArgumentsError, Validator
from pycerberus.api import NoValueSet
from pycerberus.lib.form_data import is_result
from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator


class ValidatorTest(ValidationTest):
    def test_bail_out_if_unknown_parameters_are_passed_to_constructor(self):
        with assert_raises(Exception):
            Validator(invalid='fnord')

    def test_revert_conversion(self):
        self.init_validator(Validator())
        assert_equals(u'ö', self.revert_conversion(u'ö'))
        assert_equals('1', self.revert_conversion(1))
        assert_equals(None, self.revert_conversion(None))
    
    def test_can_copy_itself(self):
        # This is the same test as in BaseValidator - however Validator has
        # thread-safety built-in so we need extra code
        class MutableValidator(Validator):
            acceptable_values = [1, 2, 3]
        validator = MutableValidator()
        
        a = validator.copy()
        b = validator.copy()
        a.acceptable_values.append(4)
        
        assert_contains(4, a.acceptable_values)
        assert_not_contains(4, b.acceptable_values)

    def test_can_override_result_handling(self):
        """While this is not an official API this is used by some projects and
        pycerberus should not break them accidentally without providing similar
        functionality via some API."""
        class CustomHandlingValidator(IntegerValidator):
            def handle_validator_result(self, converted_value, result, context, **kwargs):
                result.set(value=42)
                return result

        validator = CustomHandlingValidator(exception_if_invalid=False)
        result = validator.process('invalid')
        assert_equals(42, result.value)

    def test_process_does_not_modify_context_permanently_if_value_is_empty(self):
        context = {}
        validator = Validator(exception_if_invalid=False)
        validator.process(None, context=context)
        assert_equals({}, context)

        validator = Validator(required=False, exception_if_invalid=False)
        validator.process(None, context=context)
        assert_equals({}, context)

        validator = Validator(exception_if_invalid=True)
        with assert_raises(EmptyError):
            validator.process(None, context=context)
        assert_equals({}, context)

        validator = Validator(required=False, exception_if_invalid=True)
        validator.process(None, context=context)
        assert_equals({}, context)


class DefaultAndRequiredValuesTest(ValidationTest):
    
    class DummyValidator(Validator):
        _empty_value = 'empty'
        
        def __init__(self, default=42, *args, **kwargs):
            self._is_internal_state_frozen = False
            self.super()
        
        def is_empty(self, value, context):
            return value == self._empty_value
    
    validator_class = DummyValidator
    
    class AttributeHolder(object): pass
    
    def not_implemented(self, *args, **kwargs):
        raise NotImplementedError()
    
    def test_have_special_value_for_no_value_set(self):
        self.assert_equals(NoValueSet, NoValueSet)
        self.assert_trueish(NoValueSet)
    
    def test_can_detect_empty_values_and_return_special_value_before_validation(self):
        self.validator().convert = self.not_implemented
        self.init_validator(required=False)
        self.assert_equals(42, self.process('empty'))
        # special check to ensure that other tests are not affected by this
        self.assert_not_equals(self.not_implemented, self.validator().convert)

    def test_validator_provides_almost_empty_dict_if_no_context_was_given(self):
        # we need a "result" in our context so validators can properly report
        # results
        dummy = self.AttributeHolder()
        dummy.given_context = None
        
        def store_empty(context):
            dummy.given_context = context
            return 21
        self.init_validator(required=False)
        self.validator().empty_value = store_empty
        self.assert_equals(21, self.process('empty'))

        assert_not_none(dummy.given_context)
        result = dummy.given_context.pop('result', None)
        assert_true(is_result(result),
            message='context must contain a result instance to return errors without using exceptions')
        self.assert_equals({}, dummy.given_context)
        # check that we did not change the real class used in other test cases
        self.assert_not_equals(store_empty, self.init_validator().empty_value)
    
    def test_can_set_default_value_for_empty_values(self):
        self.assert_equals(23, Validator(default=23, required=False).process(None))
    
    def test_raise_exception_if_required_value_is_missing(self):
        self.assert_equals(42,  Validator(required=True).process(42))
        self.assert_none(Validator(required=False).process(None))
        assert_raises(EmptyError, lambda: Validator(required=True).process(None))
        assert_raises(EmptyError, lambda: Validator().process(None))
    
    def test_raise_exception_if_value_is_required_but_default_is_set_to_prevent_errors(self):
        assert_raises(InvalidArgumentsError, lambda: Validator(required=True, default=12))


class StripValueTest(ValidationTest):
    
    validator_class = Validator
    
    def test_can_strip_input(self):
        self.init_validator(strip=True)
        self.assert_equals('foo', self.validator().process(' foo '))
        
        self.init_validator(strip=False)
        self.assert_equals(' foo ', self.validator().process(' foo '))
    
    def test_do_not_strip_input_by_default(self):
        self.assert_equals(' foo ', self.validator().process(' foo '))
    
    def test_only_strip_if_value_has_strip_method(self):
        self.init_validator(strip=True)
        self.assert_error(None)
    
    def test_input_is_stripped_before_tested_for_emptyness(self):
        self.init_validator(strip=True)
        self.validator().set_internal_state_freeze(False)
        self.validator().is_empty = lambda value, context: value == ''
        
        self.assert_error(' ')


