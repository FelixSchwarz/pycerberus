#!/usr/bin/env python

# Goals:
#  - Independend from the context (useful for web applications as well as servers)
#  - Simple API, no magic behind the scenes
#  - as few dependencies as possible
#  - 
#  - great docs
#  - no global state/variables
#  - Validator objects are stateless
#  - you can programmatically see from the exception which error was thrown. 

class ValidationError(Exception):
    def __init__(self, msg):
        super(ValidationError, self).__init__(msg)
        self.msg = msg
        
    
class InvalidDataError(ValidationError):
    def __init__(self, msg, value, key=None, state=None):
        super(InvalidDataError, self).__init__(msg)
        self.value = value
        self.key = key
        self.state = state
    
    def __repr__(self):
        cls_name = self.__class__.__name__
        values = (cls_name, repr(msg), repr(value), repr(self.key), repr(self.state))
        return '%s(%s, %s, key=%s, state=%s)' % values

class EmptyError(InvalidDataError):
    pass


class InvalidArgumentsError(ValidationError):
    pass


class BaseValidator(object):
    """The BaseValidator implements only the minimally required methods. Most
    users probably want to use the Validator class which already implements some
    commonly used features."""
    
    def process(self, value, state=None):
        return value
    
    def as_string(self, value, state=None):
        "Return the value as string"
        return str(value)


class NoValueSet(object):
    pass


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
                raise EmptyError('Value must not be empty.', value, key='empty', state=state)
            return self.empty_value(state)
        converted_value = self.convert(value, state)
        self.validate(converted_value, state)
        return converted_value


from unittest import TestCase

class DummyValidator(Validator):
    _empty_value = 'empty'
    
    def __init__(self, default=42, *args, **kwargs):
        super(DummyValidator, self).__init__(default=default, *args, **kwargs)

    def is_empty(self, value, state):
        return value == self._empty_value


class ValidatorTest(TestCase):
    class AttributeHolder(object): pass
    
    def setUp(self):
        self._validator = self.validator()
    
    def validator(self, *args, **kwargs):
        return DummyValidator(*args, **kwargs)
    
    def not_implemented(self, *args, **kwargs):
        raise NotImplementedError()
    
    def test_have_special_value_for_no_value_set(self):
        self.assertEqual(NoValueSet, NoValueSet)
        self.assertNotEqual(True, NoValueSet)
   
    def test_can_detect_empty_values_and_return_special_value_before_validation(self):
        self._validator.convert = self.not_implemented
        self.assertEqual(42, self.validator(required=False).process('empty'))
        self.assertNotEqual(self.not_implemented, self.validator().convert)
    
    def test_validator_provides_empty_dict_if_no_state_was_given(self):
        dummy = self.AttributeHolder()
        dummy.given_state = None
        
        def store_empty(state):
            dummy.given_state = state
            return 21
        validator = self.validator(required=False)
        validator.empty_value = store_empty
        self.assertEqual(21, validator.process('empty'))
        self.assertEqual({}, dummy.given_state)
        self.assertNotEqual(store_empty, self.validator().empty_value)
    
    def test_can_set_default_value_for_empty_values(self):
        self.assertEqual(23, Validator(default=23, required=False).process(None))
    
    def test_raise_exception_if_required_value_is_missing(self):
        self.assertEqual(42,  Validator(required=True).process(42))
        self.assertEqual(None,  Validator(required=False).process(None))
        self.assertRaises(EmptyError, Validator(required=True).process, None)
        self.assertRaises(EmptyError, Validator().process, None)
    
    def test_raise_exception_if_value_is_required_but_default_is_set_to_prevent_errors(self):
        self.assertRaises(InvalidArgumentsError, Validator, required=True, default=12)
        

# Handle i18n:
#   - Basic infrastructure
#   - How to add new messages for your own validators?


