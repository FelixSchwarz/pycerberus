# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import re

from pycerberus.i18n import _
from pycerberus.validators.string import StringValidator

__all__ = ['DomainNameValidator']


class DomainNameValidator(StringValidator):
    """A validator to check if an domain name is syntactically correct."""
    
    def messages(self):
        return {
            'invalid_domain_character': _('Invalid character "%(invalid_character)s" in domain "%(domain)s".'),
            'leading_dot':       _('Invalid domain: "%(domain)s" must not start with a dot.'),
            'trailing_dot':      _('Invalid domain: "%(domain)s" must not end with a dot.'),
            'double_dot':        _('Invalid domain: "%(domain)s" must not contain consecutive dots.'),
        }
    
    def validate(self, value, context):
        super(DomainNameValidator, self).validate(value, context)
        if value.startswith('.'):
            self.raise_error('leading_dot', value, context, domain=str(value))
        if value.endswith('.'):
            self.raise_error('trailing_dot', value, context, domain=str(value))
        if '..' in value:
            self.raise_error('double_dot', value, context, domain=str(value))
        
        match = re.search(r'([^a-zA-Z0-9\.\-])', value)
        if match is not None:
            self.raise_error('invalid_domain_character', value, context, invalid_character=str(match.group(1)), domain=str(value))



