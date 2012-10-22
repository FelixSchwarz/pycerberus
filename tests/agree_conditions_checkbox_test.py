# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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

from pycerberus.lib.pythonic_testcase import *
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
