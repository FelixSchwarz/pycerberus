# -*- coding: UTF-8 -*-

from unittest import TestCase

from inputvalidation import InvalidDataError
from inputvalidation.api import NoValueSet
from inputvalidation.validators import IntegerValidator


class IntegerValidatorTest(TestCase):
    def setUp(self):
        self.validator = IntegerValidator()
    
    def validate(self, *args, **kwargs):
        return self.validator.process(*args, **kwargs)
    
    def test_can_convert_string_to_int(self):
        self.assertEqual(42, self.validate('42'))
        self.assertEqual(42, self.validate(u'42'))
        self.assertEqual(-5, self.validate('-5'))
    
    def test_validator_accepts_integer(self):
        self.assertEqual(4, self.validate(4))
    
    def test_fail_for_non_digit_strings(self):
        self.assertRaises(InvalidDataError, self.validate, 'invalid_number')
    
    def test_validator_rejects_bad_types(self):
        self.assertRaises(InvalidDataError, self.validate, [])
        self.assertRaises(InvalidDataError, self.validate, {})
        self.assertRaises(InvalidDataError, self.validate, object)
        self.assertRaises(InvalidDataError, self.validate, int)


