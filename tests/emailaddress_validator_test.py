# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2010, 2013 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
        self.assert_equals("Invalid character ' ' in email address 'foo bar@example.com'.", e.msg())
    
    def test_reject_domains_with_invalid_characters(self):
        # This is a regression test - actually the EmailAddressValidator and 
        # the DomainNameValidator used the same key which led to strange 
        # KeyErrors
        e = self.get_error('foobar@ex ample.com')
        self.assert_equals("Invalid character ' ' in domain 'ex ample.com'.", e.msg())


