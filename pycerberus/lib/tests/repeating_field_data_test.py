# This file was part of GrumpyWidgets, copyright (c) 2012 Felix Schwarz
# The source code contained in this file is licensed under the MIT license.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pycerberus.errors import InvalidDataError
from pythonic_testcase import *

from ..form_data import FieldData, FormData, RepeatingFieldData


class RepeatingFieldDataTest(PythonicTestCase):

    def setUp(self):
        self.context = RepeatingFieldData(lambda: None)
        self.context.items = [FieldData(value='foo'), FieldData(value='bar')]

    # --- errors --------------------------------------------------------------

    def test_can_tell_if_child_contains_errors(self):
        assert_false(self.context.contains_errors())
        assert_equals(0, self.context.error_count)

        self.context.items[1].errors = (self.error(),)
        assert_true(self.context.contains_errors())
        assert_equals(1, self.context.error_count)

    # --- aggregate values ----------------------------------------------------

    def test_can_return_repeated_values(self):
        assert_equals(('foo', 'bar'), self.context.value)

    def test_can_return_values_from_nested_containers(self):
        complex_child = FormData()
        complex_child.children = {'baz': FieldData(value='qux')}
        self.context.items = [complex_child]

        assert_equals(({'baz': 'qux'}, ), self.context.value)

    def test_can_return_repeated_errors(self):
        errors = (self.error(), )
        self.context.items[1].errors = errors

        assert_equals((None, errors), self.context.errors)

    def test_can_return_initial_values(self):
        self.context.items[1].initial_value = 'foo'

        assert_equals((None, 'foo'), self.context.initial_value)

    # --- update values -------------------------------------------------------
    def test_can_call_update_without_any_values(self):
        with assert_not_raises():
            self.context.update()

    def test_can_set_new_values(self):
        values = ('baz', 'qox')
        self.context.update(values)

        assert_equals(values, self.context.value)

    def test_can_add_new_items_if_not_previously_set(self):
        values = ('foo', '42')
        self.context.update(values)

        assert_length(2, self.context.value)

    def test_raises_assertion_error_if_existing_length_does_not_match_given_values(self):
        assert_length(2, self.context.items)

        assert_raises(AssertionError, lambda: self.context.update(('foo', )))

    def test_can_set_initial_values(self):
        values = ('foo', '42')
        self.context.update(initial_value=values)

        assert_equals(values, self.context.initial_value)

    def test_can_set_errors(self):
        values = (None, ('too big', 'not applicable'))
        self.context.update(errors=values)

        expected_values = (None, values[1])
        assert_equals(expected_values, self.context.errors)

    def test_can_set_complex_value(self):
        complex_child = FormData()
        complex_child.children = {'baz': FieldData(value='qux')}
        self.context.items = [complex_child]

        input_ = ({'baz': 'foo'}, )
        self.context.update(input_)
        assert_equals(input_, self.context.value)

    # --- helpers -------------------------------------------------------------

    def error(self, message='bad input', value=None):
        return InvalidDataError(message, value)
