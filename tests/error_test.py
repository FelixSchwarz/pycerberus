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

from pycerberus.compat import set
from pycerberus.errors import InvalidArgumentsError, InvalidDataError
from pycerberus.lib.pythonic_testcase import *


class InvalidDataErrorTest(PythonicTestCase):
    
    def test_can_return_list_of_errors(self):
        e = InvalidDataError('a message', 42, error_list=['foo'])
        assert_equals(['foo'], e.errors())
    
    def test_can_not_set_error_dict_and_error_list(self):
        InvalidDataError('a message', 42, error_dict={}, error_list=['foo'])
        InvalidDataError('a message', 42, error_dict={'foo': 'bar'}, error_list=[])
        
        assert_raises(InvalidArgumentsError, 
            lambda: InvalidDataError('a message', 42, error_dict={'foo': 'bar'}, error_list=['foo']))
    
    def test_errors_can_generate_list_of_errors_from_error_dict(self):
        e = InvalidDataError('a message', 42, error_dict={'foo': 42, 'bar': 21})
        assert_equals(set((42, 21)), set(e.errors()))
    
    def test_errors_can_generate_list_of_errors_from_single_error(self):
        e = InvalidDataError('a message', 42)
        assert_equals([e], e.errors())
    
    def _error(self, message='a message', value=42, error_dict=None, error_list=None):
        return InvalidDataError(message, value, error_dict=error_dict, error_list=error_list)
    
    def test_can_unpack_errors_from_error_dict(self):
        foo_error = self._error('foo', 21)
        bar_error = self._error('bar', 21)
        subschema_error = self._error(message='subschema_error', error_dict={'foo': foo_error, 'bar': bar_error})
        wrapping_error = self._error(error_dict={'foobar': subschema_error})
        
        assert_equals({'foobar': {'foo': foo_error, 'bar': bar_error}}, wrapping_error.unpack_errors())
    
    def test_can_unpack_errors_from_error_list(self):
        foo_error = self._error('foo', 21)
        subschema_error = self._error(message='subschema_error', error_list=[foo_error, None])
        wrapping_error = self._error(error_dict={'foobar': subschema_error})
        
        assert_equals({'foobar': [foo_error, None]}, wrapping_error.unpack_errors())

