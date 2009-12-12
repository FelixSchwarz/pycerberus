# -*- coding: UTF-8 -*-

from unittest import TestCase

from inputvalidation import EmptyError, InvalidArgumentsError, Validator
from inputvalidation.api import NoValueSet
from inputvalidation.errors import InvalidDataError
from inputvalidation.validators import IntegerValidator


class VariablePartsInErrorMessages(TestCase):
    
    def setUp(self):
        self.init(IntegerValidator())
    
    def init(self, validator):
        self.validator = validator
    
    def assert_raises(self, exception, method, *args, **kwargs):
        try:
            method(*args, **kwargs)
            self.fail()
        except exception, e:
            return e
    
    def message_for_inputvalue(self, value, locale='en'):
        error = self.assert_raises(InvalidDataError, self.validator.process, value, {'locale': locale})
        return error.msg
    
    def test_error_messages_can_contain_variable_parts(self):
        self.assertTrue('got list)' in self.message_for_inputvalue([]))
    
    def _test_variable_parts_are_added_after_translation(self):
        pass
    
    # TODO: Test ngettext?
    



