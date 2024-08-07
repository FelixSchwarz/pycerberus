# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.api import Error, Validator
from pycerberus.compat import OrderedDict
from pycerberus.errors import InvalidArgumentsError, InvalidDataError
from pycerberus.lib import AttrDict
from pycerberus.schema import SchemaValidator
from pycerberus.test_util import error_keys, ValidationTest
from pycerberus.validators import ForEach, IntegerValidator, StringValidator



def exploding_validator():
    def mock_process(fields, context=None):
        raise ValueError('boooom!')
    return AttrDict(process=mock_process)

def failing_validator(fields=None, exception_if_invalid=True):
    error_fields = fields
    raising_validator = exception_if_invalid

    # using a real validator here uncovered quite a few integration issues
    # (e.g. bad context type for FormValidators)
    class FailingValidator(Validator):
        exception_if_invalid = raising_validator

        def convert(self, fields, context):
            if exception_if_invalid:
                assert (error_fields is None), 'specific fields not supported'
                raise InvalidDataError('foo', fields, 'key', context)
            if not error_fields:
                result = context['result']
                error = Error('key', 'msg for global error', fields, context)
                result.global_errors = result.global_errors + (error,)
            else:
                result = context['result']
                value = None
                for fieldname in error_fields:
                    error = Error('key', 'error for %s', value, context)
                    result.children[fieldname].add_error(error)
            return fields

    return FailingValidator()



