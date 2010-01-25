# -*- coding: UTF-8 -*-

import gettext
import os
import sys

__all__ = ['_']


class GettextTranslation(object):
    # default localedir?
    
    def __init__(self, domain='messages', **kwargs):
        self._gettext_domain = domain
        self._gettext_args = kwargs
    
    def _domain(self):
        return self._gettext_domain
    
    def _default_localedir(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(this_dir, 'locales')
    
    def _locale(self, state):
        return (state or {}).get('locale', 'en')
    
    def _args(self, state):
        args = self._gettext_args.copy()
        args.setdefault('localedir', self._default_localedir())
        args['languages'] = [self._locale(state)]
        return args
    
    def translation(self, state):
        return gettext.translation(self._domain(), **self._args(state))
    
    def _state_from_stack(self):
        frame = sys._getframe(2)
        locals_ = frame.f_locals
        if 'state' not in locals_:
            return {}
        return locals_['state'] or {}
    
    def __getattr__(self, name):
        if name not in ('gettext', ):
            raise AttributeError(name)
        translation = self.translation(self._state_from_stack())
        return getattr(translation, name)


# If we name that method '_' pygettext will choke on that...
def some_name_which_is_not_reserved_by_gettext(message):
    return message
_ = some_name_which_is_not_reserved_by_gettext

