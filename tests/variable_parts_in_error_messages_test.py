# -*- coding: UTF-8 -*-

from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator


class VariablePartsInErrorMessages(ValidationTest):
    
    validator_class = IntegerValidator
    
    def test_error_messages_can_contain_variable_parts(self):
        self.assert_contains('got "list"', self.get_error([]).details().msg())
    
    def test_variable_parts_are_added_after_translation(self):
        expected_part = '(String erwartet, "list" erhalten)'
        translated_message = self.get_error([], locale='de').details().msg()
        self.assert_contains(expected_part, translated_message)



