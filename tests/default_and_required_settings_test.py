# -*- coding: UTF-8 -*-

from pycerberus import EmptyError, InvalidArgumentsError, Validator
from pycerberus.api import NoValueSet
from pycerberus.test_util import ValidationTest


class DummyValidator(Validator):
    _empty_value = 'empty'
    
    def __init__(self, default=42, *args, **kwargs):
        self._is_internal_state_frozen = False
        self.super()
    
    def is_empty(self, value, context):
        return value == self._empty_value


class ValidatorTest(ValidationTest):
    
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
    
    def test_validator_provides_empty_dict_if_no_context_was_given(self):
        dummy = self.AttributeHolder()
        dummy.given_context = None
        
        def store_empty(context):
            dummy.given_context = context
            return 21
        self.init_validator(required=False)
        self.validator().empty_value = store_empty
        self.assert_equals(21, self.process('empty'))
        self.assert_equals({}, dummy.given_context)
        # check that we did not change the real class used in other test cases
        self.assert_not_equals(store_empty, self.init_validator().empty_value)
    
    def test_can_set_default_value_for_empty_values(self):
        self.assert_equals(23, Validator(default=23, required=False).process(None))
    
    def test_raise_exception_if_required_value_is_missing(self):
        self.assert_equals(42,  Validator(required=True).process(42))
        self.assert_none(Validator(required=False).process(None))
        self.assert_raises(EmptyError, Validator(required=True).process, None)
        self.assert_raises(EmptyError, Validator().process, None)
    
    def test_raise_exception_if_value_is_required_but_default_is_set_to_prevent_errors(self):
        self.assert_raises(InvalidArgumentsError, Validator, required=True, default=12)


