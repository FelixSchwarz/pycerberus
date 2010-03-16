# -*- coding: UTF-8 -*-

from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator


class MessagesFromBuiltInValidatorsAreTranslatedTest(ValidationTest):
    
    validator_class = IntegerValidator
    
    def test_error_messages_are_translated(self):
        self.assert_equals('Please enter a number.', self.get_error('foo', locale='en').details().msg())
        self.assert_equals('Bitte geben Sie eine Zahl ein.', self.get_error('foo', locale='de').details().msg())
    
    def test_variable_parts_are_added_after_translation(self):
        expected_message = u'(String erwartet, "list" erhalten)'
        translated_message = self.get_error([], locale='de').details().msg()
        self.assert_contains(expected_message, translated_message)


