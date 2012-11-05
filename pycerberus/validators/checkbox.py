# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pycerberus.errors import InvalidDataError
from pycerberus.i18n import _
from pycerberus.validators.string import StringValidator


__all__ = ['AgreeToConditionsCheckbox', 'BooleanCheckbox']


class BooleanCheckbox(StringValidator):
    
    trueish = ('true', 't', 'on', '1')
    falsish = ('false', 'f', 'off', '0', '')
    
    def __init__(self, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('strip', True)
        self.super.__init__(**kwargs)
    
    def messages(self):
        return {
            'unknown_bool': _(u'Value should be "%s" or "%s".') % (self.trueish[0], self.falsish[0])
        }
    
    def convert(self, value, context):
        if isinstance(value, bool):
            return value
        
        string_value = self.super().lower()
        if string_value in self.trueish:
            return True
        elif string_value in self.falsish:
            return False
        self.raise_error('unknown_bool', value, context)
    
    def empty_value(self, context):
        return False
    
    def revert_conversion(self, value, context=None):
        "Returns True for all trueish values, otherwise False."
        try:
            return self.convert(value, context or dict())
        except InvalidDataError:
            return False


class AgreeToConditionsCheckbox(BooleanCheckbox):
    def __init__(self, **kwargs):
        kwargs['required'] = True
        self.super.__init__(**kwargs)
    
    def messages(self):
        return {
            'must_agree': _(u'Please accept our Terms and Conditions.')
        }
    
    def convert(self, value, context):
        if value is None:
            return False
        return self.super(value, context)
    
    def validate(self, value, context):
        self.super()
        if value == True:
            return
        self.raise_error('must_agree', value, context)
    
    def is_empty(self, value, context):
        return False

