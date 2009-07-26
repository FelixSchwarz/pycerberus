# -*- coding: UTF-8 -*-

from unittest import TestCase

from inputvalidation import EmptyError, InvalidArgumentsError, Validator
from inputvalidation.api import NoValueSet


class DummyValidator(Validator):
    _empty_value = 'empty'
    
    def __init__(self, default=42, *args, **kwargs):
        super(DummyValidator, self).__init__(default=default, *args, **kwargs)

    def is_empty(self, value, state):
        return value == self._empty_value


class ValidatorTest(TestCase):
    class AttributeHolder(object): pass
    
    def setUp(self):
        self._validator = self.validator()
    
    def validator(self, *args, **kwargs):
        return DummyValidator(*args, **kwargs)
    
    def not_implemented(self, *args, **kwargs):
        raise NotImplementedError()
    
    def test_have_special_value_for_no_value_set(self):
        self.assertEqual(NoValueSet, NoValueSet)
        self.assertNotEqual(True, NoValueSet)
   
    def test_can_detect_empty_values_and_return_special_value_before_validation(self):
        self._validator.convert = self.not_implemented
        self.assertEqual(42, self.validator(required=False).process('empty'))
        self.assertNotEqual(self.not_implemented, self.validator().convert)
    
    def test_validator_provides_empty_dict_if_no_state_was_given(self):
        dummy = self.AttributeHolder()
        dummy.given_state = None
        
        def store_empty(state):
            dummy.given_state = state
            return 21
        validator = self.validator(required=False)
        validator.empty_value = store_empty
        self.assertEqual(21, validator.process('empty'))
        self.assertEqual({}, dummy.given_state)
        self.assertNotEqual(store_empty, self.validator().empty_value)
    
    def test_can_set_default_value_for_empty_values(self):
        self.assertEqual(23, Validator(default=23, required=False).process(None))
    
    def test_raise_exception_if_required_value_is_missing(self):
        self.assertEqual(42,  Validator(required=True).process(42))
        self.assertEqual(None,  Validator(required=False).process(None))
        self.assertRaises(EmptyError, Validator(required=True).process, None)
        self.assertRaises(EmptyError, Validator().process, None)
    
    def test_raise_exception_if_value_is_required_but_default_is_set_to_prevent_errors(self):
        self.assertRaises(InvalidArgumentsError, Validator, required=True, default=12)
        

