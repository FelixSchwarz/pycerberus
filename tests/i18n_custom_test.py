# -*- coding: UTF-8 -*-

from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator


class FrameworkValidator(IntegerValidator):
    def translation_parameters(self, context):
        return {'domain': 'framework'}


class ValidatorWithAdditionalKeys(FrameworkValidator):
    
    def messages(self):
        return {'foo': 'bar'}
    
    def translation_parameters(self, context):
        return {'domain': 'fnord'}
    
    def translate_message(self, key, native_message, translation_parameters, context):
        assert key == 'foo'
        return 'A message from an application validator.'


class SimpleDerivedValidator(ValidatorWithAdditionalKeys):
    pass


class ValidatorRedefiningKeys(FrameworkValidator):
    
    def messages(self):
        return {'empty': 'fnord'}
    
    def translation_parameters(self, context):
        # We need to change back the domain as this validator is used to get
        # a real message - if the .mo file for the gettext domain does not 
        # exist, gettext will raise an error.
        return {'domain': 'pycerberus'}


class ValidatorWithNonGettextTranslation(FrameworkValidator):
    
    def translation_parameters(self, context):
        # we change the domain here on purpose - if gettext would check for 
        # locale files for this domain, it would raise an exception because the
        # file is not there...
        return {'domain': 'application'}
    
    def translate_message(self, key, native_message, translation_parameters, context):
        assert key == 'inactive'
        if context['locale'] == 'de':
            return u'db Übersetzung'
        return 'db translation'
    
    def messages(self):
        return {'inactive': 'Untranslated message'}



class CustomizedI18NBehaviorTest(ValidationTest):
    
    validator_class = ValidatorWithAdditionalKeys
    
    def domain_for_key(self, key):
        gettext_args = self.validator()._implementation(key, 'translation_parameters', {})()
        return gettext_args.get('domain')
    
    def test_validator_can_define_more_translations_while_keeping_existing_ones(self):
        self.assert_equals('Bitte geben Sie einen Wert ein.', self.message_for_key('empty'))
        self.assert_equals('A message from an application validator.', self.message_for_key('foo'))
    
    def test_validator_can_define_custom_parameters_for_translation_mechanism(self):
        self.assert_equals('pycerberus', self.domain_for_key('empty'))
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
        self.assert_equals(u'Bitte geben Sie einen Wert ein.', self.message_for_key('empty'))
        self.init_validator(ValidatorRedefiningKeys())
        self.assert_equals('fnord', self.message_for_key('empty'))
    
    def test_validators_can_use_other_translation_systems_than_gettext(self):
        self.init_validator(ValidatorWithNonGettextTranslation())
        self.assert_equals('db translation', self.message_for_key('inactive', locale='en'))
        self.assert_equals(u'db Übersetzung', self.message_for_key('inactive', locale='de'))
    
    def test_different_translation_system_is_only_applied_to_messages_declared_in_that_class(self):
        self.init_validator(ValidatorWithNonGettextTranslation())
        # This translation is present in the included mo files but not returned
        # by the custom translation method.
        self.assert_equals(u'Bitte geben Sie einen Wert ein.', self.message_for_key('empty'))


