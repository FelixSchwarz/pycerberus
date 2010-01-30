# -*- coding: UTF-8 -*-

from pycerberus.api import Validator
from pycerberus.i18n import _

__all__ = ['IntegerValidator']


class IntegerValidator(Validator):
    
    def messages(self):
        return {
                'invalid_type': _(u'Validator got unexpected input (expected string, got "%(classname)s").'),
                'invalid_number': _(u'Please enter a number.'),
               }
    
    def convert(self, value, context=None):
        if not isinstance(value, (int, basestring)):
            classname = value.__class__.__name__
            self.error('invalid_type', value, context, classname=classname)
        try:
            return int(value)
        except ValueError:
            self.error('invalid_number', value, context)


