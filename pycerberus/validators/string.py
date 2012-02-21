# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2009-2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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

from pycerberus.api import NoValueSet, Validator
from pycerberus.errors import InvalidArgumentsError
from pycerberus.i18n import _


__all__ = ['StringValidator']


class StringValidator(Validator):
    
    def __init__(self, min_length=NoValueSet, max_length=NoValueSet, **kwargs):
        self._min_length = min_length
        self._max_length = max_length
        self._check_min_max_length_consistency()
        self.super.__init__(**kwargs)
    
    def _check_min_max_length_consistency(self):
        if (self._min_length != NoValueSet) and (self._max_length != NoValueSet):
            if self._min_length > self._max_length:
                values = tuple(map(repr, [self._min_length, self._max_length]))
                message = 'min_length must be smaller or equal to max_length (%s > %s)' % values
                raise InvalidArgumentsError(message)
    
    def messages(self):
        return {
            'invalid_type': _(u'Validator got unexpected input (expected string, got "%(classname)s").'),
            'too_long': _(u'Must be less than %(max)d characters long.'),
            'too_short': _(u'Must be at least %(min)d characters long.'),
        }
    
    def convert(self, value, context):
        if not isinstance(value, basestring):
            classname = value.__class__.__name__
            self.raise_error('invalid_type', value, context, classname=classname)
        return value
    
    def validate(self, value, context):
        if self._min_length != NoValueSet and len(value) < self._min_length:
            self.raise_error('too_short', value, context, min=self._min_length)
        if self._max_length != NoValueSet and len(value) > self._max_length:
            self.raise_error('too_long', value, context, max=self._max_length)
    
    def is_empty(self, value, context):
        return value in (None, '')


