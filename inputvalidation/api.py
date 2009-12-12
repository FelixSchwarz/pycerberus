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

import inspect

from inputvalidation.errors import *
from inputvalidation.i18n import _

__all__ = ['BaseValidator', 'Validator']

class NoValueSet(object):
    pass


class EarlyBindForMethods(type):
    def __new__(cls, classname, direct_superclasses, class_attributes_dict):
        validator_class = type.__new__(cls, classname, direct_superclasses, class_attributes_dict)
        cls._simulate_early_binding_for_message_methods(validator_class)
        return validator_class
    
    @classmethod
    def _simulate_early_binding_for_message_methods(cls, validator_class):
        # We need to simulate 'early binding' so that we can reference the 
        # messages() method which is defined in the class to be created!
        def keys(self):
            return validator_class.messages(self)
        def message_for_key(self, key, state):
            return validator_class.messages(self)[key]
        validator_class.keys = keys
        validator_class.message_for_key = message_for_key


class BaseValidator(object):
    """The BaseValidator implements only the minimally required methods. Most
    users probably want to use the Validator class which already implements some
    commonly used features."""
    
    __metaclass__ = EarlyBindForMethods
    
    # TODO: final name
    def messages(self):
        return {}
    
    def message_for_key(self, key, state):
        raise NotImplementedError('message_for_key() should have been replaced by a metaclass')
    
    def keys(self):
        raise NotImplementedError('keys() should have been replaced by a metaclass')
    
    def error(self, key, value, state):
        msg = self.messages()[key]
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
        self._implementations, self._implementation_by_class = self._freeze_implementations_for_class()
    
    def _freeze_implementations_for_class(self):
        class_for_key = {}
        implementations_for_class = {}
        known_functions = set()
        for cls in reversed(inspect.getmro(self.__class__)):
            if self._class_defines_custom_keys(cls, known_functions):
                known_functions.add(cls.keys)
                for key in cls.keys(self):
                    class_for_key[key] = self._find_implementations_for_class(cls)
                    implementations_for_class[cls] = class_for_key[key]
        return class_for_key, implementations_for_class
    
    def _find_implementations_for_class(self, cls):
        implementations_by_key = dict()
        for name in ['gettextargs', 'keys', 'message_for_key', 'translate_message']:
            implementations_by_key[name] = getattr(cls, name)
        return implementations_by_key
    
    def _class_defines_custom_keys(self, cls, known_functions):
        # TODO: How to find out which keys are really new if you don't have to
        # define a custom method (pull from messages)?
        # TODO: Check messages attribute as well
        return hasattr(cls, 'keys') and cls.keys not in known_functions
    
    # TODO: final name
    def messages(self):
        return {'empty': _('Value must not be empty.')}
    
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
    
    def error(self, key, value, state, errorclass=InvalidDataError, **values):
        translated_message = self.message(key, state, **values)
        raise errorclass(translated_message, value, key=key, state=state)
    
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
                self.error('empty', value, state, errorclass=EmptyError)
            return self.empty_value(state)
        converted_value = self.convert(value, state)
        self.validate(converted_value, state)
        return converted_value
    
    # - i18n --------------------------------------------------------------
    
    # TODO: Use a more technology-agnostic name
    def gettextargs(self, state):
        return {'domain': 'pyinputvalidator'}
    
    def translate_message(self, native_message, gettextargs, key, state):
        # This method can be overriden on a by-class basis to get translations 
        # to support non-gettext translation mechanisms (e.g. from a db)
        from inputvalidation.i18n import proxy
        return proxy.gettext(native_message)
#        return native_message
    
    # TODO: This method also needs the value to interpolate it into the final
    # message somehow...
    def message(self, key, state, **values):
        # This method can be overriden globally to use a different message 
        # lookup / translation mechanism alltogether
        # TODO: Test
        # improve syntax later
        native_message = self._implementation_for_key(key, 'message_for_key')(key, state)
        gettextargs = self.args_for_gettext(key, state)
        translation_function = self._implementation_for_key(key, 'translate_message')
        # every function should get key as first parameter so I can unify some 
        # things.
        translated_template_message = translation_function(native_message, gettextargs, key, state)
        return translated_template_message % values
#        # if key was defined by me, use translate_message which can be overwritten
#        # otherwise, use default translation
#        if getattr(self, 'messages') and key in self.messages:
#            english_message = self.messages[key]
#        else:
#            english_message = self.messages()__messages__[key]
#        return self.translate_message_with_default_settings(english_message, state)
        
    # TODO: add *args, **kwargs
    # TODO: always add state as last parameter
    def _implementation_for_key(self, key, methodname):
        method = self._implementations[key][methodname]
        return lambda *args, **kwargs: method(self, *args, **kwargs)
    
    def _implementation_for_class(self, cls, methodname):
        method = self._implementations_by_cls[cls][methodname]
        return lambda *args, **kwargs: method(self, *args, **kwargs)
    
    
    # TODO: get rid of that special method
    def args_for_gettext(self, key, state):
        return self._implementation_for_key(key, 'gettextargs')(state)
    
    def locale(self, state):
        """Extract the locale for the given state."""
        return state.get('locale', 'en')
    
    # -------------------------------------------------------------------------


class Schema(Validator):
    remove_extra_values = True
    
    def validator_for_field(self):
        pass
    
    def fieldnames(self):
        pass
    
    def add_validator(self, fieldname, validator):
        pass


