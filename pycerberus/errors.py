# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pycerberus.lib import AttrDict


__all__ = [
    'EmptyError',
    'Error',
    'InvalidArgumentsError',
    'InvalidDataError',
    'ThreadSafetyError',
    'ValidationError',
]

class ValidationError(Exception):
    "All exceptions thrown by this library must be derived from this base class"
    
    def __init__(self, msg):
        # Exceptions are old-style classes so we need an explicit call the the
        # super class to be compatible with Python 2.3
        Exception.__init__(self, msg)
        self._msg = msg
    
    def msg(self):
        return self._msg


class InvalidDataError(ValidationError):
    """All exceptions which were caused by data to be validated must be derived 
    from this base class."""
    def __init__(self, msg, value, key=None, context=None, error_dict=None, error_list=()):
        ValidationError.__init__(self, msg)
        self._details = AttrDict(key=lambda: key, msg=lambda: msg, 
                                 value=lambda: value, context=lambda: context)
        self._error_dict = error_dict or {}
        self._error_list = tuple(error_list) if (error_list is not None) else None
        if self._error_dict and self._error_list:
            values = tuple(map(repr, (self._error_dict, self._error_list)))
            raise InvalidArgumentsError('You can only set one of error_dict (%s) and error_list (%s)' % values)
    
    def __repr__(self):
        cls_name = self.__class__.__name__
        e = self.details()
        context = e.context()
        #context = '[...]'
        values = (cls_name, e.msg(), e.value(), e.key(), context)
        return '%s(%r, %r, key=%r, context=%r)' % values
    __str__ = __repr__
    
    def details(self):
        """Return information about the *first* error."""
        return self._details
    
    def error_dict(self):
        "Return all errors as an iterable."
        return self._error_dict
    
    def error_for(self, field_name):
        return self.error_dict()[field_name]
    
    def errors(self):
        "Return a list of all errors."
        if self._error_list:
            return tuple(self._error_list)
        elif self._error_dict:
            return tuple(self._error_dict.values())
        return tuple([self])
    
    def unpack_errors(self):
        if self._error_dict:
            error_dict = {}
            for key, error in self._error_dict.items():
                if error is not None:
                    error_dict[key] = error.unpack_errors()
            return error_dict
        elif self._error_list:
            error_list = []
            for error in self._error_list:
                unpacked = None
                if error is not None:
                    unpacked = error.unpack_errors()
                error_list.append(unpacked)
            return error_list
        return self


class EmptyError(InvalidDataError):
    pass


class InvalidArgumentsError(ValidationError):
    pass


class ThreadSafetyError(ValidationError):
    pass


class Error(object):
    def __init__(self, key, msg, value, context, is_critical=True, **custom_attrs):
        self.key = key
        self.msg = msg
        self.value = value
        self.context = context
        self.is_critical = is_critical
        self._custom_attrs = custom_attrs

    def __getattr__(self, attr_name):
        if ('_custom_attrs' in self.__dict__) and (attr_name in self._custom_attrs):
            return self._custom_attrs[attr_name]
        # __getattr__ is the "line of last defense" (only called for "really
        # custom" attributes) so we can assume that the attribute just does not
        # exist at all.
        klassname = self.__class__.__name__
        raise AttributeError("type object '%s' has no attribute '%s'" % (klassname, attr_name))

    def __setattr__(self, attr_name, value):
        if ('_custom_attrs' in self.__dict__) and (attr_name in self._custom_attrs):
            self._custom_attrs[attr_name] = value
        object.__setattr__(self, attr_name, value)

    @property
    def message(self):
        return self.msg

    def __repr__(self):
        tmpl = 'Error(key=%r, msg=%r, value=%r, context=%r, is_critical=%r%s)'
        custom_attrs = []
        keys = sorted(self._custom_attrs.keys())
        for key in keys:
            value = self._custom_attrs[key]
            custom_attrs.append('%s=%r' % (key, value))
        custom_str = ''.join(map(lambda s: (', ' + s), custom_attrs))
        context = self.context
        #context ='[...]'
        return tmpl % (self.key, self.msg, self.value, context, self.is_critical, custom_str)

