# This file was part of GrumpyWidgets, copyright (c) 2012 Felix Schwarz
# The source code contained in this file is licensed under the MIT license.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import pytest
from pythonic_testcase import *

from pycerberus.errors import InvalidDataError
from pycerberus.lib import AttrDict
from ..form_data import FieldData, FormData


@pytest.fixture
def ctx():
    form = FormData()
    form.children.update({
            'foo': FieldData(value='foo'),
            'bar': FieldData(value=2, initial_value='2', meta={'quox': 'baz'}),
        })

    return AttrDict({
        'form': form,
    })


def _error(message='bad input', value=None):
    return InvalidDataError(message, value)


def test_formdata_can_add_error_for_field(ctx):
    error = _error('bad foo')

    ctx.form.add_errors({'foo': error})
    assert ctx.form.contains_errors()
    assert not ctx.form.global_errors
    assert ctx.form.errors == {'foo': (error, )}


def test_formdata_can_add_global_errors(ctx):
    error1 = _error('global error 1')
    ctx.form.add_errors((error1, ))
    assert ctx.form.contains_errors()
    assert not ctx.form.errors
    assert ctx.form.global_errors == (error1, )

    error2 = _error('global error 2')
    ctx.form.add_errors((error2, ))
    assert len(ctx.form.global_errors) == 2
    assert ctx.form.global_errors == (error1, error2)



class FormDataTest(PythonicTestCase):
    def setUp(self):
        self.context = FormData()
        self.context.children.update({
            'foo': FieldData(value='foo'),
            'bar': FieldData(value=2, initial_value='2', meta={'quox': 'baz'}),
        })

    def test_can_access_children_as_attributes(self):
        foo = self.context.children['foo']
        assert_equals(foo, self.context.foo)

        assert_raises(AttributeError, lambda: self.context.invalid)

    def test_can_copy_itself(self):
        copied_context = self.context.copy()
        del self.context.children['foo']
        self.context.bar.value = 5

        assert_equals(['bar'], list(self.context.children))
        assert_equals(5, self.context.bar.value)

        assert_equals(set(['foo', 'bar']), set(copied_context.children))
        assert_equals(2, copied_context.bar.value)

    def test_can_set_child_values_when_setting_only_child_names(self):
        # FormData should not assume that it only has simple (FieldData) children
        # but only when we absolutely need it.
        context = FormData(child_names=('foo', 'bar'))

        data = {'foo': 'FOO', 'bar': 'BAR'}
        context.set(value=data)
        assert_equals(data, context.value)

    # --- errors --------------------------------------------------------------

    def test_can_tell_if_child_contains_errors(self):
        assert_false(self.context.contains_errors())
        assert_equals(0, self.context.error_count)

        self.context.foo.errors = (self.error(),)
        assert_true(self.context.contains_errors())
        assert_equals(1, self.context.error_count)

    def test_can_tell_if_container_child_contains_errors(self):
        child_container = FormData()
        child_container.children = {'baz': FieldData(errors=(self.error(), ))}
        assert_true(child_container.contains_errors())
        assert_equals(1, child_container.error_count)

        assert_false(self.context.contains_errors())
        assert_equals(0, self.context.error_count)
        self.context.children['complex'] = child_container
        assert_true(self.context.contains_errors())
        assert_equals(1, self.context.error_count)

    def test_can_set_global_errors(self):
        assert_false(self.context.contains_errors())

        errors = (self.error(), )
        self.context.set(errors=errors)
        assert_true(self.context.contains_errors())
        assert_false(self.context.children['foo'].contains_errors())
        assert_false(self.context.children['bar'].contains_errors())
        assert_equals(errors, self.context.global_errors)

#    def test_can_detect_errors_for_repeated_children(self):
#        repeated_context = RepeatingFieldData(None)
#        repeated_context.items = [FieldData(value=1), FieldData(errors=(self.error(),))]
#        self.context.children['items'] = repeated_context
#
#        assert_true(self.context.contains_errors())

    # --- aggregate values ----------------------------------------------------

