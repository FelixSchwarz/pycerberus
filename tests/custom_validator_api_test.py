# -*- coding: UTF-8 -*-

from pycerberus.api import Validator
from pycerberus.test_util import ValidationTest


class ValidatorWithCustomMessageForKey(Validator):
    
    def validate(self, value, context):
        self.error('inactive', value, context)
    
    def messages(self):
        return {'inactive': 'Untranslated message'}
    
    def message_for_key(self, key, context):
        assert key == 'inactive'
        return 'message from custom lookup'



class CustomValidatorAPITest(ValidationTest):
    
    validator_class = ValidatorWithCustomMessageForKey
    
    def test_validators_can_custom_lookup_mechanism_for_messages(self):
        self.assert_equals('message from custom lookup', self.message_for_key('inactive', locale='en'))


