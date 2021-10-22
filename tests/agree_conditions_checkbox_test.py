# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.test_util import ValidationTest
from pycerberus.validators import AgreeToConditionsCheckbox


class AgreeToConditionsCheckboxTest(ValidationTest):
    validator_class = AgreeToConditionsCheckbox
    
    def test_accepts_true(self):
        for _input in ('true', True, '1', 'on'):
            self.assert_is_valid(_input, expected=True)

    def test_rejects_unchecked_checkbox(self):
        for input_ in (False, None, ''):
            self.assert_error_with_key('must_agree', input_)
