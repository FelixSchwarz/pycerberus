# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2011 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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
from pycerberus.validators import OneOf



class OneOfTest(ValidationTest):
    
    validator_class = OneOf
    validator_args = (['foo', 'bar'], )
    
    def test_passes_if_item_is_in_allowed_values(self):
        self.process('foo')
        self.process('bar')
    
    def test_rejects_values_missing_in_allowed_values(self):
        self.assert_error('baz')
        self.assert_error('foobar')
        self.assert_error(None)
    
    def assert_raises_error_with_key(self, value, error_key):
        assert_equals(error_key, self.assert_error(value).details().key())

