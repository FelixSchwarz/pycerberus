# -*- coding: UTF-8 -*-

from inputvalidation.test_util import ValidationTest
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
        # We need to change back the domain as this validator is used to get
        # a real message - if the .mo file for the gettext domain does not 
        # exist, gettext will raise an error.
        return {'domain': 'pyinputvalidator'}


class ValidatorWithNonGettextTranslation(FrameworkValidator):
    
    def gettextargs(self, state):
        # we change the domain here on purpose - if gettext would check for 
        # locale files for this domain, it would raise an exception because the
        # file is not there...
        return {'domain': 'application'}
    
    def translate_message(self, native_message, gettextargs, key, state):
        assert key == 'inactive'
        if self.locale(state) == 'de':
            return u'db Übersetzung'
        return 'db translation'
    
    def messages(self):
        return {'inactive': 'Untranslated message'}



class CustomizedI18NBehaviorTest(ValidationTest):
    
    validator_class = ValidatorWithAdditionalKeys
    
    def domain_for_key(self, key):
        gettext_args = self.validator().args_for_gettext(key, {})
        return gettext_args.get('domain')
    
    def test_validator_can_define_more_translations_while_keeping_existing_ones(self):
        self.assert_equals('Bitte geben Sie einen Wert ein.', self.message_for_key('empty'))
        self.assert_equals('A message from an application validator.', self.message_for_key('foo'))
    
    def test_validator_can_define_custom_parameters_for_translation_mechanism(self):
        self.assert_equals('pyinputvalidator', self.domain_for_key('empty'))
        self.assert_equals('fnord', self.domain_for_key('foo'))
    
    def test_parameters_for_translation_are_inherited_from_super_class(self):
        self.assert_equals('fnord', self.domain_for_key('foo'))
        self.init_validator(SimpleDerivedValidator())
        self.assert_equals('fnord', self.domain_for_key('foo'))
    
    def test_use_parameters_for_translation_from_class_where_key_is_defined(self):
        self.init_validator(SimpleDerivedValidator())
        self.assert_equals('framework', self.domain_for_key('invalid_type'))
        self.assert_equals('fnord', self.domain_for_key('foo'))
    
    def test_validators_can_use_their_own_translations_for_existing_keys(self):
        self.assert_equals('Bitte geben Sie einen Wert ein.', self.message_for_key('empty'))
        self.init_validator(ValidatorRedefiningKeys())
        self.assert_equals('fnord', self.message_for_key('empty'))
    
    def test_validators_can_use_other_translation_systems_than_gettext(self):
        self.init_validator(ValidatorWithNonGettextTranslation())
        self.assert_equals('db translation', self.message_for_key('inactive', locale='en'))
        self.assert_equals(u'db Übersetzung', self.message_for_key('inactive', locale='de'))


