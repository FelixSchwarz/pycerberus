# -*- coding: UTF-8 -*-

__all__ = ['EmptyError', 'InvalidArgumentsError', 'InvalidDataError', 
           'ValidationError']

class ValidationError(Exception):
    "All exceptions thrown by this library must be derived from this base class"
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)
        self.msg = msg
        
    
class InvalidDataError(ValidationError):
    """All exceptions which were caused by data to be valided must be derived 
    from this base class."""
    def __init__(self, msg, value, key=None, state=None):
        super(InvalidDataError, self).__init__(msg)
        self.value = value
        self.key = key
        self.state = state
    
    def __repr__(self):
        cls_name = self.__class__.__name__
        values = (cls_name, repr(self.msg), repr(self.value), repr(self.key), repr(self.state))
        return '%s(%s, %s, key=%s, state=%s)' % values


class EmptyError(InvalidDataError):
    pass


class InvalidArgumentsError(ValidationError):
    pass

