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

from pycerberus.errors import InvalidArgumentsError
from pycerberus.lib.pythonic_testcase import *
from pycerberus.test_util import ValidationTest
from pycerberus.validators import ForEach, IntegerValidator



class ForEachTest(ValidationTest):
    
    validator_class = ForEach
    validator_args = (IntegerValidator, )
    
    def _invalid_message(self):
        return IntegerValidator().message('invalid_number', {})
    
    def test_passes_for_empty_lists(self):
        self.process([])
    
    def test_passes_if_every_single_item_passes(self):
        self.process((21, 42,))
    
    def test_applied_validator_can_convert_items(self):
        assert_equals((21, 42), self.process(('21', '42')))
    
    def test_applies_validator_to_first_item(self):
        errors = self.assert_error(['bar']).errors()
        
        assert_length(1, errors)
        assert_equals(self._invalid_message(), errors[0].msg())
    
    def test_applies_validator_to_every_item(self):
        errors = self.assert_error(['bar', 'baz']).errors()
        
        assert_length(2, errors)
        assert_equals(self._invalid_message(), errors[0].msg())
        assert_equals(self._invalid_message(), errors[1].msg())
    
    def test_returns_sparse_error_list(self):
        errors = self.assert_error(['bar', '42']).errors()
        
        assert_length(2, errors)
        assert_equals(self._invalid_message(), errors[0].msg())
        assert_equals(None, errors[1])
    
    def test_works_with_validator_instances(self):
        # This is important if validators need some configuration in the 
        # constructor
        self.init_validator(ForEach(IntegerValidator()))
        self.process((42,))
    
    def assert_raises_error_with_key(self, value, error_key):
        assert_equals(error_key, self.assert_error(value).details().key())
    
    def test_rejects_missing_field(self):
        self.assert_raises_error_with_key(None, 'empty')
    
    def test_rejects_non_iteratible_types(self):
        self.assert_raises_error_with_key(object(), 'invalid_type')
        self.assert_raises_error_with_key(42, 'invalid_type')
    
    def test_can_specify_min_amount_of_items(self):
        self.init_validator(ForEach(IntegerValidator, min_length=2))
        self.process((21, 42))
        
        self.assert_raises_error_with_key((), 'too_short')
        self.assert_raises_error_with_key((21,), 'too_short')
    
    def test_can_specify_max_amount_of_items(self):
        self.init_validator(ForEach(IntegerValidator, max_length=2))
        self.process((21, 42))
        
        self.assert_raises_error_with_key((21, 42, 63), 'too_long')
    
    def test_can_specify_min_length_and_max_lenght(self):
        self.init_validator(ForEach(IntegerValidator, min_length=1, max_length=1))
        self.process((21,))
        self.assert_raises_error_with_key((), 'too_short')
        self.assert_raises_error_with_key((21, 42), 'too_long')
    
    def test_min_length_must_be_smaller_or_equal_max_length(self):
        assert_raises(InvalidArgumentsError, 
            lambda: ForEach(IntegerValidator, min_length=2, max_length=1))
    
    def test_returns_empty_tuple_if_not_required_and_no_value_given(self):
        validator = ForEach(IntegerValidator, required=False)
        assert_equals((), validator.empty_value({}))
    
    def test_can_set_validator_arguments_for_constructor(self):
        self.init_validator(ForEach(IntegerValidator, default=[], required=False))
        assert_equals([], self.process(None))

