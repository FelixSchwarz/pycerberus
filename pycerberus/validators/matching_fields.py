# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pycerberus.api import Validator
from pycerberus.i18n import _


__all__ = ['MatchingFields']

class MatchingFields(Validator):
    exception_if_invalid = True

    def __init__(self, first_field, second_field, *args, **kwargs):
        self.first_field = first_field
        self.second_field = second_field
        super(MatchingFields, self).__init__(*args, **kwargs)

    def messages(self):
        return dict(mismatch=_(u'Fields do not match'))
    
    def validate(self, values, context):
        first = values[self.first_field]
        second = values[self.second_field]
        if first != second:
            error = self.exception('mismatch', second, context)
            error_dict = {self.second_field: error}
            self.raise_error('mismatch', values, context, error_dict=error_dict)
