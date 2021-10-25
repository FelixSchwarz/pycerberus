# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import six

from pycerberus.api import NoValueSet, Validator
from pycerberus.errors import InvalidArgumentsError
from pycerberus.i18n import _


__all__ = ['StringValidator']


class StringValidator(Validator):
    
    def __init__(self, min_length=NoValueSet, max_length=NoValueSet, **kwargs):
        self._min_length = min_length
        self._max_length = max_length
        self._check_min_max_length_consistency()
        if not hasattr(self, 'exception_if_invalid'):
            kwargs.setdefault('exception_if_invalid', True)
        super(StringValidator, self).__init__(**kwargs)

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
        if not isinstance(value, six.string_types):
            classname = value.__class__.__name__
            self.new_error('invalid_type',
                value, context, dict(classname=classname),
                is_critical=True
            )
            return None
        return value
    
    def validate(self, value, context):
        if self._min_length != NoValueSet and len(value) < self._min_length:
            self.new_error('too_short',
                value, context, dict(min=self._min_length),
                is_critical=False
            )
        if self._max_length != NoValueSet and len(value) > self._max_length:
            self.new_error('too_long',
                value, context, dict(max=self._max_length),
                is_critical=False
            )

    def is_empty(self, value, context):
        return value in (None, '')


