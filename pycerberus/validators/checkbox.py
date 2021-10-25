# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pycerberus.errors import InvalidDataError
from pycerberus.i18n import _
from pycerberus.lib import FieldData
from pycerberus.validators.string import StringValidator


__all__ = ['AgreeToConditionsCheckbox', 'BooleanCheckbox']


class BooleanCheckbox(StringValidator):
    trueish = ('true', 't', 'on', '1')
    falsish = ('false', 'f', 'off', '0', '')

    _exception_if_invalid = False

    def __init__(self, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('strip', True)
        self.trueish = kwargs.pop('trueish', self.__class__.trueish)
        self.falsish = kwargs.pop('falsish', self.__class__.falsish)
        super(BooleanCheckbox, self).__init__(**kwargs)

    def messages(self):
        return {
            'unknown_bool': _(u'Value should be "%s" or "%s".') % (self.trueish[0], self.falsish[0])
        }
    
    def convert(self, value, context):
        # support arbitrary data types which might be configured explicitely
        if self._contains(value, self.trueish):
            return True
        elif self._contains(value, self.falsish):
            return False

        if isinstance(value, bool):
            return value
        string_value = super(BooleanCheckbox, self).convert(value, context)
        if string_value is None:
            return False
        if string_value.lower() in self.trueish:
            return True
        elif string_value.lower() in self.falsish:
            return False
        self.new_error('unknown_bool', value, context)

    def _contains(self, value, values):
        for v in values:
            if value is v:
                return True
        return False

    def empty_value(self, context):
        return False
    
    def revert_conversion(self, value, context=None):
        "Returns True for all trueish values, otherwise False."
        old_result = None
        if context and ('result' in context):
            old_result = context['result']
        if not context:
            context = {}
        context['result'] = FieldData()

        try:
            _valid_value = self.convert(value, context=context)
        except InvalidDataError:
            _valid_value = False
        _result = context.pop('result')
        if old_result:
            context['result'] = old_result
        return _valid_value if not _result.contains_error() else False


class AgreeToConditionsCheckbox(BooleanCheckbox):
    def __init__(self, **kwargs):
        kwargs['required'] = True
        super(AgreeToConditionsCheckbox, self).__init__(**kwargs)

    def messages(self):
        return {
            'must_agree': _(u'Please accept our Terms and Conditions.')
        }
    
    def convert(self, value, context):
        if value is None:
            return False
        return super(AgreeToConditionsCheckbox, self).convert(value, context)
    
    def validate(self, value, context):
        super(AgreeToConditionsCheckbox, self).validate(value, context)
        if value == True:
            return
        self.new_error('must_agree', value, context)

    def is_empty(self, value, context):
        return False

