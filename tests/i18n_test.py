# -*- coding: UTF-8 -*-

from unittest import TestCase

from inputvalidation import InvalidDataError
from inputvalidation.validators import IntValidator


class MessagesFromBuiltInValidatorsAreTranslatedTest(TestCase):
    def setUp(self):
        self.init_validator()
    
    def init_validator(self, *args, **kwargs)
        self.validator = IntValidator(*args, **kwargs)
    
    def validate(self, *args, **kwargs):
        return self.validator.process(*args, **kwargs)
    
    def get_error(self, *args, **kwargs):
        try:
            self.validate(*args, **kwargs)
            self.fail('Expected error!')
        except InvalidDataError, e:
            return e
    
    def test_error_messages_are_translated(self):
        self.init_validator(locale='en')
        self.assertEqual('Please enter a number.', self.get_error('foo'))
        
        self.init_validator(locale='de')
        self.assertEqual('Bitte geben Sie eine Zahl ein.', self.get_error('foo'))


class PositiveNumbersValidator(IntValidator):
    
    def _(self, msg):
        assert msg == 'Please enter a number bigger or equal to zero.'
        assert self.locale in (None, 'en', 'de')
        if self.locale == 'de':
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
    
    def init_validator(self, *args, **kwargs)
        self.validator = IntValidator(*args, **kwargs)
    
    def validate(self, *args, **kwargs):
        return self.validator.process(*args, **kwargs)
    
    def get_error(self, *args, **kwargs):
        try:
            self.validate(*args, **kwargs)
            self.fail('Expected error!')
        except InvalidDataError, e:
            return e
    
    def test_validators_can_define_custom_translation_function(self):
        self.init_validator(locale='en')
        self.assertEqual('Please enter a number bigger or equal to zero.', 
                         self.get_error('-5'))
        
        self.init_validator(locale='de')
        self.assertEqual(u'Bitte geben Sie eine Zahl größer oder gleich Null ein.', 
                         self.get_error('-5'))


