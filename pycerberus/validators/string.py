# -*- coding: UTF-8 -*-

from pycerberus.api import Validator
from pycerberus.i18n import _


__all__ = ['StringValidator']


class StringValidator(Validator):
    
    def messages(self):
        return {
                'invalid_type': _('Validator got unexpected input (expected string, got %s).'),
               }
    
    def validate(self, value, context=None):
        if not isinstance(value, basestring):
            self.error('invalid_type', value, context)


