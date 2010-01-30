# -*- coding: UTF-8 -*-

from pycerberus.api import Validator
from pycerberus.i18n import _


__all__ = ['StringValidator']


class StringValidator(Validator):
    
    def messages(self):
        return {
                'invalid_type': _(u'Validator got unexpected input (expected string, got "%(classname)s").'),
               }
    
    def convert(self, value, context):
        if not isinstance(value, basestring):
            classname = value.__class__.__name__
            self.error('invalid_type', value, context, classname=classname)
        return value


