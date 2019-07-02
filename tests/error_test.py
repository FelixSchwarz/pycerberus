# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import re

from pythonic_testcase import *

from pycerberus.errors import Error, InvalidArgumentsError, InvalidDataError


class InvalidDataErrorTest(PythonicTestCase):
    
    def test_can_return_list_of_errors(self):
        e = InvalidDataError('a message', 42, error_list=['foo'])
        assert_equals(('foo', ), e.errors())
    
    def test_can_not_set_error_dict_and_error_list(self):
        InvalidDataError('a message', 42, error_dict={}, error_list=['foo'])
        InvalidDataError('a message', 42, error_dict={'foo': 'bar'}, error_list=[])

        with assert_raises(InvalidArgumentsError):
            InvalidDataError('a message', 42, error_dict={'foo': 'bar'}, error_list=['foo'])
    
    def test_errors_can_generate_list_of_errors_from_error_dict(self):
        e = InvalidDataError('a message', 42, error_dict={'foo': 42, 'bar': 21})
        assert_equals(set((42, 21)), set(e.errors()))
    
    def test_errors_can_generate_list_of_errors_from_single_error(self):
        e = InvalidDataError('a message', 42)
        assert_equals((e, ), e.errors())
    
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


# repr() returns u'...' for "unicode" strings in Python 2. We are using
# "unicode_literals" from __future__ so all strings are treated as unicode.
# As we also test "repr()" outputs let's strip the u'...' for assertions.
_u_repr = lambda s: re.sub("([\=\{])u'", r"\1'", repr(s))

class ErrorTest(PythonicTestCase):
    def test_can_store_attributes(self):
        context = {'quox': 21}
        error = Error(key='foo', msg='bar', value='baz', context=context.copy(), is_critical=False)
        assert_equals('foo', error.key)
        assert_equals('bar', error.msg)
        assert_equals('bar', error.message,
            message='the alias is sometimes helpful as well')
        assert_equals('baz', error.value)
        assert_equals(context, error.context)
        expected_repr = "Error(key='foo', msg='bar', value='baz', context={'quox': 21}, is_critical=False)"
        if "context='[...]'" in repr(error):
            self.skipTest('context stubbed out')
        assert_equals(expected_repr, _u_repr(error))

    def test_can_store_custom_attributes(self):
        error = Error(key='foo', msg='bar', value='baz', context={}, quox=42, foobar=21)
        repr_tmpl = "Error(key='foo', msg='bar', value='baz', context={}, is_critical=True, foobar=21, quox=%d)"
        if "context='[...]'" in repr(error):
            self.skipTest('context stubbed out')
        assert_equals(repr_tmpl % 42, _u_repr(error))

        assert_equals(42, error.quox)
        assert_equals(21, error.foobar)

        error.quox = 12
        assert_equals(12, error.quox)
        assert_equals(repr_tmpl % 12, _u_repr(error))
