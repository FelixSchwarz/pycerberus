# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2009-2010 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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

from pycerberus import InvalidArgumentsError, InvalidDataError
from pycerberus.lib.pythonic_testcase import *
from pycerberus.test_util import ValidationTest
from pycerberus.validators import StringValidator



class StringValidatorTest(ValidationTest):
    
    validator_class = StringValidator
    
    def test_accept_string_and_unicode(self):
        self.assert_equals('foo', self.process('foo'))
        self.assert_equals(u'bär', self.process(u'bär'))
    
    def test_reject_bad_types(self):
        assert_raises(InvalidDataError, lambda: self.process([]))
        assert_raises(InvalidDataError, lambda: self.process({}))
        assert_raises(InvalidDataError, lambda: self.process(object))
        assert_raises(InvalidDataError, lambda: self.process(5))
    
    def test_show_class_name_in_error_message(self):
        e = self.assert_raises(InvalidDataError, lambda: self.process([]))
        self.assert_contains(u'(expected string, got "list")', e.details().msg())
    
    def test_empty_string_is_also_empty(self):
        self.assert_error(None)
        self.assert_error('')
        
        self.init_validator(default='foo', required=False)
        self.assert_equals('foo', self.process(None))
        self.assert_equals('foo', self.process(''))
    
    def test_can_specify_min_length(self):
        self.init_validator(StringValidator(min_length=3))
        self.process('foo')
        self.assert_error('fo')
    
    def test_can_specify_max_length(self):
        self.init_validator(StringValidator(max_length=3))
        self.process('foo')
        self.assert_error('foobar')
    
    def test_can_specify_min_and_max_length_together(self):
        self.init_validator(StringValidator(min_length=2, max_length=3))
        self.assert_error('f')
        self.process('fo')
        self.process('foo')
        self.assert_error('foobar')
    
    def test_min_length_must_be_smaller_or_equal_max_length(self):
        assert_raises(InvalidArgumentsError, 
            lambda: StringValidator(min_length=2, max_length=1))


class ValidatorsDerivedFromStringTest(ValidationTest):
    class TrueValidator(StringValidator):
        def convert(self, value, context):
            return True
    
    validator_class = TrueValidator
    
    def test_only_test_for_length_if_explicitely_set(self):
        self.process('5')
        
        self.init_validator(self.validator_class(min_length=0))
        assert_raises(TypeError, lambda: self.process('5'))

