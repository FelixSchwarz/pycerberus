# -*- coding: UTF-8 -*-

from unittest import TestCase

from inputvalidation import InvalidDataError
from inputvalidation.api import Validator


class ValidatorWithCustomMessageForKey(Validator):
    
    def validate(self, value, state):
        self.error('inactive', value, state)
    
    def messages(self):
        return {'inactive': 'Untranslated message'}
    
    def message_for_key(self, key, state):
        assert key == 'inactive'
        return 'message from custom lookup'



class CustomValidatorAPITest(TestCase):
    def setUp(self):
        self.validator = ValidatorWithCustomMessageForKey()
    
    def assert_raises(self, exception, method, *args, **kwargs):
        try:
            method(*args, **kwargs)
            self.fail()
        except exception, e:
            return e
    
    def message_for_key(self, key, locale='de'):
        error = self.assert_raises(InvalidDataError, self.validator.error, key, None, {'locale': locale})
        return error.msg

    def test_validators_can_custom_lookup_mechanism_for_messages(self):
        self.assertEqual('message from custom lookup', self.message_for_key('inactive', locale='en'))


