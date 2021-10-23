# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.api import Validator
from pycerberus.errors import ThreadSafetyError
from pycerberus.test_util import ValidationTest


class DetectThreadSafetyViolationInValidatorTest(ValidationTest):
    class NonThreadSafeValidator(Validator):
        def validate(self, value, context):
            self.fnord = 42
    
    validator_class = NonThreadSafeValidator
    
    def test_can_detect_threadsafety_violations(self):
        with assert_raises(ThreadSafetyError):
            self.process(42)

    def test_can_disable_threadsafety_detection(self):
        class ValidatorWrittenByExpert(self.validator_class):
            def __init__(self, *args, **kwargs):
                self._is_internal_state_frozen = False
                super(ValidatorWrittenByExpert, self).__init__(*args, **kwargs)
        self.init_validator(ValidatorWrittenByExpert())
        self.assert_is_valid(42, expected=42)


