# -*- coding: UTF-8 -*-

from inputvalidation.api import Validator
from inputvalidation.errors import InvalidDataError

__all__ = ['StringValidator']


class StringValidator(Validator):
    def validate(self, value, state=None):
        if not isinstance(value, basestring):
            msg = 'Validator got unexpected input (expected string, got %s).' % value.__class__.__name__
            raise InvalidDataError(msg, value, key='invalid_type', state=state)