#    def test_can_return_repeated_values(self):
#        repeating_context = RepeatingFieldData(None)
#        repeating_context.items = [FieldData(value=1), FieldData(value=None)]
#        self.context.children = {'items': repeating_context}
#        assert_equals((1, None), self.context.value['items'])

    def test_can_return_values_from_nested_containers(self):
        complex_child = FormData()
        complex_child.children = {'baz': FieldData(value='qux')}
        self.context.children['complex'] = complex_child

        assert_equals({'baz': 'qux'}, self.context.value['complex'])

    def test_can_return_errors_from_nested_containers(self):
        errors = (self.error(), )
        complex_child = FormData()
        complex_child.children = {'baz': FieldData(errors=errors)}
        self.context.children['complex'] = complex_child

        assert_equals({'baz': errors}, self.context.errors['complex'])

    def test_can_return_initial_values_from_nested_containers(self):
        complex_child = FormData()
        complex_child.children = {'baz': FieldData(initial_value='42')}
        self.context.children['complex'] = complex_child

        assert_equals({'baz': '42'}, self.context.initial_value['complex'])

    # --- setting values ------------------------------------------------------

    def test_can_set_new_values(self):
        values = {'foo': 'baz', 'bar': 42}
        self.context.set(value=values)

        assert_equals(values, self.context.value)

    def test_resets_unspecified_items_when_setting_values(self):
        self.context.set(value={'bar': 42})

        assert_equals({'foo': None, 'bar': 42}, self.context.value)

    def test_can_set_initial_values(self):
        values = {'foo': 'baz', 'bar': 42}
        self.context.set(initial_value=values)

        assert_equals('baz', self.context.foo.initial_value)
        assert_equals(42, self.context.bar.initial_value)

    def test_can_set_meta_values(self):
        values = {'foo': 'baz', 'bar': 42}
        self.context.set(meta=values)

        assert_equals('baz', self.context.foo.meta)
        assert_equals(42, self.context.bar.meta)

    def test_can_set_schema_meta(self):
        values = {'foo': 'baz', 'bar': 42}
        self.context.set(meta=values, schema_meta={'quox': 21})

        assert_equals({'quox': 21}, self.context.schema_meta)
        expected_meta = {'foo': 'baz', 'bar': 42, '_schema_meta': {'quox': 21}}
        assert_equals(expected_meta, self.context.meta)

    def test_does_not_touch_unrelated_values_during_set(self):
        values = {'foo': 'baz', 'bar': 42}
        self.context.set(value=values)
        assert_equals(values, self.context.value)

        initial_values = {'foo': 'bar', 'bar': '42'}
        self.context.set(initial_value=initial_values)
        assert_equals(initial_values, self.context.initial_value)
        assert_equals(values, self.context.value)

    def test_ignores_unknown_children_when_setting_initial_values(self):
        values = {'foo': 'baz', 'quox': 42}
        self.context.set(initial_value=values)

        assert_equals('baz', self.context.foo.initial_value)
        assert_equals(set(['foo', 'bar']), set(self.context.children))

    def test_ignores_mismatched_types_when_setting_initial_values(self):
        field = FieldData()
        schema = FormData(children={'name': field})
        schema.set(initial_value=1)

        assert_none(field.initial_value, message='should ignore mismatched input')

    def test_can_set_errors(self):
        values = {'foo': ('too big', ), 'bar': None}
        self.context.set(errors=values)

        assert_equals({'foo': ('too big',)}, self.context.errors)

    def test_can_set_errors_as_none(self):
        self.context.set(errors={'foo': ('too big', ), 'bar': None})
        assert_true(self.context.contains_errors())

        # setting errors=None to mean "no errors" seems like a "natural" API me
        self.context.set(errors=None)
        assert_false(self.context.contains_errors())
        assert_equals({}, self.context.errors)

    def test_raises_exception_if_values_contain_unknown_key(self):
        values = dict(foo='s1', bar='e1', invalid=None)
        e = assert_raises(ValueError, lambda: self.context.set(values))
        assert_equals("unknown key 'invalid'", e.args[0])

    def test_raises_exception_if_meta_contains_unknown_key(self):
        values = dict(foo='s1', bar='e1', invalid=None)
        e = assert_raises(ValueError, lambda: self.context.set(meta=values))
        assert_equals("unknown key 'invalid'", e.args[0])

    def test_can_set_values_in_nested_containers(self):
        complex_child = FormData()
        complex_child.children = {'baz': FieldData(), 'quox': FieldData()}
        self.context.children['complex'] = complex_child

        self.context.set(value={'complex': {'baz': 'A', 'quox': 'B'}})
        assert_equals({'baz': 'A', 'quox': 'B'}, self.context.value['complex'])

        self.context.set(value={'complex': {'baz': 'C'}})
        assert_equals({'baz': 'C', 'quox': None}, self.context.value['complex'])

    def test_can_set_values_even_if_nested_container_is_present(self):
        complex_child = FormData()
        complex_child.children = {'baz': FieldData()}
        self.context.children['complex'] = complex_child
        assert_equals({'foo': 'foo', 'bar': 2, 'complex': {'baz': None}}, self.context.value)

        self.context.set(value={'foo': '12'})
        assert_equals({'foo': '12', 'bar': None, 'complex': {'baz': None}}, self.context.value)

    # --- update --------------------------------------------------------------

    def test_does_not_change_unspecified_items_when_updating_values(self):
        self.context.update(value={'bar': 42})

        assert_equals({'foo': 'foo', 'bar': 42}, self.context.value)

    def test_can_update_schema_meta(self):
        self.context.update(schema_meta={'quox': 21})
        assert_equals({'quox': 21}, self.context.schema_meta)
        expected_meta = {'foo': {}, 'bar': {'quox': 'baz'}, '_schema_meta': {'quox': 21}}
        assert_equals(expected_meta, self.context.meta)

    # --- helpers -------------------------------------------------------------

    def error(self, message='bad input', value=None):
        return _error(message=message, value=value)