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
from pycerberus.schema import SchemaValidator
from pycerberus.test_util import ValidationTest
from pycerberus.validators import BooleanCheckbox


class BooleanCheckboxTest(ValidationTest):
    
    validator_class = BooleanCheckbox
    
    def test_false_values(self):
        assert_false(self.process('off'))
        assert_false(self.process('false'))
        assert_false(self.process(False))
        assert_false(self.process(None))
        assert_false(self.process(''))
    
    def test_true_values(self):
        assert_true(self.process('on'))
        assert_true(self.process('true'))
        assert_true(self.process(True))
    
    def test_strips_by_default(self):
        assert_true(self.process('  true  '))
    
    def test_ignores_case(self):
        assert_true(self.process('ON'))
        assert_true(self.process('TrUe'))
        assert_false(self.process('oFf'))
        assert_false(self.process('FaLsE'))
    
    def test_rejects_values_which_are_neither_true_nor_false(self):
        e = self.assert_error('maybe')
        assert_equals('unknown_bool', e.details().key())
    
    def test_treat_missing_value_in_schema_as_false(self):
        # regression test!
        class CheckboxSchema(SchemaValidator):
            allow_additional_parameters = True
            decision = BooleanCheckbox()
        assert_equals({'decision': False}, CheckboxSchema().process({}))
        assert_equals({'decision': False}, CheckboxSchema().process({'foo': 'bar'}))
    
    def test_can_revert_conversion_for_falsish_values(self):
        assert_false(self.revert_conversion(False))
        assert_false(self.revert_conversion('false'))
        assert_false(self.revert_conversion('FALSE'))
        assert_false(self.revert_conversion('off'))
        assert_false(self.revert_conversion(None))
        assert_false(self.revert_conversion([]))
        assert_false(self.revert_conversion('invalid'))
    
    def test_can_revert_conversion_for_trueish_values(self):
        assert_true(self.revert_conversion(True))
        assert_true(self.revert_conversion('true'))
        assert_true(self.revert_conversion('TRUE'))
        assert_true(self.revert_conversion('on'))
        assert_true(self.revert_conversion('t'))

