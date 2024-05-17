# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import warnings

import six

from pycerberus.api import BaseValidator, EarlyBindForMethods, Validator
from pycerberus.compat import OrderedDict
from pycerberus.errors import Error, InvalidArgumentsError, InvalidDataError
from pycerberus.error_conversion import exception_from_errors, exception_to_errors
from pycerberus.i18n import _
from pycerberus.lib.form_data import is_result, FieldData, FormData


__all__ = ['SchemaValidator']

class SchemaMeta(EarlyBindForMethods):
    def __new__(cls, classname, direct_superclasses, class_attributes_dict):
        fields = cls.extract_fieldvalidators(class_attributes_dict, direct_superclasses)
        formvalidators = cls.extract_formvalidators(class_attributes_dict, direct_superclasses)
        cls.restore_overwritten_methods(direct_superclasses, class_attributes_dict)
        schema_class = EarlyBindForMethods.__new__(cls, classname, direct_superclasses, class_attributes_dict)
        schema_class._fields = fields
        schema_class._formvalidators = formvalidators
        inherited_allow_additional_parameters = getattr(schema_class, 'allow_additional_parameters', None)
        schema_class.allow_additional_parameters = class_attributes_dict.get('allow_additional_parameters', inherited_allow_additional_parameters)
        inherited_filter_unvalidated_parameters = getattr(schema_class, 'filter_unvalidated_parameters', True)
        schema_class.filter_unvalidated_parameters = class_attributes_dict.get('filter_unvalidated_parameters', inherited_filter_unvalidated_parameters)
        return schema_class

    @classmethod
    def is_validator(cls, value):
        if isinstance(value, BaseValidator):
            return True
        elif isinstance(value, type) and issubclass(value, BaseValidator):
            return True
        return False

    @classmethod
    def _filter_validators(cls, items):
        validators = []
        for item in items:
            validator = item
            if isinstance(item, (tuple, list)):
                validator = item[1]
            if not cls.is_validator(validator):
                continue
            validators.append(item)
        return validators

    @classmethod
    def extract_fieldvalidators(cls, class_attributes_dict, superclasses):
        fields = OrderedDict()
        for superclass in superclasses:
            if not hasattr(superclass, '_fields'):
                continue
            validators = cls._filter_validators(superclass._fields.items())
            fields.update(validators)

        new_validators = cls._filter_validators(class_attributes_dict.items())
        for key, validator in new_validators:
            fields[key] = validator
            del class_attributes_dict[key]
        return fields

    @classmethod
    def extract_formvalidators(cls, class_attributes_dict, superclasses):
        formvalidators = []
        for superclass in superclasses:
            if not hasattr(superclass, '_formvalidators'):
                continue
            formvalidators.extend(cls._filter_validators(superclass._formvalidators))
        
        if 'formvalidators' in class_attributes_dict:
            validators = class_attributes_dict['formvalidators']
            if not callable(validators):
                formvalidators.extend(cls._filter_validators(validators))
        return tuple(formvalidators)

    @classmethod
    def restore_overwritten_methods(cls, direct_superclasses, class_attributes_dict):
        super_class = direct_superclasses[0]
        for name in dir(super_class):
            if name not in class_attributes_dict:
                continue
            old_value = getattr(super_class, name)
            new_value = class_attributes_dict[name]
            if name != 'formvalidators' and not cls.is_validator(new_value):
                continue
            class_attributes_dict[name] = old_value


