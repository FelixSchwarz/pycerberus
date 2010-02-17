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

from pycerberus.api import Validator
from pycerberus.i18n import _
from pycerberus.errors import InvalidDataError

__all__ = ['SchemaValidator']


class SchemaValidator(Validator):
    
    def __init__(self, *args, **kwargs):
        self.super()
        self._fields = {}
        self._formvalidators = []
    
    # -------------------------------------------------------------------------
    # additional public API 
    
    def validators_by_field(self):
        return self._fields.copy()
    
    def add(self, fieldname, validator):
        self._fields[fieldname] = validator
    
    def validator_for(self, field_name):
        return self._fields[field_name]
    
    def add_formvalidator(self, formvalidator):
        self._formvalidators.append(formvalidator)
    
    def formvalidators(self):
        return tuple(self._formvalidators)
    
    # -------------------------------------------------------------------------
    # overridden public methods
    
    def messages(self):
        return {
                'invalid_type': _(u'Validator got unexpected input (expected "dict", got "%(classname)s").'),
               }
    
    def convert(self, fields, context):
        if fields is None:
            return self.empty_value(context)
        if not isinstance(fields, dict):
            self.error('invalid_type', fields, context, classname=fields.__class__)
        return self._process_fields(fields, context)
    
    def is_empty(self, value, context):
        # Schemas have a different notion of being "empty"
        return False
    
    def empty_value(self, context):
        return {}
    
    # -------------------------------------------------------------------------
    # private
    
    def _value_for_field(self, field_name, validator, fields, context):
        if field_name in fields:
            return fields[field_name]
        return validator.empty_value(context)
    
    def _process_field(self, key, validator, fields, context, validated_fields, exceptions):
        try:
            original_value = self._value_for_field(key, validator, fields, context)
            converted_value = validator.process(original_value, context)
            validated_fields[key] = converted_value
        except InvalidDataError, e:
            exceptions[key] = e
    
    def _process_field_validators(self, fields, context):
        validated_fields = {}
        exceptions = {}
        for key, validator in self.validators_by_field().items():
            self._process_field(key, validator, fields, context, validated_fields, exceptions)
        if len(exceptions) > 0:
            self._raise_exception(exceptions, context)
        return validated_fields
    
    def _process_form_validators(self, validated_fields, context):
        for formvalidator in self.formvalidators():
            validated_fields = formvalidator.process(validated_fields, context=context)
        return validated_fields
    
    def _process_fields(self, fields, context):
        validated_fields = self._process_field_validators(fields, context)
        return self._process_form_validators(validated_fields, context)
    
    def _raise_exception(self, exceptions, context):
        first_field_with_error = exceptions.keys()[0]
        first_error = exceptions[first_field_with_error].error()
        error = InvalidDataError(first_error.msg, first_error.value, first_error.key, 
                                 context, error_dict=exceptions)
        raise error
    
    # -------------------------------------------------------------------------


