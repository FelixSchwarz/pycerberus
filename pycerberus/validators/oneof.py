# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2011-2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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

from pycerberus.api import Validator
from pycerberus.i18n import _


__all__ = ['OneOf']


class OneOf(Validator):
    def __init__(self, allowed_values, **kwargs):
        self._allowed_values = allowed_values
        self.super.__init__(**kwargs)
    
    def messages(self):
        return {
            'value_not_allowed': _(u'This value is not allowed.'),
        }
    
    def validate(self, value, context):
        if value in self._allowed_values:
            return
        self.raise_error('value_not_allowed', value, context)


