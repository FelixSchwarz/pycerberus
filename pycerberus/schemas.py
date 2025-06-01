# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import re

from pycerberus.i18n import _
from pycerberus.schema import SchemaValidator

__all__ = ['PositionalArgumentsParsingSchema']


class PositionalArgumentsParsingSchema(SchemaValidator):
    """This schema parses a string containing arguments within a specified order
    and returns a dict where each of these parameters is mapped to a specific 
    key for easy retrieval.
    
    You specify the order of parameters (and the keys) in the class-level 
    attribute ``parameter_order``::
    
        class ConfigListSchema(PositionalArgumentsParsingSchema):
            first_key = StringValidator()
            second_key = IntegerValidator()
            parameter_order = (first_key, second_key)
    
    By default the items are separated by comma though you can override in the
    method ``separator_pattern()``. If there are more items than keys specified,
    this schema will behave like any other schema (depending if you set the
    class-level attribute ``allow_additional_parameters``).
    """
    
    def __init__(self, *args, **kwargs):
        super(PositionalArgumentsParsingSchema, self).__init__(*args, **kwargs)
        self.set_internal_state_freeze(False)
        self.set_allow_additional_parameters(False)
        self.set_parameter_order(getattr(self.__class__, 'parameter_order', ()))
        self.set_internal_state_freeze(True)
    
    def messages(self):
        return {'additional_item': _('Unknown parameter "%(additional_item)s"')}
    
    def separator_pattern(self):
        return r'\s*,\s*'
    
    def split_parameters(self, value, context):
        arguments = []
        if len(value) > 0:
            num_declared_fields = len(self.fieldvalidators())
            arguments = re.split(self.separator_pattern(), value.strip(), maxsplit=num_declared_fields)
        return arguments
    
    def _parameter_names(self):
        return list(self._parameter_order)
    
    def aggregate_values(self, parameter_names, arguments, context):
        """This method can manipulate or aggregate parsed arguments. In this 
        class, it's just a noop but sub classes can override this method to do
        more interesting stuff."""
        return parameter_names, arguments
    
    def _map_arguments_to_named_fields(self, value, context):
        parameter_names = self._parameter_names()
        arguments = self.split_parameters(value, context)
        
        parameter_names, arguments = self.aggregate_values(parameter_names, arguments, context)
        nr_missing_parameters = max(len(parameter_names) - len(arguments), 0)
        arguments.extend([None] * nr_missing_parameters)
        if len(parameter_names) < len(arguments):
            parameter_names.append('_extra')
        return dict(zip(parameter_names, arguments))
    
    def set_parameter_order(self, parameter_names):
        self._parameter_order = parameter_names
    
    def process(self, value, context=None):
        if value is None:
            value = {}
        fields = self._map_arguments_to_named_fields(value, context or {})
        return super(PositionalArgumentsParsingSchema, self).process(fields, context=context)

    def _raise_exception(self, result, context):
        if '_extra' in result.children:
            extra_child = result.children['_extra']
            assert extra_child.contains_errors()
            error = extra_child.errors[0]
            value = error.value
            new_error = self._error(error.key,
                value, context, dict(additional_item=value),
                is_critical=False,
            )
            extra_child.set(errors=(new_error,))
        super(PositionalArgumentsParsingSchema, self)._raise_exception(result, context)

