# -*- coding: UTF-8 -*-

from unittest import TestCase

from inputvalidation import InvalidDataError
from inputvalidation.i18n import _
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


class PositiveNumbersValidator(IntegerValidator):
    
    def translate_message(self, msg, state):
        assert msg == 'Please enter a number bigger or equal to zero.'
        assert self.locale(state) in (None, 'en', 'de')
        if self.locale(state) == 'de':
            return u'Bitte geben Sie eine Zahl größer oder gleich Null ein.'
        return msg
    
    messages = {'too_low': _('Please enter a number bigger or equal to zero.')}
    
    def validate(self, value, state=None):
        super(PositiveNumbersValidator, self).validate(value, state=state)
        if value < 0:
            self.error('too_low', value, state)


class CustomValidatorsCanDeclareOwnTranslationFunction(TestCase):
    def setUp(self):
        self.init_validator()
    
    def init_validator(self, *args, **kwargs):
        self.validator = PositiveNumbersValidator(*args, **kwargs)
    
    def validate(self, *args, **kwargs):
        return self.validator.process(*args, **kwargs)
    
    def get_error(self, value, locale=None, *args, **kwargs):
        state = {'locale': locale}
        try:
            self.validate(value, state=state, *args, **kwargs)
            self.fail('Expected error!')
        except InvalidDataError, e:
            return e
    
    def test_validators_can_define_custom_translation_function(self):
        self.init_validator()
        self.assertEqual('Please enter a number bigger or equal to zero.', 
                         self.get_error('-5', locale='en').msg)
        
        self.init_validator()
        self.assertEqual(u'Bitte geben Sie eine Zahl größer oder gleich Null ein.', 
                         self.get_error('-5', locale='de').msg)


