# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2010-2011, 2014 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# Modified 2011 Andrew Fleenor at Fastsoft <andrew@fastsoft.com>
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

from pycerberus.api import Validator
from pycerberus.errors import InvalidArgumentsError, InvalidDataError
from pycerberus.lib import AttrDict
from pycerberus.lib.pythonic_testcase import *
from pycerberus.test_util import ValidationTest
from pycerberus.schema import SchemaValidator
from pycerberus.validators import IntegerValidator, StringValidator



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
    
    # -------------------------------------------------------------------------
    # setup / introspection
    
    def test_new_schema_has_no_validators_by_default(self):
        self.assert_equals({}, SchemaValidator().fieldvalidators())
    
    def test_process_smoke(self):
        self.assert_equals({},SchemaValidator().process(None))
        self.assert_equals({}, SchemaValidator().process({}))
    
    def test_can_add_validators(self):
        schema = SchemaValidator()
        id_validator = IntegerValidator()
        schema.add('id', id_validator)
        self.assert_equals({'id': id_validator}, schema.fieldvalidators())
    # protect against duplicate add
    
    def test_can_retrieve_validator_for_field(self):
        schema = self._schema(('id', 'key'))
        assert_isinstance(schema.validator_for('id'), IntegerValidator)
        assert_isinstance(schema.validator_for('key'), StringValidator)

    def test_can_specify_allow_additional_params_at_construction(self):
        schema = SchemaValidator(allow_additional_parameters=False)
        self.assert_equals(False, schema.allow_additional_parameters)
    
    # -------------------------------------------------------------------------
    # processing / validation
    
    def test_non_dict_inputs_raise_invaliddataerror(self):
        assert_raises(InvalidDataError, lambda: SchemaValidator().process('foo'))
        exception = assert_raises(InvalidDataError, lambda: SchemaValidator().process([]))
        self.assert_equals('invalid_type', exception.details().key())
    
    def test_can_process_single_value(self):
        schema = self._schema()
        self.assert_equals({'id': 42}, schema.process({'id': '42'}))
    
    def test_can_process_multiple_values(self):
        schema = self._schema()
        schema.add('amount', IntegerValidator())
        self.assert_equals({'id': 42, 'amount': 21}, 
                           schema.process({'id': '42', 'amount': '21'}))
    
    def test_can_retrieve_information_about_error(self):
        schema = self._schema()
        error = assert_raises(InvalidDataError, lambda: schema.process({'id': 'invalid'})).details()
        self.assert_equals('invalid', error.value())
        self.assert_equals('invalid_number', error.key())
        self.assert_equals('Please enter a number.', error.msg())
    
    def test_use_empty_value_from_validator_for_missing_fields(self):
        schema = SchemaValidator()
        schema.add('id', IntegerValidator(required=False))
        self.assert_equals({'id': None}, schema.process({}))
    
    def test_missing_fields_are_validated_as_well(self):
        schema = self._schema()
        assert_raises(InvalidDataError, lambda: schema.process({}))
    
    def test_converted_dict_contains_only_validated_fields(self):
        schema = self._schema()
        self.assert_equals({'id': 42}, schema.process({'id': '42', 'foo': 'bar'}))
    
    def test_can_get_all_errors_at_once(self):
        schema = self._schema(('id', 'key'))
        exception = assert_raises(InvalidDataError, 
            lambda: schema.process({'id': 'invalid', 'key': None}))
        self.assert_length(2, exception.error_dict())
    
    def test_exception_contains_information_about_all_errrors(self):
        schema = self._schema(('id', 'key'))
        exception = assert_raises(InvalidDataError, 
            lambda: schema.process({'id': 'invalid', 'key': {}}))
        self.assert_equals(set(['id', 'key']), set(exception.error_dict().keys()))
        id_error = exception.error_for('id').details()
        self.assert_equals('invalid', id_error.value())
        self.assert_equals('invalid_number', id_error.key())
        
        key_error = exception.error_for('key').details()
        self.assert_equals({}, key_error.value())
        self.assert_equals('invalid_type', key_error.key())
    
    # -------------------------------------------------------------------------
    # warn about additional parameters
    
    def test_schema_can_bail_out_if_additional_items_are_detected(self):
        schema = self._schema(fields=())
        self.assert_equals({}, schema.process(dict(foo=42)))
        schema.set_internal_state_freeze(False)
        schema.set_allow_additional_parameters(False)
        assert_raises(InvalidDataError, lambda: schema.process(dict(foo=42)))
        
    def test_exception_contains_information_about_invalid_and_extra_fields(self):
        schema = self._schema(allow_additional_parameters=False)

        exception = assert_raises(InvalidDataError, 
            lambda: schema.process({'id': 'invalid', 'foo':'heh'}))
        self.assert_equals(2, len(exception.error_dict().items()))
    
    # -------------------------------------------------------------------------
    # pass unvalidated parameters
    
    def test_filters_unvalidated_parameters_by_default(self):
        schema = self._schema(filter_unvalidated_parameters=True)
        self.init_validator(schema)
        
        assert_equals({'id': 42}, self.process({'id': '42', 'foo': 'bar'}))
    
    def test_passes_unvalidated_parameters_if_specified(self):
        schema = self._schema(filter_unvalidated_parameters=False)
        self.init_validator(schema)

        assert_equals({'id': 42, 'foo': 'bar'}, self.process({'id': '42', 'foo': 'bar'}))
    
    def test_prevents_schema_instantiation_with_exception_for_additional_items_and_passing_unvalidated(self):
        assert_raises(InvalidArgumentsError,
            lambda: self._schema(allow_additional_parameters=False, filter_unvalidated_parameters=False))
    
    # -------------------------------------------------------------------------
    # form validators
    
    def test_can_add_form_validators(self):
        self._schema().add_formvalidator(Validator())
    
    def test_can_retrieve_form_validators(self):
        formvalidator = Validator()
        schema = self._schema()
        schema.add_formvalidator(formvalidator)
        self.assert_length(1, schema.formvalidators())
        self.assert_equals(formvalidator, schema.formvalidators()[0])
    
    def _failing_validator(self):
        def mock_process(fields, context=None):
            raise InvalidDataError('foo', fields, 'key', context)
        return AttrDict(process=mock_process)
    
    def test_formvalidators_are_executed(self):
        schema = self._schema(formvalidators=(self._failing_validator(), ))
        assert_raises(Exception, lambda: schema.process({'id': '42'}))
    
    def test_formvalidators_can_modify_fields(self):
        class FormValidator(Validator):
            def convert(self, fields, context):
                return {'new_field': True, }
        schema = self._schema(formvalidators=(FormValidator(),))
        self.assert_equals({'new_field': True}, schema.process({'id': '42'}))
    
    def test_formvalidators_are_not_executed_if_field_validator_failed(self):
        schema = self._schema(formvalidators=(self._failing_validator(), ))
        error = assert_raises(InvalidDataError, lambda: schema.process({'id': 'invalid'}))
        self.assert_equals(('id',), tuple(error.error_dict().keys()))
    
    def test_formvalidators_are_executed_after_field_validators(self):
        def mock_process(fields, context=None):
            assert fields == {'id': 42}
        formvalidator = AttrDict(process=mock_process)
        schema = self._schema(formvalidators=(formvalidator, ))
        schema.process({'id': '42'})
    
    def test_can_have_multiple_formvalidators(self):
        schema = self._schema()
        def first_mock_process(fields, context):
            assert context['state'] == 0
            context['state'] = 1
        first_validator = AttrDict(process=first_mock_process)
        schema.add_formvalidator(first_validator)
        
        def second_mock_process(fields, context=None):
            assert context['state'] == 1
            context['state'] = 2
        second_validator = AttrDict(process=second_mock_process)
        schema.add_formvalidator(second_validator)
        
        context = {'state': 0}
        schema.process({'id': '42'}, context)
        self.assert_equals(2, context['state'])
    
    def test_execute_no_formvalidators_after_one_failed(self):
        schema = self._schema()
        def mock_process(fields, context=None):
            raise InvalidDataError('a message', fields, key='expected', context=context)
        first_validator = AttrDict(process=mock_process)
        schema.add_formvalidator(first_validator)
        schema.add_formvalidator(self._failing_validator())
        
        error = assert_raises(InvalidDataError, lambda: schema.process({'id': '42'}))
        self.assert_equals('expected', error.details().key())
    
    # -------------------------------------------------------------------------
    # sub-schemas
    
    def _user_schema(self):
        user_schema = self._schema(fields=())
        user_schema.add('first_name', StringValidator)
        user_schema.add('last_name', StringValidator)
        return user_schema
    
    def _schema_with_user_subschema(self):
        schema = self._schema(fields=())    
        schema.add('user', self._user_schema())
        return schema
    
    def test_can_declare_schema_with_subschema(self):
        self.init_validator(self._schema_with_user_subschema())
        
        user_input = {'user': {'first_name': 'Foo', 'last_name': 'Bar'}}
        assert_equals(user_input, self.process(user_input))

