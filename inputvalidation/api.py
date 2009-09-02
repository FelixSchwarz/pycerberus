# -*- coding: UTF-8 -*-

# Goals:
#  - Independend from the context (useful for web applications as well as servers)
#  - Simple API, no magic behind the scenes
#  - as few dependencies as possible
#  - 
#  - great docs
#  - no global state/variables
#  - Validator objects are stateless
#  - you can programmatically see from the exception which error was thrown. 


from inputvalidation.errors import *

__all__ = ['BaseValidator', 'Validator']

class NoValueSet(object):
    pass


class BaseValidator(object):
    """The BaseValidator implements only the minimally required methods. Most
    users probably want to use the Validator class which already implements some
    commonly used features."""
    
    messages = {}
    
    def error(self, key, value, state):
        msg = self.messages[key]
        raise InvalidDataError(msg, value, key, state)
    
    def process(self, value, state=None):
        return value
    
    def as_string(self, value, state=None):
        "Return the value as string"
        return str(value)


class Validator(BaseValidator):
    def __init__(self, default=NoValueSet, required=NoValueSet, *args, **kwargs):
        """The Validator is the base class of most validators and implements 
        some commonly used features like required values (raise exception if no
        value was provided) or default values in case no value is given.
        
        In this validator, validation and conversion are packed together because
        experience showed that both operations are often very tightly coupled
        in order not to duplicate code (validation already performs a conversion,
        conversion on unvalidated values is unsafe or there are different types
        of valid input so both validation and conversion need to know about the
        algorithm). And last but not least, using real Python types (e.g. int(5)
        instead of '5') is much more convenient...
        
        When a value is processed, the validator will first call convert() which
        performce some checks on the value and eventually returns the converted
        value. After that the validate() function can do additional checks on
        the converted value and possibly raise an Exception on errors.
        
        By default, a validator will raise an InvalidDataError if no value was
        given (unless you set a default value). If required is False, the 
        default is None.
        
        In order to prevent programmer errors, an exception will be raised if 
        you set required to True but provide a default value as well.
        
        All exceptions thrown by validators must be derived from ValidationError.
        Exceptions caused by invalid user input should use InvalidDataError or
        one of the subclasses."""
        super(Validator, self).__init__(*args, **kwargs)
        self._default = default
        self._required = required
        self._check_argument_consistency()
    
    def _check_argument_consistency(self):
        if self.is_required(set_explicitely=True) and self._has_default_value_set():
            msg = 'Set default value (%s) has no effect because a value is required.' % repr(self._default)
            raise InvalidArgumentsError(msg)
    
    def _has_default_value_set(self):
        return (self._default is not NoValueSet)
    
    def is_empty(self, value, state):
        """Decide if the value is considered an empty value."""
        return (value == None)
    
    def is_required(self, set_explicitely=False):
        if self._required == True:
            return True
        elif (not set_explicitely) and (self._required == NoValueSet):
            return True
        return False
    
    def empty_value(self, state):
        """Return the 'empty' value for this validator."""
        if self._default is NoValueSet:
            return None
        return self._default
    
    def convert(self, value, state):
        """Convert the input value to a suitable Python instance which is 
        returned. If the input is invalid, raise an InvalidDataError."""
        return value
   
    def validate(self, converted_value, state):
        """Perform additional checks on the value which was processed 
        previously. Raise an InvalidDataError if the input data is invalid.
        
        This method must not modify the converted_value."""
        pass
    
    def translate_message(text, state):
        return text
    
    def message(self, key, state):
        return translate_message('Value must not be empty.', state)
    
    def error(self, key, value, state):
        raise EmptyError(self.message(key, state), value, key=key, state=state)
    
    def process(self, value, state=None):
        """Apply the validator on value and return the validated value. Raise 
        an InvalidDataError if the input is malformed.
        You can provide a dictionary to make the validator aware of some 
        external state (e.g. current user). This state object is passed to all
        other methods which can be implemented by subclasses. If you don't 
        provide any state, an emtpy dict will be used instead.
        
        Use this method to sanitize input data
        """
        if state is None:
            state = {}
        value = super(Validator, self).process(value, state)
        if self.is_empty(value, state) == True:
            if self.is_required() == True:
                self.error('empty', value, state)
            return self.empty_value(state)
        converted_value = self.convert(value, state)
        self.validate(converted_value, state)
        return converted_value


class Schema(Validator):
    remove_extra_values = True
    
    def validator_for_field(self):
        pass
    
    def fieldnames(self):
        pass
    
    def add_validator(self, fieldname, validator):
        pass


