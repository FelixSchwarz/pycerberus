# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2009-2010 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pycerberus.lib import AttrDict, SuperProxy

__all__ = ['EmptyError', 'InvalidArgumentsError', 'InvalidDataError', 
           'ValidationError']



class ValidationError(Exception):
    "All exceptions thrown by this library must be derived from this base class"
    
    super = SuperProxy()
    
    def __init__(self, msg):
        self.super()
        self.msg = msg


class InvalidDataError(ValidationError):
    """All exceptions which were caused by data to be validated must be derived 
    from this base class."""
    def __init__(self, msg, value, key=None, context=None):
        self.super(msg)
        self._error = AttrDict(key=key, msg=msg, value=value, context=context)
    
    def __repr__(self):
        cls_name = self.__class__.__name__
        e = self.error()
        values = (cls_name, repr(e.msg), repr(e.value), repr(e.key), repr(e.context))
        return '%s(%s, %s, key=%s, context=%s)' % values
    
    def error(self):
        """Return information about the first error."""
        return self._error
    
    def errors(self):
        "Return all errors as an iterable."
        return (self.error(),)


class EmptyError(InvalidDataError):
    pass


class InvalidArgumentsError(ValidationError):
    pass

