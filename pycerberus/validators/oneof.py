# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pycerberus.api import Validator
from pycerberus.i18n import _


__all__ = ['OneOf']


class OneOf(Validator):
    exception_if_invalid = True

    def __init__(self, allowed_values, **kwargs):
        self._allowed_values = allowed_values
        super(OneOf, self).__init__(**kwargs)
    
    def messages(self):
        return {
            'value_not_allowed': _(u'This value is not allowed.'),
        }
    
    def validate(self, value, context):
        if value in self._allowed_values:
            return
        self.raise_error('value_not_allowed', value, context)


