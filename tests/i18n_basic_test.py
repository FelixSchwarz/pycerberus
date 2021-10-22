# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator


class MessagesFromBuiltInValidatorsAreTranslatedTest(ValidationTest):
    
    validator_class = IntegerValidator
    
    def test_error_messages_are_translated(self):
        error_en = self.assert_error_with_locale('foo', locale='en', _return_error=True)
        assert_equals('Please enter a number.', error_en.msg())
        error_de = self.assert_error_with_locale('foo', locale='de', _return_error=True)
        assert_equals('Bitte geben Sie eine Zahl ein.', error_de.msg())

    def test_variable_parts_are_added_after_translation(self):
        expected_message = u'(String erwartet, "list" erhalten)'
        error_de = self.assert_error_with_locale([], locale='de', _return_error=True)
        assert_contains(expected_message, error_de.msg())

    def test_fallback_to_english_translation_for_unknown_locales(self):
        error_en = self.assert_error_with_locale('foo', locale='unknown', _return_error=True)
        assert_equals('Please enter a number.', error_en.msg())


