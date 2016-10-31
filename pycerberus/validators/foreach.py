# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.

from pycerberus.api import NoValueSet, Validator
from pycerberus.errors import InvalidArgumentsError, InvalidDataError
from pycerberus.i18n import _


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
        self.super.__init__(**kwargs)
    
    def messages(self):
        return {
            'invalid_type': _(u'Validator got unexpected input (expected string, got "%(classname)s").'),
            'too_short': _(u'More than %(min)d items required.'),
            'too_long': _(u'Less than %(max)d items required.'),
        }

    def convert(self, values, context):
        exceptions = []
        if not self._is_iterable(values):
            self.raise_error('invalid_type', values, context, classname=values.__class__.__name__)
        if self._min_length and len(values) < self._min_length:
            self.raise_error('too_short', values, context, min=self._min_length)
        if self._max_length != NoValueSet and len(values) > self._max_length:
            self.raise_error('too_long', values, context, max=self._max_length)
        
        validated = []
        for value in values:
            try:
                validated.append(self._validator.process(value, context))
            except InvalidDataError as e:
                exceptions.append(e)
            else:
                exceptions.append(None)
        if list(filter(None, exceptions)):
            self._raise_exception(exceptions, context)
        return tuple(validated)
    
    def _is_iterable(self, value):
        try:
            iter(value)
        except TypeError:
            return False
        return True
    
    def _init_validator(self, validator):
        if isinstance(validator, type):
            validator = validator()
        return validator    
    
    def _raise_exception(self, exceptions, context):
        first_error = list(filter(None, exceptions))[0].details()
        # can't use self.exception() as all values are already filled
        raise InvalidDataError(first_error.msg(), first_error.value(), first_error.key(), 
                               context, error_list=exceptions)


