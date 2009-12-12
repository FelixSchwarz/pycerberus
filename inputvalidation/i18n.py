# -*- coding: UTF-8 -*-

import gettext
import os
import sys
import threading

__all__ = ['_']


class NullTranslation(object):
    def noop_translation(self, text):
        return text
    
    def __getattr__(self, name):
        return self.noop_translation


class TranslationProxy(object):
    def __init__(self, localedir=None):
        self._current = threading.local()
        self.localedir = localedir or self.default_localedir()
    
    def default_localedir(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(this_dir, 'locales')
    
    def get_locale_from_state(self):
        frame = sys._getframe(2)
        locals_ = frame.f_locals
        if 'state' in locals_:
            state = locals_['state']
            if state is not None and 'locale' in state:
                return state['locale']
            return 'en'
        return None
    
    def activate(self, locale):
        if locale is None:
            self._current.translation = NullTranslation()
            self._current.active_locale = None
        elif getattr(self._current, 'active_locale', None) != locale:
            self._current.translation = gettext.translation("messages", self.localedir, languages=[locale])
            self._current.active_locale = locale
    
    def __getattr__(self, name):
        if 'gettext' not in name:
            raise AttributeError(name)
        locale_name = self.get_locale_from_state()
        self.activate(locale_name)
        return getattr(self._current.translation, name)

proxy = TranslationProxy()
# If we name that method '_' pygettext will choke on that...
def some_name_which_is_not_reserved_by_gettext(message):
    return proxy.gettext(message)
_ = some_name_which_is_not_reserved_by_gettext

