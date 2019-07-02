# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.

from __future__ import absolute_import, print_function, unicode_literals

import gettext
import os
import sys

from pkg_resources import resource_filename

__all__ = ['_', 'GettextTranslation']


class GettextTranslation(object):
    
    def __init__(self, domain='messages', **kwargs):
        self._gettext_domain = domain
        self._gettext_args = kwargs
    
    def _domain(self):
        return self._gettext_domain
    
    def _default_localedir(self):
        locale_dir_in_egg = resource_filename(__name__, "/locales")
        if os.path.exists(locale_dir_in_egg):
            return locale_dir_in_egg
        locale_dir_on_filesystem = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locales')
        if os.path.exists(locale_dir_on_filesystem):
            return locale_dir_on_filesystem
        return os.path.normpath('/usr/share/locale')
    
    def _locale(self, context):
        return (context or {}).get('locale', 'en')
    
    def _args(self, context):
        args = self._gettext_args.copy()
        args.setdefault('localedir', self._default_localedir())
        args['languages'] = [self._locale(context)]
        return args
    
    def translation(self, context):
        return gettext.translation(self._domain(), fallback=True, **self._args(context))
    
    def _context_from_stack(self):
        frame = sys._getframe(2)
        locals_ = frame.f_locals
        if 'context' not in locals_:
            return {}
        return locals_['context'] or {}
    
    def __getattr__(self, name):
        if name not in ('gettext', 'ugettext'):
            raise AttributeError(name)
        translation = self.translation(self._context_from_stack())
        if name == 'ugettext' and not hasattr(translation, 'ugettext'):
            # Python3 has no ugettext - everything is unicode by 
            # default…
            name = 'gettext'
        return getattr(translation, name)


# If we name that method '_' pygettext will choke on that...
def some_name_which_is_not_reserved_by_gettext(message):
    return message
_ = some_name_which_is_not_reserved_by_gettext

