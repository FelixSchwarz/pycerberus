# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.

from pythonic_testcase import *

from pycerberus.errors import Error, InvalidDataError
from pycerberus.error_conversion import exception_from_errors, exception_to_errors
from pycerberus.lib.form_data import is_simple_error


class ExceptionToErrorsTest(PythonicTestCase):
    def test_can_convert_error_list_to_errors(self):
        error_in_list = self._exception(message='error in list')
        exc = self._exception(error_list=(error_in_list,))

        errors = exception_to_errors(exc)
        assert_length(1, errors)
        error = errors[0]
        assert_isinstance(error, Error)
        assert_equals('error in list', error.message)

    def _exception(self, message='a message', value=42, error_dict=None, error_list=None):
        return InvalidDataError(message, value, error_dict=error_dict, error_list=error_list)


class ErrorsToExceptionTest(PythonicTestCase):
    def test_can_convert_simple_error(self):
        error = self._error(key='foo', message='bar', value=21)
        exc = exception_from_errors(error)
        assert_isinstance(exc, InvalidDataError)
        details = exc.details()
        assert_equals('foo', details.key())
        assert_equals('bar', details.msg())
        assert_equals(21, details.value())
        assert_is_empty(exc._error_dict)
        assert_is_empty(exc._error_list)

    def test_can_convert_error_list(self):
        e1 = self._error(key='foo', message='bar', value=21)
        e2 = self._error(key='bar', message='baz', value=42)
        container_exc = exception_from_errors((e1, None, e2))
        assert_isinstance(container_exc, InvalidDataError)

        assert_length(3, container_exc.errors())
        exc1, exc_none, exc2 = container_exc.errors()
        assert_equals('foo', exc1.details().key())
        assert_equals((exc1, ), exc1.errors())
        assert_none(exc_none,
            message='This happens for ForEach if one item is valid.')
        assert_equals('bar', exc2.details().key())
        assert_equals((exc2, ), exc2.errors())

    def test_can_convert_error_list_with_error_dicts(self):
        schema_error = self._error(key='bad', message='bar', value=21)
        errors = ({}, {'number': (schema_error, )})
        container_exc = exception_from_errors(errors)

        details = container_exc.details()
        assert_equals('bad', details.key())
        item_errors = container_exc.errors()

        assert_length(2, item_errors)
        item2 = item_errors[1]
        details2 = item2.details()
        assert_equals('bad', details2.key())

        item2_errors = item2._error_dict
        assert_equals(('number',), tuple(item2_errors))
        number_error = item2_errors['number']
        assert_isinstance(number_error, InvalidDataError)

    def test_can_convert_error_dict_with_nested_lists_and_dicts(self):
        id_error = self._error(key='foobar')
        errors = {'foo': (
            {'id': (id_error,)},
        )}
        container_exc = exception_from_errors(errors)
        assert_equals('foobar', container_exc.details().key(),
            message='main container uses the right error key')

        foo_container = container_exc._error_dict['foo']
        assert_length(1, foo_container._error_list)
        schema1 = foo_container._error_list[0]
        assert_equals(set(('id',)), set(schema1._error_dict))
        id_error = schema1._error_dict['id']
        assert_isinstance(id_error, InvalidDataError)
        # pycerberus can represent multiple errors for a single field but we
        # are using the old exception-based API so the initial "(id_error,)"
        # is transformed to a single error.
        assert_is_empty(id_error._error_list,
            message='should be a "leaf" error without error list/dict')
        assert_is_empty(id_error._error_dict)

    def test_can_convert_empty_error_list(self):
        id_error = self._error(key='foobar')
        errors = {
            'foo': ((), ()),
            'bar': (id_error, ),
        }
        container_exc = exception_from_errors(errors)
        assert_equals('foobar', container_exc.details().key())
        error_dict = container_exc.error_dict()
        assert_equals(None, error_dict['foo'])

        bar_error = error_dict['bar']
        assert_true(is_simple_error(bar_error))
        bar_details = bar_error.details()
        assert_equals(id_error.key, bar_details.key())

    def _error(self, key='foo', message='a message', value=42):
        return Error(key=key, msg=message, value=value, context=None, is_critical=True)