class SchemaTest(ValidationTest):
    def _schema(self, fields=('id',), formvalidators=(), **kwargs):
        schema = SchemaValidator(**kwargs)
        assert set(fields).issubset(set(('id', 'key')))
        if 'id' in fields:
            schema.add('id', IntegerValidator())
        if 'key' in fields:
            schema.add('key', StringValidator())
        for formvalidator in formvalidators:
            schema.add_formvalidator(formvalidator)
        return schema

    def init_validator(self, validator=None, *args, **kwargs):
        if validator is None:
            validator = self._schema()
        return super(SchemaTest, self).init_validator(validator=validator, *args, **kwargs)

    # -------------------------------------------------------------------------
    # setup / introspection
    
    def test_new_schema_has_no_validators_by_default(self):
        assert_equals({}, SchemaValidator().fieldvalidators())

    def test_process_smoke(self):
        self.init_validator(SchemaValidator())
        self.assert_is_valid(None, expected={})
        self.assert_is_valid({}, expected={})

    def test_can_add_validators(self):
        schema = SchemaValidator()
        id_validator = IntegerValidator()
        schema.add('id', id_validator)
        assert_equals({'id': id_validator}, schema.fieldvalidators())
    # protect against duplicate add
    
    def test_can_retrieve_validator_for_field(self):
        schema = self._schema(('id', 'key'))
        assert_isinstance(schema.validator_for('id'), IntegerValidator)
        assert_isinstance(schema.validator_for('key'), StringValidator)

    def test_can_specify_allow_additional_params_at_construction(self):
        schema = SchemaValidator(allow_additional_parameters=False)
        assert_false(schema.allow_additional_parameters)

    # -------------------------------------------------------------------------
    # processing / validation
    
    def test_returns_error_for_non_dict_inputs(self):
        self.init_validator(SchemaValidator())
        self.assert_error('foo')
        self.assert_error_with_key('invalid_type', [])

    def test_can_process_single_value(self):
        self.init_validator()
        self.assert_is_valid({'id': '42'}, expected={'id': 42})

    def test_can_process_multiple_values(self):
        schema = self._schema()
        schema.add('amount', IntegerValidator())

        _input = {'id': '42', 'amount': '21'}
        _expected = {'id': 42, 'amount': 21}
        self.assert_is_valid(_input, expected=_expected, _validator=schema)

    def test_can_retrieve_information_about_error(self):
        self.init_validator()
        exc = self.assert_error_with_key('invalid_number', {'id': 'invalid'}, _return_error=True)
        error = exc.details()
        assert_equals('invalid', error.value())
        assert_equals('Please enter a number.', error.msg())
    
    def test_use_empty_value_from_validator_for_missing_fields(self):
        schema = SchemaValidator()
        schema.add('id', IntegerValidator(required=False))
        self.assert_is_valid({}, expected={'id': None}, _validator=schema)
    
    def test_missing_fields_are_validated_as_well(self):
        self.init_validator()
        result = self.assert_error({})
        errors = result.error_dict()
        assert_equals({'id'}, set(errors))
        id_error, = errors.values()
        assert_equals('empty', id_error.details().key())

    def test_converted_dict_contains_only_validated_fields(self):
        self.init_validator()
        self.assert_is_valid({'id': '42', 'foo': 'bar'}, expected={'id': 42})

    def test_can_get_all_errors_at_once(self):
        self.init_validator(self._schema(('id', 'key'), exception_if_invalid=False))
        result = self.assert_error({'id': 'invalid', 'key': None})
        assert_length(2, result.errors)

    def test_exception_contains_information_about_all_errrors(self):
        schema = self._schema(('id', 'key'), exception_if_invalid=True)
        with assert_raises(InvalidDataError) as c:
            schema.process({'id': 'invalid', 'key': {}})
        exception = c.caught_exception
        assert_equals(set(['id', 'key']), set(exception.error_dict().keys()))
        id_error = exception.error_for('id').details()
        assert_equals('invalid', id_error.value())
        assert_equals('invalid_number', id_error.key())

        key_error = exception.error_for('key').details()
        assert_equals({}, key_error.value())
        assert_equals('invalid_type', key_error.key())

    # -------------------------------------------------------------------------
    # results instead of raising exceptions

    def test_can_return_results_for_valid_inputs(self):
        schema = self._schema(('id', 'key'), exception_if_invalid=False)
        input_ = {'id': '1', 'key': 'foo'}
        result = schema.process(input_)
        assert_equals(input_, result.initial_value)
        assert_equals({'id': 1, 'key': 'foo'}, result.value)
        assert_false(result.contains_error())
        assert_falseish(result.errors.get('id'))
        assert_falseish(result.errors.get('key'))

    def test_can_return_errors_from_results(self):
        schema = SchemaValidator(exception_if_invalid=False)
        schema.add('first', IntegerValidator(min=10, exception_if_invalid=False))
        schema.add('second', IntegerValidator(max=10, exception_if_invalid=False))

        input_ = {'first': '5', 'second': '20'}
        result = schema.process(input_)

        assert_true(result.contains_error())
        first_errors = result.errors['first']
        assert_length(1, first_errors)
        assert_equals('too_low', first_errors[0].key)
        second_errors = result.errors['second']
        assert_length(1, second_errors)
        assert_equals('too_big', second_errors[0].key)

    def test_can_gather_empty_errors_correctly(self):
        schema = SchemaValidator(exception_if_invalid=False)
        schema.add('first', IntegerValidator(required=True, exception_if_invalid=False))
        schema.add('second', IntegerValidator(required=False, exception_if_invalid=False))

        input_ = OrderedDict((('first', ''), ('second', '')))
        result = schema.process(input_)

        assert_true(result.contains_error())
        first = result.children['first']
        assert_true(first.contains_error(),
            message='"first" is required and got an empty string as input')
        assert_equals(('empty',), error_keys(first.errors))
        second = result.children['second']
        assert_false(second.contains_error())

    def test_can_gather_return_values_and_exceptions(self):
        schema = SchemaValidator(exception_if_invalid=False)
        schema.add('first', IntegerValidator(min=10, exception_if_invalid=True))
        schema.add('second', IntegerValidator(max=10, exception_if_invalid=False))

        input_ = {'first': '5', 'second': '20'}
        result = schema.process(input_)

        assert_true(result.contains_error())
        assert_is_not_empty(result.errors)
        first_errors = result.errors['first']
        assert_length(1, first_errors)
        assert_equals('too_low', first_errors[0].key)
        assert_true(first_errors[0].is_critical)
        second_errors = result.errors['second']
        assert_length(1, second_errors)
        assert_equals('too_big', second_errors[0].key)
        assert_false(second_errors[0].is_critical)

    def test_can_handle_non_input(self):
        schema = SchemaValidator(exception_if_invalid=False)
        schema.add('first', IntegerValidator(min=10, exception_if_invalid=True))

        result = schema.process(None)
        assert_true(result.contains_error())
        assert_equals({'first': None}, result.value)
        assert_equals({'first': None}, result.initial_value)
        assert_equals(('empty',), error_keys(result.errors['first']))

    def test_can_return_error_for_invalid_input_types(self):
        schema = SchemaValidator(exception_if_invalid=False)
        schema.add('first', IntegerValidator(min=10, exception_if_invalid=True))

        result = schema.process([])
        assert_true(result.contains_error())
        assert_length(0, result.errors.get('first', ()))
        assert_length(1, result.global_errors)
        error = result.global_errors[0]
        assert_equals('invalid_type', error.key)
        assert_true(error.is_critical)

    def test_can_return_result_for_valid_subschemas(self):
        subschema = self._schema(fields=('id',), exception_if_invalid=False)
        schema = self._schema(fields=('id',), exception_if_invalid=False)
        schema.add('foo', subschema)

        result = schema.process({'id': '10', 'foo': {'id': '20'}})
        assert_false(result.contains_error())

    def test_can_return_error_results_from_subschemas(self):
        subschema = self._schema(fields=('id',), exception_if_invalid=False)
        schema = self._schema(fields=('id',), exception_if_invalid=False)
        schema.add('foo', subschema)

        result = schema.process({'id': '10', 'foo': {'id': 'invalid'}})
        assert_true(result.contains_error())
        id_result = result.children['id']
        assert_false(id_result.contains_error())
        foo_container = result.children['foo']
        assert_true(foo_container.contains_error())

        foo_id = foo_container.children['id']
        assert_true(foo_id.contains_error())
        assert_length(1, foo_id.errors)
        error = foo_id.errors[0]
        assert_equals('invalid_number', error.key)

    def test_can_return_errors_from_list_children(self):
        schema = SchemaValidator(exception_if_invalid=False)
        foo_list = ForEach(IntegerValidator())
        schema.add('foo', foo_list)

        result = schema.process({'foo': ['abc']})
        assert_true(result.contains_error())
        assert_equals(('foo',), tuple(result.errors))
        foo_errors = result.errors['foo']

        assert_length(1, foo_errors)
        int_errors = foo_errors[0]
        assert_length(1, int_errors)
        int_error = int_errors[0]
        assert_isinstance(int_error, Error)
        assert_equals('invalid_number', int_error.key)

    def test_can_return_errors_from_raising_list_children(self):
        schema = SchemaValidator(exception_if_invalid=False)
        # exception_if_invalid=True is important here to trigger the bug in
        # error conversion...
        foo_list = ForEach(IntegerValidator(), exception_if_invalid=True)
        schema.add('foo', foo_list)

        # Test case: multiple items for the list child but only one contains an
        # error
        result = schema.process({'foo': ['bar', '1']})
        assert_true(result.contains_error())
        assert_equals(('foo',), tuple(result.errors))
        foo_errors = result.errors['foo']
        assert_length(2, foo_errors)

        assert_length(1, foo_errors[0])
        assert_none(foo_errors[1])

    def test_can_return_result_for_valid_schema_with_foreach_and_formvalidator(self):
        schema = SchemaValidator()
        schema.add('foo', ForEach(IntegerValidator()))
        schema.add_formvalidator(Validator(exception_if_invalid=False))

        with assert_not_raises():
            schema.process({'foo': [10]})

    # -------------------------------------------------------------------------
    # warn about additional parameters
    
    def test_schema_can_bail_out_if_additional_items_are_detected(self):
        schema = self._schema(fields=())
        self.init_validator(schema)
        self.assert_is_valid({'foo': 42}, expected={})
        schema.set_internal_state_freeze(False)
        schema.set_allow_additional_parameters(False)
        self.assert_error({'foo': 42})

    def test_can_return_error_if_additional_items_present(self):
        schema = self._schema(
            fields=(),
            exception_if_invalid=False,
            allow_additional_parameters=False,
        )
        result = schema.process(dict(foo=42))

        assert_true(result.contains_error())
        assert_length(0, result.global_errors)
        assert_contains('foo', result.children)
        foo_errors = result.children['foo'].errors
        assert_length(1, foo_errors)
        assert_equals('additional_item', foo_errors[0].key)
        assert_false(foo_errors[0].is_critical)

    def test_exception_contains_information_about_invalid_and_extra_fields(self):
        self.init_validator(self._schema(allow_additional_parameters=False))
        exc = self.assert_error({'id': 'invalid', 'foo':'heh'})
        assert_length(2, exc.error_dict())

    # -------------------------------------------------------------------------
    # pass unvalidated parameters
    
    def test_filters_unvalidated_parameters_by_default(self):
        schema = self._schema(filter_unvalidated_parameters=True)
        self.init_validator(schema)
        self.assert_is_valid({'id': '42', 'foo': 'bar'}, expected={'id': 42})

    def test_passes_unvalidated_parameters_if_specified(self):
        schema = self._schema(filter_unvalidated_parameters=False)
        self.init_validator(schema)

        _input = {'id': '42', 'foo': 'bar'}
        _expected = {'id': 42, 'foo': 'bar'}
        self.assert_is_valid(_input, expected=_expected)

    def test_prevents_schema_instantiation_with_exception_for_additional_items_and_passing_unvalidated(self):
        with assert_raises(InvalidArgumentsError):
            self._schema(allow_additional_parameters=False, filter_unvalidated_parameters=False)

    # -------------------------------------------------------------------------
    # form validators
    
    def test_can_add_form_validators(self):
        self._schema().add_formvalidator(Validator(exception_if_invalid=False))
    
    def test_can_retrieve_form_validators(self):
        formvalidator = Validator(exception_if_invalid=False)
        schema = self._schema()
        schema.add_formvalidator(formvalidator)
        assert_length(1, schema.formvalidators())
        assert_equals(formvalidator, schema.formvalidators()[0])

    def test_formvalidators_are_executed(self):
        schema = self._schema(formvalidators=(failing_validator(), ))
        with assert_raises(InvalidDataError):
            schema.process({'id': '42'})

    def test_formvalidators_can_return_global_errors(self):
        schema = self._schema(
            formvalidators=(failing_validator(exception_if_invalid=False), ),
            exception_if_invalid=False
        )
        result = schema.process({'id': '42'})
        assert_true(result.contains_error())
        assert_false(result.children['id'].contains_error())
        assert_length(1, result.global_errors)
        assert_equals('key', result.global_errors[0].key)

    def test_formvalidators_can_add_errors_for_specific_fields(self):
        schema = self._schema(
            fields=('id', 'key'),
            formvalidators=(
                failing_validator(fields=('id', 'key'), exception_if_invalid=False),
            ),
            exception_if_invalid=False
        )
        result = schema.process({'id': '42', 'key': 'foo'})
        assert_true(result.contains_error())
        assert_length(0, result.global_errors)

        assert_true(result.children['id'].contains_error())
        assert_length(1, result.children['id'].errors)
        assert_equals('key', result.children['id'].errors[0].key)
        assert_true(result.children['key'].contains_error())
        assert_length(1, result.children['key'].errors)
        assert_equals('key', result.children['key'].errors[0].key)

    def test_formvalidators_can_modify_fields(self):
        class FormValidator(Validator):
            exception_if_invalid = False
            def convert(self, fields, context):
                return {'id': True, }
        schema = self._schema(formvalidators=(FormValidator(),))
        self.assert_is_valid({'id': '42'}, expected={'id': True}, _validator=schema)

    def test_formvalidators_are_not_executed_if_field_validator_failed(self):
        schema = self._schema(formvalidators=(exploding_validator(), ))
        self.init_validator(schema)
        result = self.assert_error_with_key('invalid_number', {'id': 'invalid'})
        errors = result.error_dict()
        assert_equals({'id'}, set(errors))

    def test_formvalidators_with_result_values_are_not_executed_if_field_validator_failed(self):
        schema = self._schema(
            formvalidators=(exploding_validator(), ),
            exception_if_invalid=False
        )
        result = schema.process({'id': 'invalid'})
        assert_true(result.contains_error())
        assert_length(1, result.children['id'].errors)
        id_error = result.children['id'].errors[0]
        assert_equals('invalid_number', id_error.key)
        assert_length(0, result.global_errors)

    def test_formvalidators_are_executed_after_field_validators(self):
        def mock_process(fields, context=None):
            assert fields == {'id': 42}
            return fields
        formvalidator = AttrDict(process=mock_process)
        schema = self._schema(formvalidators=(formvalidator, ))
        with assert_not_raises():
            schema.process({'id': '42'})

    def test_can_have_multiple_formvalidators(self):
        schema = self._schema()
        def first_mock_process(fields, context):
            assert context['state'] == 0
            context['state'] = 1
            return fields
        first_validator = AttrDict(process=first_mock_process)
        schema.add_formvalidator(first_validator)
        
        def second_mock_process(fields, context=None):
            assert context['state'] == 1
            context['state'] = 2
            return fields
        second_validator = AttrDict(process=second_mock_process)
        schema.add_formvalidator(second_validator)
        
        context = {'state': 0}
        schema.process({'id': '42'}, context)
        assert_equals(2, context['state'])

    def test_execute_no_formvalidators_after_one_failed(self):
        schema = self._schema()
        def mock_process(fields, context=None):
            raise InvalidDataError('a message', fields, key='expected', context=context)
        first_validator = AttrDict(process=mock_process)
        schema.add_formvalidator(first_validator)
        schema.add_formvalidator(failing_validator())
        schema.add_formvalidator(exploding_validator())

        error = assert_raises(InvalidDataError, lambda: schema.process({'id': '42'}))
        assert_equals('expected', error.details().key())

    def test_execute_no_formvalidators_after_one_returned_error_result(self):
        schema = self._schema(
            fields=('id', 'key'),
            formvalidators=(
                failing_validator(fields=('id', 'key'), exception_if_invalid=False),
                exploding_validator(),
            ),
            exception_if_invalid=False
        )
        result = schema.process({'id': '42', 'key': 'foo'})
        assert_true(result.contains_error())
        assert_length(0, result.global_errors)

        assert_true(result.children['id'].contains_error())
        assert_length(1, result.children['id'].errors)
        assert_equals('key', result.children['id'].errors[0].key)
        assert_true(result.children['key'].contains_error())
        assert_length(1, result.children['key'].errors)
        assert_equals('key', result.children['key'].errors[0].key)

    def test_can_handle_mismatched_value_for_subschema(self):
        schema = self._schema_with_user_subschema(exception_if_invalid=False)
        result = schema.process({'user': 1})

        assert_true(result.contains_error())
        assert_true(result.user.contains_error())

    # -------------------------------------------------------------------------
    # sub-schemas
    
    def _user_schema(self, **schema_kwargs):
        user_schema = self._schema(fields=(), **schema_kwargs)
        user_schema.add('first_name', StringValidator)
        user_schema.add('last_name', StringValidator)
        return user_schema
    
    def _schema_with_user_subschema(self, **schema_kwargs):
        schema = self._schema(fields=(), **schema_kwargs)
        schema.add('user', self._user_schema(**schema_kwargs))
        return schema
    
    def test_can_declare_schema_with_subschema(self):
        self.init_validator(self._schema_with_user_subschema())
        
        user_input = {'user': {'first_name': 'Foo', 'last_name': 'Bar'}}
        self.assert_is_valid(user_input, expected=user_input)


def test_formvalidator_in_schema_with_repeatable_field_can_set_global_error():
    # Currently the schema will stop validation as soon as one form validator
    # returns an error. Therefore we do not have to check that if
    # ".set(errors=...)" resets errors set previously.
    schema = SchemaValidator(exception_if_invalid=False)
    # having a ForEach validator was important to trigger the regression
    schema.add('numbers', ForEach(IntegerValidator()))

    # Form validator which sets a "global" error
    class NumbersValidator(Validator):
        def validate(self, converted_value, context):
            error = Error('bad_number', 'Service not available', 'foo', context, is_critical=False)
            context['result'].add_errors((error,))
    schema.add_formvalidator(NumbersValidator(exception_if_invalid=False))

    result = schema.process({'numbers': ['1', '2']})

    assert result.contains_error() is True
    assert not result.children['numbers'].contains_error()
    assert not result.errors
    form_error, = result.global_errors
    assert form_error.key == 'bad_number'
