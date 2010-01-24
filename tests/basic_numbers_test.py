# -*- coding: UTF-8 -*-

from inputvalidation import InvalidDataError
from inputvalidation.lib import PythonicTestCase
from inputvalidation.validators import IntegerValidator


class IntegerValidatorTest(PythonicTestCase):
    def setUp(self):
        self.super()
        self.validator = IntegerValidator()
    
    def validate(self, *args, **kwargs):
        return self.validator.process(*args, **kwargs)
    
    def test_can_convert_string_to_int(self):
        self.assert_equals(42, self.validate('42'))
        self.assert_equals(42, self.validate(u'42'))
        self.assert_equals(-5, self.validate('-5'))
    
    def test_validator_accepts_integer(self):
        self.assert_equals(4, self.validate(4))
    
    def test_fail_for_non_digit_strings(self):
        self.assert_raises(InvalidDataError, self.validate, 'invalid_number')
    
    def test_validator_rejects_bad_types(self):
        self.assert_raises(InvalidDataError, self.validate, [])
        self.assert_raises(InvalidDataError, self.validate, {})
        self.assert_raises(InvalidDataError, self.validate, object)
        self.assert_raises(InvalidDataError, self.validate, int)


