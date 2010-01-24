# -*- coding: UTF-8 -*-

from inputvalidation import InvalidDataError
from inputvalidation.lib import PythonicTestCase
from inputvalidation.validators import IntegerValidator


class MessagesFromBuiltInValidatorsAreTranslatedTest(PythonicTestCase):
    def setUp(self):
        self.super()
        self.init_validator()
    
    def init_validator(self, *args, **kwargs):
        self.validator = IntegerValidator(*args, **kwargs)
    
    def get_error(self, value, locale=None, *args, **kwargs):
        state = {'locale': locale}
        return self.assert_raises(InvalidDataError, self.validator.process, value, state=state, *args, **kwargs)
    
    def test_error_messages_are_translated(self):
        self.init_validator()
        self.assert_equals('Please enter a number.', self.get_error('foo', locale='en').msg)
        
        self.init_validator()
        self.assert_equals('Bitte geben Sie eine Zahl ein.', self.get_error('foo', locale='de').msg)
    
    def test_variable_parts_are_added_after_translation(self):
        expected_message = 'String erwartet, list erhalten)'
        
        self.init_validator()
        translated_message = self.get_error([], locale='de').msg
        self.assert_true(expected_message in translated_message)


