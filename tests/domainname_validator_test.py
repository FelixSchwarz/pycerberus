# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.test_util import ValidationTest
from pycerberus.validators import DomainNameValidator


class DomainNameValidatorTest(ValidationTest):
    
    validator_class = DomainNameValidator
    
    def test_accepts_simple_domain_names(self):
        assert_equals('example.com', self.process('example.com'))
        assert_equals('bar-baz.example', self.process('bar-baz.example'))

    def test_reject_domain_with_leading_dot(self):
        msg = self.assert_error('.example.com').msg()
        assert_equals('Invalid domain: ".example.com" must not start with a dot.', msg)

    def test_reject_domain_with_trailing_dot(self):
        # Actually this test might be a bit fishy as this is actually a valid 
        # domain name. I guess the notion of 'domain name' varies, depending
        # on the context
        msg = self.assert_error('example.com.').msg()
        assert_equals('Invalid domain: "example.com." must not end with a dot.', msg)

    def test_reject_domain_with_double_dots(self):
        msg = self.assert_error('example..com').msg()
        assert_equals('Invalid domain: "example..com" must not contain consecutive dots.', msg)

    def test_reject_domain_with_invalid_characters(self):
        msg = self.assert_error('foo_bar.example').msg()
        assert_equals('Invalid character "_" in domain "foo_bar.example".', msg)

