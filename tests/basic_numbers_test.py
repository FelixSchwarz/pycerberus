# -*- coding: UTF-8 -*-

from pycerberus import InvalidDataError
from pycerberus.errors import InvalidArgumentsError
from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator


class IntegerValidatorTest(ValidationTest):
    
    validator_class = IntegerValidator
    
    def test_can_convert_string_to_int(self):
        self.assert_equals(42, self.process('42'))
        self.assert_equals(42, self.process(u'42'))
        self.assert_equals(-5, self.process('-5'))
    
    def test_validator_accepts_integer(self):
        self.assert_equals(4, self.process(4))
    
    def test_fail_for_non_digit_strings(self):
        self.assert_raises(InvalidDataError, self.process, 'invalid_number')
    
    def test_validator_rejects_bad_types(self):
        self.assert_raises(InvalidDataError, self.process, [])
        self.assert_raises(InvalidDataError, self.process, {})
        self.assert_raises(InvalidDataError, self.process, object)
        self.assert_raises(InvalidDataError, self.process, int)
    
    def test_validator_rejects_none_if_value_is_required(self):
        # Actually this functionality seems to be pretty basic and is 
        # implemented in the Validator class - however it was broken because of
        # a bug in simple_super ("self.super()" vs. "self.super(*args, **kwargs)")
        self.assert_raises(InvalidDataError, self.process, None)
    
    def test_can_specify_minimum_value(self):
        self.init_validator(min=20)
        self.process(20)
        self.process(40)
        e = self.assert_raises(InvalidDataError, lambda: self.process(4))
        self.assert_equals('Number must be 20 or greater.', e.msg())
    
    def test_can_specify_maximum_value(self):
        self.init_validator(max=12)
        self.process(12)
        self.process(-5)
        e = self.assert_raises(InvalidDataError, lambda: self.process(13))
        self.assert_equals('Number must be 12 or smaller.', e.msg())
    
    def test_can_use_min_and_max_together(self):
        self.init_validator(min=3, max=12)
        self.process(5)
        self.assert_raises(InvalidDataError, lambda: self.process(2))
        self.assert_raises(InvalidDataError, lambda: self.process(13))
    
    def test_minium_value_must_be_smaller_or_equal_to_maximum(self):
        e = self.assert_raises(InvalidArgumentsError, lambda: self.init_validator(min=13, max=12))
        self.assert_equals('min must be smaller or equal to max (13 > 12)', e.msg())


