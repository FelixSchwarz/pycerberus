# -*- coding: UTF-8 -*-

from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator


class MessagesFromBuiltInValidatorsAreTranslatedTest(ValidationTest):
    
    validator_class = IntegerValidator
    
    def test_error_messages_are_translated(self):
        self.assert_equals('Please enter a number.', self.get_error('foo', locale='en').msg)
        self.assert_equals('Bitte geben Sie eine Zahl ein.', self.get_error('foo', locale='de').msg)
    
    def test_variable_parts_are_added_after_translation(self):
        expected_message = u'(String erwartet, "list" erhalten)'
        translated_message = self.get_error([], locale='de').msg
        self.assert_true(expected_message in translated_message, repr(translated_message))


