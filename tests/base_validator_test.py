# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.

from pycerberus.api import BaseValidator
from pycerberus.lib.pythonic_testcase import *


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
