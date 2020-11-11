# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import re

import six

from ..i18n import _
from .string import StringValidator


__all__ = ['RegexValidator']

class RegexValidator(StringValidator):
    exception_if_invalid = False

    def __init__(self, regex=None, use_match_for_conversion=False, *args, **kwargs):
        if isinstance(regex, six.string_types):
            pattern = regex
            if not pattern.startswith('^'):
                pattern = '^'+pattern
            if not pattern.endswith('$'):
                pattern += '$'
            regex = re.compile(pattern)
        self.regex = regex
        self.use_match_for_conversion = use_match_for_conversion
        super(RegexValidator, self).__init__(*args, **kwargs)

    def messages(self):
        return {
            'bad_pattern': _(u'Input "%(input_)s" does not match the expected pattern.'),
        }

    def convert(self, value, context):
        string_value = super(RegexValidator, self).convert(value, context)
        if self.contains_critical_error(context):
            return string_value
        if not self.use_match_for_conversion:
            return string_value
        return self._assert_regex(string_value, context, is_critical=True)

    def _assert_regex(self, value, context, is_critical=True):
        match = self.regex.match(value)
        if match is None:
            self.new_error('bad_pattern', value,
                context, dict(input_=value),
                is_critical=is_critical
            )
        return match

    def validate(self, value, context):
        super(RegexValidator, self).validate(value, context)
        if self.contains_critical_error(context):
            return
        if not self.use_match_for_conversion:
            self._assert_regex(value, context, is_critical=False)

    def contains_critical_error(self, context):
        return context['result'].contains_critical_error()
