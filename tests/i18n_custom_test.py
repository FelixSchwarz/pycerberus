# -*- coding: UTF-8 -*-

from inputvalidation import InvalidDataError
from inputvalidation.lib import PythonicTestCase
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


class SimpleDerivedValidator(ValidatorWithAdditionalKeys):
    pass


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



class CustomizedI18NBehaviorTest(PythonicTestCase):
    
    def setUp(self):
        self.super()
        self.init(ValidatorWithAdditionalKeys())
    
    def init(self, validator):
        self.validator = validator
    
    def domain_for_key(self, key):
        return self.validator.args_for_gettext(key, {})['domain']
    
    def message_for_key(self, key, locale='de'):
        error = self.assert_raises(InvalidDataError, self.validator.error, key, None, {'locale': locale})
        return error.msg
    
    def test_validator_can_define_more_translations_while_keeping_existing_ones(self):
        self.assert_equals('A message from an application validator.', self.message_for_key('foo'))
        self.assert_equals('Bitte geben Sie einen Wert ein.', self.message_for_key('empty'))
    
    def test_validator_can_define_custom_parameters_for_translation_mechanism(self):
        self.assert_equals('pyinputvalidator', self.domain_for_key('empty'))
        self.assert_equals('fnord', self.domain_for_key('foo'))
    
    def test_parameters_for_translation_are_inherited_from_super_class(self):
        self.assert_equals('fnord', self.domain_for_key('foo'))
        self.init(SimpleDerivedValidator())
        self.assert_equals('fnord', self.domain_for_key('foo'))
    
    def test_use_parameters_for_translation_from_class_where_key_is_defined(self):
        self.init(SimpleDerivedValidator())
        self.assert_equals('framework', self.domain_for_key('invalid_type'))
        self.assert_equals('fnord', self.domain_for_key('foo'))
    
    def test_validators_can_use_their_own_translations_for_existing_keys(self):
        self.assert_equals('Bitte geben Sie einen Wert ein.', self.message_for_key('empty'))
        self.init(ValidatorRedefiningKeys())
        self.assert_equals('fnord', self.message_for_key('empty'))
    
    def test_validators_can_use_other_translation_systems_than_gettext(self):
        self.init(ValidatorWithNonGettextTranslation())
        self.assert_equals('db translation', self.message_for_key('inactive', locale='en'))
        self.assert_equals(u'db Übersetzung', self.message_for_key('inactive', locale='de'))


