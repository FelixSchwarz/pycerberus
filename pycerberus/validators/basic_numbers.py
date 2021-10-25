# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import six

from pycerberus.api import Validator
from pycerberus.errors import InvalidArgumentsError
from pycerberus.i18n import _

__all__ = ['IntegerValidator']


class IntegerValidator(Validator):
    
    def __init__(self, min=None, max=None, *args, **kwargs):
        self.min = min
        self.max = max
        if (self.min is not None) and (self.max is not None) and (self.min > self.max):
            message = 'min must be smaller or equal to max (%s > %s)' % (repr(self.min), repr(self.max))
            raise InvalidArgumentsError(message)
        if not hasattr(self, 'exception_if_invalid'):
            kwargs.setdefault('exception_if_invalid', True)
        super(IntegerValidator, self).__init__(*args, **kwargs)

    def messages(self):
        return {
                'invalid_type': _(u'Validator got unexpected input (expected string, got "%(classname)s").'),
                'invalid_number': _(u'Please enter a number.'),
                'too_low': _(u'Number must be %(min)d or greater.'),
                'too_big': _(u'Number must be %(max)d or smaller.'),
               }
    
    def is_empty(self, value, context):
        return (value in (None, ''))
    
    def convert(self, value, context):
        if not isinstance(value, (int, six.string_types)):
            classname = value.__class__.__name__
            self.new_error('invalid_type',
                value, context, dict(classname=classname),
                is_critical=True
            )
            return
        try:
            return int(value)
        except ValueError:
            self.new_error('invalid_number', value, context, is_critical=True)

    def validate(self, value, context):
        if (self.min is not None) and (value < self.min):
            self.new_error('too_low', value, context, dict(min=self.min), is_critical=False)
        if (self.max is not None) and (value > self.max):
            self.new_error('too_big', value, context, dict(max=self.max), is_critical=False)

    def revert_conversion(self, value, context=None):
        if hasattr(value, 'initial_value'):
            return value.initial_value
        if isinstance(value, bool):
            # True/False should not be mapped to 1/0 here because that
            # peculiarity of Python ("0 == False" but "0 is not False") might
            # cause nasty surprises later on.
            # need to check this first because "isinstance(False, int) -> True"
            return value
        elif not isinstance(value, (int, six.string_types)):
            # int() can only work on the types above, so just return the input
            # value for other types
            return value
        try:
            return int(value)
        except ValueError:
            return value


