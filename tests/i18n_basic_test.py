# -*- coding: UTF-8 -*-

from unittest import TestCase

from inputvalidation import InvalidDataError
from inputvalidation.validators import IntegerValidator


class MessagesFromBuiltInValidatorsAreTranslatedTest(TestCase):
    def setUp(self):
        self.init_validator()
    
    def init_validator(self, *args, **kwargs):
        self.validator = IntegerValidator(*args, **kwargs)
    
    def validate(self, *args, **kwargs):
        return self.validator.process(*args, **kwargs)
    
    def get_error(self, value, locale=None, *args, **kwargs):
        state = {'locale': locale}
        try:
            self.validate(value, state=state, *args, **kwargs)
            self.fail('Expected error!')
        except InvalidDataError, e:
            return e
    
    def test_error_messages_are_translated(self):
        self.init_validator()
        self.assertEqual('Please enter a number.', self.get_error('foo', locale='en').msg)
        
        self.init_validator()
        self.assertEqual('Bitte geben Sie eine Zahl ein.', self.get_error('foo', locale='de').msg)


