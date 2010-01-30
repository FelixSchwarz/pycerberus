# -*- coding: UTF-8 -*-

from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator


class VariablePartsInErrorMessages(ValidationTest):
    
    validator_class = IntegerValidator
    
    def test_error_messages_can_contain_variable_parts(self):
        self.assert_true('got "list"' in self.get_error([]).msg)
    
    def test_variable_parts_are_added_after_translation(self):
        expected_part = '(String erwartet, "list" erhalten)'
        translated_message = self.get_error([], locale='de').msg
        self.assert_true(expected_part in translated_message, translated_message)



