# -*- coding: UTF-8 -*-

from inputvalidation.api import Validator
from inputvalidation.errors import InvalidDataError
from inputvalidation.i18n import _

__all__ = ['IntegerValidator']


class IntegerValidator(Validator):
    
    messages = {
                'invalid_type': _('Validator got unexpected input (expected string, got %s).'),
                'invalid_number': _('Please enter a number.'),
               }

    def convert(self, value, state=None):
        print 'state in convert', state
        if not isinstance(value, (int, basestring)):
            self.error('invalid_type', value, state)
        try:
            return int(value)
        except ValueError:
            self.error('invalid_number', value, state)


