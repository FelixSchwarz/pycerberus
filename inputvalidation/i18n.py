# -*- coding: UTF-8 -*-

import gettext
import sys
import threading

__all__ = ['_']


class NullTranslation(object):
    def noop_translation(self, text):
        return text
    
    def __getattr__(self, name):
        return self.noop_translation


class TranslationProxy(object):
    def __init__(self):
        self._current = threading.local()
    
    def get_locale_from_state(self):
        frame = sys._getframe(2)
        locals_ = frame.f_locals
        if 'state' in locals_:
            locale_name = locals_['state']
            return locale_name
        return None
    
    def activate(self, locale):
        if locale is None:
            self._current.translation = NullTranslation()
            self._current.active_locale = None
        elif getattr(self._current, 'active_locale', None) != locale:
            self._current.translation = gettext.translation("messages", localedir, languages=[locale])
            self._current.active_locale = locale
    
    def __getattr__(self, name):
        if 'gettext' not in name:
            raise AttributeError(name)
        locale_name = self.get_locale_from_state()
        self.activate(locale_name)
        return getattr(self._current.translation, name)

proxy = TranslationProxy()
def _():
    return proxy._


