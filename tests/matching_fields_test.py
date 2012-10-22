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
from pycerberus.validators import MatchingFields


class MatchingFieldsTest(ValidationTest):
    
    validator_class = MatchingFields
    validator_args = ('foo', 'bar')
    
    def test_accepts_if_both_fields_are_equal(self):
        self.process(dict(foo='', bar=''))
        self.process(dict(foo=None, bar=None))
        self.process(dict(foo='value', bar='value'))
    
    def test_rejects_fields_with_unequal_content(self):
        self.assert_error(dict(foo='', bar=None))
        self.assert_error(dict(foo='first', bar='second'))
    
    def test_marks_second_field_as_faulty(self):
        e = self.assert_error(dict(foo='', bar=None))
        
        errors = e.unpack_errors()
        assert_equals(['bar'], list(errors))
        assert_not_none(errors['bar'])
        bar_error = errors['bar'].details()
        assert_equals('mismatch', bar_error.key())
