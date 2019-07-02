# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.

from __future__ import absolute_import, print_function, unicode_literals

from pycerberus.test_util import ValidationTest
from pycerberus.validators import EmailAddressValidator


class EmailAddressValidatorTest(ValidationTest):
    
    validator_class = EmailAddressValidator
    
    def _assert_valid_email(self, address_string):
        self.assert_equals(address_string, self.process(address_string))
    
    def test_accepts_simple_email_address(self):
        self._assert_valid_email('foo@example.com')
        self._assert_valid_email('foo.bar@example.com')
        self._assert_valid_email('foo_bar@example.com')
        self._assert_valid_email('foo@bar-baz.example')
        self._assert_valid_email('foo+bar@example.com')
        self._assert_valid_email('foo-bar@example.com')
    
    def test_reject_email_address_without_at(self):
        e = self.get_error('example.com')
        self.assert_equals("An email address must contain a single '@'.", e.msg())
    
    def test_reject_email_address_with_multiple_at_characters(self):
        e = self.get_error('foo@bar@example.com')
        self.assert_equals("An email address must contain a single '@'.", e.msg())
    
    def test_reject_localpart_with_space(self):
        e = self.get_error('foo bar@example.com')
        self.assert_equals('Invalid character " " in email address "foo bar@example.com".', e.msg())

    def test_reject_domains_with_invalid_characters(self):
        # This is a regression test - actually the EmailAddressValidator and 
        # the DomainNameValidator used the same key which led to strange 
        # KeyErrors
        e = self.get_error('foobar@ex ample.com')
        self.assert_equals('Invalid character " " in domain "ex ample.com".', e.msg())

    def test_reject_missing_domain(self):
        e = self.get_error('foobar@')
        self.assert_equals('Missing domain in email address "foobar@".', e.msg())

