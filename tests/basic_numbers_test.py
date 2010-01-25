# -*- coding: UTF-8 -*-

from pycerberus import InvalidDataError
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


