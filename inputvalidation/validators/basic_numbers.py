# -*- coding: UTF-8 -*-

from inputvalidation.api import Validator
from inputvalidation.errors import InvalidDataError

__all__ = ['IntegerValidator']


class IntegerValidator(Validator):
    def convert(self, value, state=None):
        if not isinstance(value, (int, basestring)):
            msg = 'Validator got unexpected input (expected string, got %s).' % value.__class__.__name__
            raise InvalidDataError(msg, value, key='invalid_type', state=state)
        try:
            return int(value)
        except ValueError:
            raise InvalidDataError('Please enter a number.', value, key='invalid_number', state=state)


