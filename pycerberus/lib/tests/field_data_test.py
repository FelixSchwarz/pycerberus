# This file was part of GrumpyWidgets, copyright (c) 2012 Felix Schwarz
# The source code contained in this file is licensed under the MIT license.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pycerberus.errors import InvalidDataError
from pythonic_testcase import *

from ..form_data import FieldData

class FieldDataTest(PythonicTestCase):

    def setUp(self):
        self.context = FieldData()

    def error(self, message='bad input', value=None):
        return InvalidDataError(message, value)

    def test_can_set_attributes_during_initialization(self):
        assert_equals(5, FieldData(value=5).value)

        error = self.error()
        assert_equals([error], FieldData(errors=[error]).errors)

        assert_equals('42', FieldData(initial_value='42').initial_value)

        assert_equals({'foo': 'bar'}, FieldData(meta={'foo': 'bar'}).meta)

    def test_can_clone_itself(self):
        self.context.value = {}
        self.context.errors = []
        self.context.meta = {'x': 42}

        clone = self.context.copy()
        clone.errors.append('new error')
        clone.value['new'] = 21
        clone.meta['y'] = 21

        assert_equals({}, self.context.value)
        assert_equals([], self.context.errors)
        assert_equals({'x': 42}, self.context.meta)
        assert_equals({'new': 21}, clone.value)
        assert_equals(['new error'], clone.errors)
        assert_equals({'x': 42, 'y': 21}, clone.meta)

    def test_knows_if_context_contains_errors(self):
        self.context.errors = None
        assert_false(self.context.contains_errors())
        assert_equals(0, self.context.error_count)

        self.context.errors = []
        assert_false(self.context.contains_errors())
        assert_equals(0, self.context.error_count)

        self.context.errors = (self.error(),)
        assert_true(self.context.contains_errors())
        assert_equals(1, self.context.error_count)

    def test_can_set_new_value(self):
        self.context.set(value='bar')

        assert_equals('bar', self.context.value)

    def test_can_set_initial_attribute_when_updating_values(self):
        context = FieldData()
        context.update(initial_value='42')

        assert_equals('42', context.initial_value)

    def test_can_set_errors_attribute_when_updating_values(self):
        context = FieldData()
        context.update(errors=(4,))

        assert_equals((4,), context.errors)

    def test_can_set_meta_attribute_when_updating_values(self):
        context = FieldData()
        context.update(meta={'foo': 'bar'})

        assert_equals({'foo': 'bar'}, context.meta)

    def test_can_set_errors_as_none(self):
        context = FieldData()
        context.update(errors=(4, ))
        assert_true(context.contains_errors())

        # setting errors=None to mean "no errors" seems like a "natural" API me
        context.update(errors=None)
        assert_false(context.contains_errors())
        assert_equals((), context.errors)

    def test_can_add_error(self):
        context = FieldData()
        context.update(errors=(4, ))
        assert_equals((4,), context.errors)
        context.add_error(6)
        assert_equals((4, 6), context.errors)

    def test_can_set_exception_for_errors(self):
        # Python 2 happily converts tuple(exception) to tuple((exception_msg,))
        # which I found highly surprising. This test ensures that we take care
        # of the special case.
        # This is not a problem in Python 3 where Exception is not iterable
        # anymore
        e = Exception('foo')
        context = FieldData()
        context.update(errors=e)
        assert_true(context.contains_errors())
        assert_equals((e, ), context.errors,
            message='we should get the initial exception instance even in Python 2')

    def test_update_as_alias_for_set(self):
        self.context.set(value='bar')

        assert_equals('bar', self.context.value)


