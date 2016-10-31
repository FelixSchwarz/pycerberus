# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.

from pythonic_testcase import *

from pycerberus.test_util import ValidationTest
from pycerberus.validators import AgreeToConditionsCheckbox


class AgreeToConditionsCheckboxTest(ValidationTest):
    validator_class = AgreeToConditionsCheckbox
    
    def test_accepts_true(self):
        assert_true(self.process('true'))
        assert_true(self.process(True))
        assert_true(self.process('1'))
        assert_true(self.process('on'))
    
    def test_rejects_unchecked_checkbox(self):
        for input_ in (False, None, ''):
            e = self.assert_error(input_)
            assert_equals('must_agree', e.details().key())
