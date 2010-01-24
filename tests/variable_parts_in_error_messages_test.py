# -*- coding: UTF-8 -*-

from inputvalidation.errors import InvalidDataError
from inputvalidation.lib import PythonicTestCase
from inputvalidation.validators import IntegerValidator


class VariablePartsInErrorMessages(PythonicTestCase):
    
    def setUp(self):
        self.super()
        self.init(IntegerValidator())
    
    def init(self, validator):
        self.validator = validator
    
    def get_error(self, value, locale='en', *args, **kwargs):
        state = {'locale': locale}
        try:
            self.validator.process(value, state=state, *args, **kwargs)
            self.fail('Expected error!')
        except InvalidDataError, e:
            return e
    
    def message_for_inputvalue(self, value, locale='en'):
        return self.get_error(value, locale=locale).msg
    
    def test_error_messages_can_contain_variable_parts(self):
        self.assert_true('got list)' in self.get_error([]).msg)
    
    def test_variable_parts_are_added_after_translation(self):
        expected_part = 'String erwartet, list erhalten)'
        translated_message = self.get_error([], locale='de').msg
        self.assert_true(expected_part in translated_message, translated_message)



