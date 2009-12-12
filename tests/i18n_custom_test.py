# -*- coding: UTF-8 -*-

from unittest import TestCase

from inputvalidation import InvalidDataError
from inputvalidation.validators import IntegerValidator


class FrameworkValidator(IntegerValidator):
    def gettextargs(self, state):
        return {'domain': 'framework'}

class ValidatorWithAdditionalKeys(FrameworkValidator):
    
    def messages(self):
        return {'foo': 'bar'}
    
    def gettextargs(self, state):
        return {'domain': 'fnord'}
    
    def translate_message(self, native_message, gettextargs, key, state):
        assert key == 'foo'
        return 'A message from an application validator.'

class ValidatorRedefiningKeys(FrameworkValidator):
    
    def messages(self):
        return {'empty': 'fnord'}
    
    def gettextargs(self, state):
        return {'domain': 'application'}

class ValidatorWithNonGettextTranslation(FrameworkValidator):
    
    def translate_message(self, native_message, gettextargs, key, state):
        assert key == 'inactive'
        if self.locale(state) == 'de':
            return u'db Übersetzung'
        return 'db translation'
    
    def messages(self):
        return {'inactive': 'Untranslated message'}


class MyApplicationValidator(FrameworkValidator):
    # a class that does not declare any method - test that no method must be
    # implemented.
    pass


class CustomizedI18NBehaviorTest(TestCase):
    
    def setUp(self):
        self.init(ValidatorWithAdditionalKeys())
    
    def init(self, validator):
        self.validator = validator
    
    def assert_raises(self, exception, method, *args, **kwargs):
        try:
            method(*args, **kwargs)
            self.fail()
        except exception, e:
            return e
    
    def domain_for_key(self, key):
        return self.validator.args_for_gettext(key, {})['domain']
    
    def message_for_key(self, key, locale='de'):
        error = self.assert_raises(InvalidDataError, self.validator.error, key, None, {'locale': locale})
        return error.msg
    
    def test_validator_can_define_more_translations_while_keeping_existing_ones(self):
        self.assertEqual('A message from an application validator.', self.message_for_key('foo'))
        self.assertEqual('Bitte geben Sie einen Wert ein.', self.message_for_key('empty'))
    
    def test_validator_can_define_custom_parameters_for_translation_mechanism(self):
        self.assertEqual('pyinputvalidator', self.domain_for_key('empty'))
        self.assertEqual('fnord', self.domain_for_key('foo'))
    
    def test_validators_can_use_their_own_translations_for_existing_keys(self):
        self.assertEqual('Bitte geben Sie einen Wert ein.', self.message_for_key('empty'))
        self.init(ValidatorRedefiningKeys())
        self.assertEqual('fnord', self.message_for_key('empty'))
    
    def test_validators_can_use_other_translation_systems_than_gettext(self):
        self.init(ValidatorWithNonGettextTranslation())
        self.assertEqual('db translation', self.message_for_key('inactive', locale='en'))
        self.assertEqual(u'db Übersetzung', self.message_for_key('inactive', locale='de'))


# TODO: Test you can use your own keys
# TODO: Test you can have your own message_for_key (e.g. depending on state)

