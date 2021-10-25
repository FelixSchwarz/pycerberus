# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import re

from pycerberus.i18n import _
from pycerberus.validators.domain import DomainNameValidator

__all__ = ['EmailAddressValidator']


class EmailAddressValidator(DomainNameValidator):
    """A validator to check if an email address is syntactically correct.
    
    Please note that there is no clear definition of an 'email address'. Some
    parts are defined in consecutive RFCs, there is a notion of 'string that is 
    accepted by a MTA' and last but not least a fuzzy 'general expectation' what
    an email address should be about.
    
    Therefore this validator is currently extremly simple and does not handle
    internationalized local parts/domains.
    
    For the future I envision some extensions here:
     - support internationalized domain names (possibly also encode to/
       decode from idna) if specified by flag
     - More flexible structure if there must be a second-level domain
    
    Something that should not happen in this validator:
     - Open SMTP connections to check if an account exists
     - specify default domains if missing
    
    These things can be implemented in derived validators
    """
    
    def messages(self):
        return {
            'single_at': _(u"An email address must contain a single '@'."),
            'invalid_email_character': _(u'Invalid character "%(invalid_character)s" in email address "%(emailaddress)s".'),
            'missing_domain': _(u'Missing domain in email address "%(emailaddress)s".'),
        }
    
    def validate(self, emailaddress, context):
        parts = emailaddress.split('@')
        if len(parts) != 2:
            self.raise_error('single_at', emailaddress, context)
        localpart, domain = parts
        super(EmailAddressValidator, self).validate(domain, context)
        self._validate_localpart(localpart, emailaddress, context)
        self._validate_domain(domain, emailaddress, context)

    # --------------------------------------------------------------------------
    # private helpers
    
    def _validate_localpart(self, localpart, emailaddress, context):
        match = re.search(r'([^a-zA-Z0-9\.\_\-\+])', localpart)
        if match is not None:
            values = dict(invalid_character=str(match.group(1)), emailaddress=str(emailaddress))
            self.raise_error('invalid_email_character', localpart, context, **values)

    def _validate_domain(self, domain, emailaddress, context):
        if len(domain) == 0:
            self.raise_error('missing_domain', emailaddress, context, emailaddress=emailaddress)

