# -*- coding: UTF-8 -*-

from inputvalidation.api import Validator
from inputvalidation.i18n import _


__all__ = ['StringValidator']


class StringValidator(Validator):
    
    def messages(self):
        return {
                'invalid_type': _('Validator got unexpected input (expected string, got %s).'),
               }
    
    def validate(self, value, state=None):
        if not isinstance(value, basestring):
            self.error('invalid_type', value, state)


