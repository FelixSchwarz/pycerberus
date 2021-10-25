# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pycerberus.api import NoValueSet, Validator
from pycerberus.errors import Error, InvalidArgumentsError, InvalidDataError
from pycerberus.error_conversion import exception_from_errors, exception_to_errors
from pycerberus.i18n import _
from pycerberus.lib.form_data import is_iterable, is_result, FieldData, RepeatingFieldData


__all__ = ['ForEach']

class ForEach(Validator):
    """Apply a validator to every item of an iterable (like map). Also you
    can specify the allowed min/max number of items in that iterable."""
    
    def __init__(self, validator, min_length=0, max_length=NoValueSet, **kwargs):
        self._validator = self._init_validator(validator)
        self._min_length = min_length
        self._max_length = max_length
        if (self._min_length is not None) and (self._max_length is not NoValueSet):
            if self._min_length > self._max_length:
                values = tuple(map(repr, [self._min_length, self._max_length]))
                message = 'min_length must be smaller or equal to max_length (%s > %s)' % values
                raise InvalidArgumentsError(message)
        kwargs.setdefault('default', ())
        if not hasattr(self, 'exception_if_invalid'):
            kwargs.setdefault('exception_if_invalid', False)
        super(ForEach, self).__init__(**kwargs)

    def messages(self):
        return {
            'invalid_type': _(u'Validator got unexpected input (expected string, got "%(classname)s").'),
            'too_short': _(u'More than %(min)d items required.'),
            'too_long': _(u'Less than %(max)d items required.'),
        }

    def convert(self, values, context):
        result = context['result']
        assert isinstance(result, RepeatingFieldData), repr(result)
        if not is_iterable(values):
            classname = values.__class__.__name__
            self.new_error('invalid_type',
                values, context, is_critical=None,
                msg_values={'classname': classname}
            )
            return
        if self._min_length and len(values) < self._min_length:
            self.new_error('too_short', values, context, msg_values={'min': self._min_length})
        if self._max_length != NoValueSet and len(values) > self._max_length:
            self.new_error('too_long', values, context, msg_values={'max': self._max_length})
            values = values[:self._max_length]

        field_results = []
        for i, value in enumerate(values):
            field_result = self._process_field(value, context)
            field_results.append(field_result)
        result.items = field_results
        if self._exception_if_invalid and result.contains_errors():
            raise exception_from_errors(result.errors)
        return result.value

    def _process_field(self, initial_value, context):
        field_result = self._validator.new_result(initial_value)
        list_result = context.pop('result')
        context['result'] = field_result
        try:
            validator_result = self._validator.process(initial_value, context)
        except InvalidDataError as e:
            if not field_result.contains_errors():
                errors = exception_to_errors(e)
                if isinstance(errors, Error):
                    errors = (errors, )
                field_result.update(errors=errors)
            validator_result = field_result
        if not is_result(validator_result):
            # this can only happen for old-style validators (exception on error,
            # so this case must be a successful validation)
            field_result.set(value=validator_result)
        context['result'] = list_result
        return field_result

    # overridden from Validator
    def handle_validator_result(self, converted_value, result, context, errors=None, nr_new_errors=None):
        # not calling super() as our errors are special
        if errors is None:
            errors = result.errors
        if nr_new_errors is not None:
            is_input_valid = (nr_new_errors <= 0)
        else:
            is_input_valid = not result.contains_errors()

        if not self._exception_if_invalid:
            if is_input_valid:
                result.set(value=converted_value)
            return result
        for item_errors in (errors or ()):
            if (item_errors is None) or (len(item_errors) == 0):
                continue
            error = item_errors[0]
            raise InvalidDataError(error.msg, error.value, error.key, context)
        return result.value

    # overridden from Validator
    def new_result(self, initial_value):
        return RepeatingFieldData(child_creator=lambda: FieldData())

    def _init_validator(self, validator):
        if isinstance(validator, type):
            validator = validator()
        return validator

