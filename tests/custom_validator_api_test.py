# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.api import Validator
from pycerberus.test_util import ValidationTest


class ValidatorWithCustomMessageForKey(Validator):
    exception_if_invalid = True

    def validate(self, value, context):
        self.raise_error('inactive', value, context)
    
    def messages(self):
        return {'inactive': 'Untranslated message'}
    
    def message_for_key(self, key, context):
        assert key == 'inactive'
        return 'message from custom lookup'


class AdditionalMessagesValidator(Validator):
    exception_if_invalid = True

    def messages(self):
        # need to have multiple messages, therefore 'ValidatorWithCustomMessageForKey'
        # is not suitable
        return {
            'disabled': 'account disabled',
            'deleted': 'account deleted',
        }
    
    def validate(self, value, context):
        if value in ('disabled', 'deleted'):
            self.raise_error(value, value, context)
        raise AssertionError('unknown value in validate')


class CustomValidatorAPITest(ValidationTest):
    
    def test_validators_can_use_custom_lookup_mechanism_for_messages(self):
        self.init_validator(ValidatorWithCustomMessageForKey())
        assert_equals('message from custom lookup', self.message_for_key('inactive'))

    def test_can_specify_additional_messages_during_instantiation(self):
        validator = AdditionalMessagesValidator(messages={
            'deleted': 'Your account was deleted.'
        })
        self.init_validator(validator)

        assert_equals({
            'disabled': 'account disabled',
            'deleted': 'Your account was deleted.',
        }, validator.messages())
        assert_equals('account disabled', validator.message_for_key('disabled', {}))
        assert_equals('Your account was deleted.', validator.message_for_key('deleted', {}))
        assert_equals(set(['disabled', 'deleted']), set(validator.keys()))

        assert_equals('account disabled', self.message_for_key('disabled'))
        assert_equals('Your account was deleted.', self.message_for_key('deleted'))
        assert_equals('Value must not be empty.', self.message_for_key('empty', locale='en'))

    def test_can_replace_builtin_messages_during_instantion(self):
        validator_messages = AdditionalMessagesValidator().messages()
        assert_not_contains('empty', validator_messages,
            message='the bug only occurred when the validator class did not override the key itself.')
        new_msg = 'Please select any value.'
        validator = AdditionalMessagesValidator(messages={
            'empty': new_msg,
        })
        self.init_validator(validator)

        assert_equals(new_msg, self.message_for_key('empty'))
        assert_equals('account deleted', self.message_for_key('deleted'),
            message='class-level message definitions should still work')


class CanDeclareMessagesInClassDictValidator(Validator):
    exception_if_invalid = True
    messages = {'classlevel': 'Message from class-level.'}
    
    def validate(self, value, context):
        self.raise_error('classlevel', value, context)


class CanDeclareMessagesInClassDictTest(ValidationTest):
    
    validator_class = CanDeclareMessagesInClassDictValidator
    
    def test_can_declare_messages_in_classdict(self):
        assert_equals('Message from class-level.', self.message_for_key('classlevel'))


