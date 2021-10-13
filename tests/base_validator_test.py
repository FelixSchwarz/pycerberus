# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.api import BaseValidator


class BaseValidatorTest(PythonicTestCase):
    def test_can_copy_itself(self):
        class MutableValidator(BaseValidator):
            acceptable_values = [1, 2, 3]
        validator = MutableValidator()
        
        a = validator.copy()
        b = validator.copy()
        a.acceptable_values.append(4)
        
        assert_contains(4, a.acceptable_values)
        assert_not_contains(4, b.acceptable_values)

    def test_can_set_validator_id_via_constructor(self):
        validator = BaseValidator(id='foo')
        assert_equals('foo', validator.id)

    def test_can_generate_validator_id(self):
        class FooBarValidator(BaseValidator):
            pass
        validator = FooBarValidator()
        assert_equals('foo-bar-validator', validator.id)

