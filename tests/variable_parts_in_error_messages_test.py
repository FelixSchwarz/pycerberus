# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator


class VariablePartsInErrorMessages(ValidationTest):
    
    validator_class = IntegerValidator
    
    def test_error_messages_can_contain_variable_parts(self):
        error = self.assert_error_with_locale([], locale='en', _return_error=True)
        assert_contains('got "list"', error.msg())

    def test_variable_parts_are_added_after_translation(self):
        expected_part = '(String erwartet, "list" erhalten)'
        error = self.assert_error_with_locale([], locale='de', _return_error=True)
        assert_contains(expected_part, error.msg())



