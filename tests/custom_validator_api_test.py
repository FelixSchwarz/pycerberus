# -*- coding: UTF-8 -*-

from inputvalidation.api import Validator
from inputvalidation.test_util import ValidationTest


class ValidatorWithCustomMessageForKey(Validator):
    
    def validate(self, value, state):
        self.error('inactive', value, state)
    
    def messages(self):
        return {'inactive': 'Untranslated message'}
    
    def message_for_key(self, key, state):
        assert key == 'inactive'
        return 'message from custom lookup'



class CustomValidatorAPITest(ValidationTest):
    
    validator_class = ValidatorWithCustomMessageForKey
    
    def test_validators_can_custom_lookup_mechanism_for_messages(self):
        self.assert_equals('message from custom lookup', self.message_for_key('inactive', locale='en'))