@six.add_metaclass(SchemaMeta)
class SchemaValidator(Validator):
    def __init__(self, allow_additional_parameters=None, 
            filter_unvalidated_parameters=None, *args, **kwargs):
        self._fields = OrderedDict()
        self._formvalidators = []
        if not hasattr(self, 'exception_if_invalid'):
            kwargs.setdefault('exception_if_invalid', True)

        if allow_additional_parameters is not None:
            self.allow_additional_parameters = allow_additional_parameters
        if getattr(self, 'allow_additional_parameters', None) is None:
            self.allow_additional_parameters = True
        if filter_unvalidated_parameters is not None:
            self.filter_unvalidated_parameters = filter_unvalidated_parameters
        self._check_consistency_additional_and_filtered_parameters()

        super(SchemaValidator, self).__init__(*args, **kwargs)
        self._setup_fieldvalidators()
        self._setup_formvalidators()
    
    def _check_consistency_additional_and_filtered_parameters(self):
        if (not self.allow_additional_parameters) and (not self.filter_unvalidated_parameters):
            message = _(u'if "allow_additional_parameters" is False, "filter_unvalidated_parameters=False" is meaningless')
            raise InvalidArgumentsError(message)
    
    def _init_validator(self, validator):
        if isinstance(validator, type):
            validator = validator()
        return validator
    
    def _setup_fieldvalidators(self):
        for name, validator in self.__class__._fields.items():
            self.add(name, validator)
    
    def _setup_formvalidators(self):
        for formvalidator in self.__class__._formvalidators:
            self.add_formvalidator(formvalidator)
    
    # -------------------------------------------------------------------------
    # additional public API 
    
    def add(self, fieldname, validator):
        self._fields[fieldname] = self._init_validator(validator)
    
    def validator_for(self, field_name):
        return self._fields[field_name]
    
    def add_formvalidator(self, formvalidator):
        self._formvalidators.append(self._init_validator(formvalidator))
    
    def fieldvalidators(self):
        return self._fields.copy()
    
    def formvalidators(self):
        return tuple(self._formvalidators)
    
    def add_missing_validators(self, schema):
        for name, validator in schema.fieldvalidators().items():
            if name in self.fieldvalidators():
                continue
            self.add(name, validator)
        for formvalidator in schema.formvalidators():
            self.add_formvalidator(formvalidator)
    
    # -------------------------------------------------------------------------
    # overridden public methods
    
    def messages(self):
        return {
                'invalid_type': _(u'Validator got unexpected input (expected "dict", got "%(classname)s").'),
                'additional_item': _(u'Undeclared field detected: "%(additional_item)s".'),
               }
    
    def convert(self, fields, context):
        if fields is None:
            # This is helpful to produce the correct "empty" error for each
            # field if this is a subschema.
            fields = {}
        if not isinstance(fields, dict):
            self.new_error('invalid_type',
                fields, context,
                msg_values=dict(classname=fields.__class__.__name__),
                is_critical=True
            )
            return None

        result = context['result']
        self._process_fields(fields, result, context)
        # even though this seems duplicated (all information is also present
        # in "result" we should keep API compatibility
        return result.value

    # overriden from Validator
    def handle_validator_result(self, converted_value, result, context, errors=None, nr_new_errors=None):
        if errors is None:
            # only pass (errors != None) if there are actual errors
            errors = result.global_errors or None
        return super(SchemaValidator, self).handle_validator_result(converted_value, result, context, errors=errors, nr_new_errors=nr_new_errors)

    def new_error(self, key, value, context, msg_values=None, is_critical=True):
        result = context['result']
        error = self._error(key, value, context, msg_values=msg_values, is_critical=is_critical)
        result.global_errors = result.global_errors + (error,)
        return error

    def is_empty(self, value, context):
        # Schemas have a different notion of being "empty"
        return False
    
    def empty_value(self, context):
        return {}

    # overriden from Validator
    def new_result(self, initial_value):
        result = self._add_result_containers_for_fields(self, initial_value)
        if isinstance(initial_value, dict):
            result.set(initial_value=initial_value)
        return result

    def _add_result_containers_for_fields(self, schema, initial_values):
        result = FormData()
        for field_name, field_validator in schema._fields.items():
            subresult = field_validator.new_result(initial_values)
            result.children[field_name] = subresult
        return result

    # -------------------------------------------------------------------------
    # private
    
    def _value_for_field(self, field_name, validator, fields, context):
        if field_name in fields:
            return fields[field_name]
        return validator.empty_value(context)

    def _process_field(self, key, validator, fields, context, schema_result):
        original_value = self._value_for_field(key, validator, fields, context)
        field_result = schema_result.children[key]
        field_result.set(initial_value=original_value)
        form_result = context.pop('result')
        context['result'] = field_result
        try:
            validator_result = validator.process(original_value, context)
        except InvalidDataError as e:
            errors = exception_to_errors(e)
            if isinstance(errors, Error):
                errors = (errors,)
            field_result.set(errors=errors)
            validator_result = field_result
        context['result'] = form_result
        self._handle_field_validation_result(validator_result, field_result)

    def _handle_field_validation_result(self, processed_value, result):
        if not is_result(processed_value):
            # this can only happen for old-style validators (exception on error,
            # so this case must be a successful validation)
            result.set(value=processed_value)
            return
        assert id (processed_value) == id(result)

    def _process_field_validators(self, fields, result, context):
        for key, validator in self.fieldvalidators().items():
            self._process_field(key, validator, fields, context, result)

        additional_items = set(fields).difference(set(self.fieldvalidators()))
        if (not self.allow_additional_parameters) and additional_items:
            for item_key in additional_items:
                default = FieldData(initial_value=fields[item_key])
                field_result = result.children.setdefault(item_key, default)
                error = self._error('additional_item',
                    fields[item_key], context, dict(additional_item=item_key),
                    is_critical=False,
                )
                field_result.set(errors=(error,))
        if not self.filter_unvalidated_parameters:
            for key in additional_items:
                default = FieldData(initial_value=fields[key])
                field_result = result.children.setdefault(key, default)
                field_result.set(value=fields[key])
        if result.contains_errors() and self._exception_if_invalid:
            self._raise_exception(result, context)

    def _process_form_validators(self, result, context):
        if result.contains_errors():
            return
        for formvalidator in self.formvalidators():
            nr_previous_errors = result.error_count
            values = formvalidator.process(result.value, context=context)
            if not is_result(values):
                if values is None:
                    warnings.warn('form validator %r returned None' % formvalidator)
                    continue
                result.set(value=values)
            if result.error_count > nr_previous_errors:
                # do not execute additional form validators if one of them
                # found an error
                # LATER: Once the code does not stop on the first error anymore,
                # we need to adapt the tests to check that setting a global
                # error does not reset other errors.
                break

    def _process_fields(self, fields, result, context):
        self._process_field_validators(fields, result, context)
        self._process_form_validators(result, context)

    def _raise_exception(self, result, context):
        # PositionalParametersParsingSchema overrides this (and needs 'context')
        raise exception_from_errors(result.errors)

    def set_allow_additional_parameters(self, value):
        self.allow_additional_parameters = value
    
    # -------------------------------------------------------------------------


