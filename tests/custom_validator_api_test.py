# -*- coding: UTF-8 -*-

from inputvalidation import InvalidDataError
from inputvalidation.api import Validator
from inputvalidation.lib import PythonicTestCase


class ValidatorWithCustomMessageForKey(Validator):
    
    def validate(self, value, state):
        self.error('inactive', value, state)
    
    def messages(self):
        return {'inactive': 'Untranslated message'}
    
    def message_for_key(self, key, state):
        assert key == 'inactive'
        return 'message from custom lookup'



class CustomValidatorAPITest(PythonicTestCase):
    def setUp(self):
        self.super()
        self.validator = ValidatorWithCustomMessageForKey()
    
    def message_for_key(self, key, locale='de'):
        error = self.assert_raises(InvalidDataError, self.validator.error, key, None, {'locale': locale})
        return error.msg

    def test_validators_can_custom_lookup_mechanism_for_messages(self):
        self.assert_equals('message from custom lookup', self.message_for_key('inactive', locale='en'))


