# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.

import copy
import inspect
import types
import warnings

import six

from pycerberus.error_conversion import exception_from_errors
from pycerberus.errors import *
from pycerberus.i18n import _, GettextTranslation
from pycerberus.lib import SuperProxy
from pycerberus.lib.form_data import FieldData


__all__ = ['BaseValidator', 'Validator']


class NoValueSet(object):
    pass


class EarlyBindForMethods(type):
    
    super = SuperProxy()
    
    def __new__(cls, classname, direct_superclasses, class_attributes_dict):
        validator_class = type.__new__(cls, classname, direct_superclasses, class_attributes_dict)
        cls._simulate_early_binding_for_message_methods(validator_class)
        return validator_class
    
    def _simulate_early_binding_for_message_methods(cls, validator_class):
        # Need to create a dynamic method if messages are defined in a 
        # class-level dict.
        if not callable(validator_class.messages):
            messages_dict = validator_class.messages.copy()
            def messages(self):
                return messages_dict
            validator_class.messages = messages
        
        # We need to simulate 'early binding' so that we can reference the 
        # messages() method which is defined in the class to be created!
        def keys(self):
            return validator_class.messages(self)
        # make sphinx happy
        keys.__doc__ = validator_class.keys.__doc__
        validator_class.keys = keys
        
        if validator_class.__name__ == 'BaseValidator' or \
            getattr(validator_class.message_for_key, 'autogenerated', False):
            def message_for_key(self, key, context):
                return validator_class.messages(self)[key]
            message_for_key.autogenerated = True
            # make sphinx happy
            message_for_key.__doc__ = validator_class.message_for_key.__doc__
            validator_class.message_for_key = message_for_key
    _simulate_early_binding_for_message_methods = classmethod(_simulate_early_binding_for_message_methods)


@six.add_metaclass(EarlyBindForMethods)
class BaseValidator(object):
    """The BaseValidator implements only the minimally required methods. 
    Therefore it does not put many constraints on you. Most users probably want 
    to use the ``Validator`` class which already implements some commonly used 
    features.
    
    You can pass ``messages`` a dict of messages during instantiation to 
    overwrite messages specified in the validator without the need to create 
    a subclass."""
    
    super = SuperProxy()
    
    def __init__(self, messages=None):
        if not messages:
            return
        
        old_messages = self.messages
        old_message_for_key = self.message_for_key
        def messages_(self):
            all_messages = old_messages()
            all_messages.update(messages)
            return all_messages
        def keys_(self):
            return tuple(messages_(self).keys())
        def message_for_key(self, key, context):
            if key in messages:
                return messages[key]
            return old_message_for_key(key, context)
        self.messages = self._new_instancemethod(messages_)
        self.keys = self._new_instancemethod(keys_)
        self.message_for_key = self._new_instancemethod(message_for_key)
    
    def _new_instancemethod(self, method):
        if six.PY2:
            return types.MethodType(method, self, self.__class__)
        return types.MethodType(method, self)
    
    def messages(self):
        """Return all messages which are defined by this validator as a 
        key/message dictionary. Alternatively you can create a class-level
        dictionary which contains these keys/messages.
        
        You must declare all your messages here so that all keys are known 
        after this method was called.
        
        Calling this method might be costly when you have a lot of messages and 
        returning them is expensive. You can reduce the overhead in some 
        situations by implementing ``message_for_key()``"""
        return {}
    
    def copy(self):
        """Return a copy of this instance."""
        clone = copy.copy(self)
        was_frozen = False
        if hasattr(clone, 'is_internal_state_frozen'):
            was_frozen = clone.is_internal_state_frozen()
            clone.set_internal_state_freeze(False)
        # deepcopy only copies instance-level attribute but we need to copy also
        # class-level attributes to support the declarative syntax properly.
        # I did not want to add more metaclass magic (that's already complicated
        # enough).
        klass = self.__class__
        for name in dir(clone):
            if name in ('__dict__', '__doc__', '__module__', '__slotnames__',
                        '__weakref__', 'super'):
                continue
            elif not hasattr(klass, name):
                # this is an instance-specific attribute/method, already copied
                continue
            clone_value = getattr(clone, name)
            klass_value = getattr(klass, name)
            if id(clone_value) != id(klass_value):
                continue
            if name.startswith('__') and callable(clone_value):
                continue
            elif inspect.isroutine(clone_value):
                continue
            
            if hasattr(clone_value, 'copy'):
                copied_value = clone_value.copy()
            else:
                copied_value = copy.copy(clone_value)
            setattr(clone, name, copied_value)
        if was_frozen:
            clone.set_internal_state_freeze(True)
        return clone
    
    def message_for_key(self, key, context):
        """Return a message for a specific key. Implement this method if you 
        want to avoid calls to messages() which might be costly (otherwise 
        implementing this method is optional)."""
        raise NotImplementedError('message_for_key() should have been replaced by a metaclass')
    
    def keys(self):
        """Return all keys defined by this specific validator class."""
        raise NotImplementedError('keys() should have been replaced by a metaclass')
    
    def raise_error(self, key, value, context, errorclass=InvalidDataError, **values):
        """Raise an InvalidDataError for the given key."""
        msg_template = self.message_for_key(key, context)
        raise errorclass(msg_template % values, value, key=key, context=context)

    def process(self, value, context=None):
        """This is the method to validate your input. The validator returns a
        (Python) representation of the given input ``value``.
        
        In case of errors a ``InvalidDataError`` is thrown."""
        return value
    
    def revert_conversion(self, value, context=None):
        """Undo the conversion of ``process()`` and return a "string-like" 
        representation. This method is especially useful for widget libraries
        like ToscaWigets so they can render Python data types in a human 
        readable way.
        The returned value does not have to be an actual Python string as long
        as it has a meaningful unicode() result. Generally the validator 
        should accept the return value in its '.process()' method."""
        if hasattr(value, 'initial_value'):
            return value.initial_value
        if value is None:
            return None
        return six.text_type(value)


class Validator(BaseValidator):
    """The Validator is the base class of most validators and implements 
    some commonly used features like required values (raise exception if no
    value was provided) or default values in case no value is given.
    
    This validator splits conversion and validation into two separate steps:
    When a value is ``process()``ed, the validator first calls ``convert()`` 
    which performs some checks on the value and eventually returns the converted
    value. Only if the value was converted correctly, the ``validate()`` 
    function can do additional checks on the converted value and possibly raise 
    an Exception in case of errors. If you only want to do additional checks 
    (but no conversion) in your validator, you can implement ``validate()`` and
    simply assume that you get the correct Python type (e.g. int). 
    
    Of course if you can also raise a ``ValidationError`` inside of ``convert()`` -
    often errors can only be detected during the conversion process.
    
    By default, a validator will raise an ``InvalidDataError`` if no value was
    given (unless you set a default value). If ``required`` is False, the 
    default is None. All exceptions thrown by validators must be derived from 
    ``ValidationError``. Exceptions caused by invalid user input should use 
    ``InvalidDataError`` or one of the subclasses.
    
    If ``strip`` is True (default is False) and the input value has a ``strip()``
    method, the input will be stripped before it is tested for empty values and
    passed to the ``convert()``/``validate()`` methods.
    
    In order to prevent programmer errors, an exception will be raised if 
    you set ``required`` to True but provide a default value as well.
    """
    
    def __init__(self, default=NoValueSet, required=NoValueSet,
                 exception_if_invalid=NoValueSet, strip=False, messages=None):
        self.super(messages=messages)
        self._default = default
        self._required = required
        self._exception_if_invalid = getattr(self, 'exception_if_invalid', NoValueSet)
        self._check_argument_consistency(exception_if_invalid)
        if self._exception_if_invalid is NoValueSet:
            value = True if (exception_if_invalid is NoValueSet) else exception_if_invalid
            self._exception_if_invalid = value
        self._strip_input = strip
        self._implementations, self._implementation_by_class = self._freeze_implementations_for_class()
        if self.is_internal_state_frozen() not in (True, False):
            self._is_internal_state_frozen = True
    
    # --------------------------------------------------------------------------
    # initialization

    def _check_argument_consistency(self, exception_if_invalid):
        if self.is_required(set_explicitely=True) and self._has_default_value_set():
            msg = 'Set default value (%s) has no effect because a value is required.' % repr(self._default)
            raise InvalidArgumentsError(msg)

        class_has_static_value = (self._exception_if_invalid is not NoValueSet)
        user_specified_value = (exception_if_invalid is not NoValueSet)
        if class_has_static_value and user_specified_value and (self._exception_if_invalid != exception_if_invalid):
            msg = 'This validator does not accept "exception_if_invalid" as it is set on a class level'
            raise InvalidArgumentsError(msg)

    def _has_default_value_set(self):
        return (self._default is not NoValueSet)
    
    def _freeze_implementations_for_class(self):
        class_for_key = {}
        implementations_for_class = {}
        known_functions = set()
        for cls in reversed(inspect.getmro(self.__class__)):
            if not self._class_defines_custom_keys(cls, known_functions):
                continue
            defined_keys = cls.keys(self)
            if cls == self.__class__:
                cls = self
                defined_keys = self.keys()
            known_functions.add(cls.keys)
            for key in defined_keys:
                class_for_key[key] = self._implementations_by_key(cls)
                implementations_for_class[cls] = class_for_key[key]
        return class_for_key, implementations_for_class
    
    def _implementations_by_key(self, cls):
        implementations_by_key = dict()
        for name in ['translation_parameters', 'keys', 'message_for_key', 'translate_message']:
            implementations_by_key[name] = getattr(cls, name)
        return implementations_by_key
    
    def _class_defines_custom_keys(self, cls, known_functions):
        return hasattr(cls, 'keys') and cls.keys not in known_functions
    
    # --------------------------------------------------------------------------
    # Implementation of BaseValidator API
    
    def messages(self):
        return {'empty': _('Value must not be empty.')}
    
    def exception(self, key, value, context, errorclass=InvalidDataError, 
            error_dict=None, error_list=(), **values):
        translated_message = self.message(key, context, **values)
        return errorclass(translated_message, value, key=key, context=context, 
            error_dict=error_dict, error_list=error_list)
    
    def raise_error(self, key, value, context, errorclass=InvalidDataError, 
            error_dict=None, error_list=(), **values):
        if not self._exception_if_invalid:
            klassname = self.__class__.__name__
            warnings.warn('raise_error() called in validator "%s" which should not use exceptions (exception_if_invalid=False)' % klassname)
        raise self.exception(key, value, context, errorclass=errorclass, 
            error_dict=error_dict, error_list=error_list, **values)
    
    def process(self, value, context=None):
        old_result = (context or {}).get('result', NoValueSet)
        context = self.build_context(value, context)
        if self._strip_input and hasattr(value, 'strip'):
            value = value.strip()
        value = super(Validator, self).process(value, context)

        result = self.get_result(value, context)
        if self.is_empty(value, context) == True:
            return self.handle_empty_input(value, context, old_result)

        context['result'] = result
        convert_errors = result.errors
        converted_value = self.convert(value, context)
        if convert_errors == result.errors:
            self.validate(converted_value, context)
        self._restore_old_result_in_context(context, old_result)
        return self.handle_validator_result(converted_value, result, context)

    def _restore_old_result_in_context(self, context, old_result):
        context.pop('result')
        if old_result is not NoValueSet:
            context['result'] = old_result

    def handle_empty_input(self, value, context, old_result):
        result = context['result']
        result.set(initial_value=value)
        if self.is_required() and not self._exception_if_invalid:
            self.new_error('empty', value, context)
        self._restore_old_result_in_context(context, old_result)
        if self.is_required() == False:
            empty_value = self.empty_value(context)
            if self._exception_if_invalid:
                return empty_value
            result.set(value=empty_value)
        elif self._exception_if_invalid:
            self.raise_error('empty', value, context, errorclass=EmptyError)
        # required new-style validator is handeled at the beginning
        # This reduces the number of "context restores" in this branch
        return result

    def handle_validator_result(self, converted_value, result, context, errors=None):
        if not self._exception_if_invalid:
            if not result.contains_errors():
                result.set(value=converted_value)
            return result

        if (errors is None) and not result.contains_errors():
            return converted_value
        if errors is None:
            errors = result.errors
        if errors:
            raise exception_from_errors(errors)
        else:
            return converted_value

    def get_result(self, initial_value, context):
        result = context.get('result')
        assert (result is not None), 'not "result" in context (should never happen)'
        return result

    def build_context(self, initial_value, context):
        if context is None:
            context = {}
        if 'result' not in context:
            context['result'] = self.new_result(initial_value)
        return context

    def new_result(self, initial_value):
        return FieldData(initial_value=initial_value)

    # --------------------------------------------------------------------------
    # Defining a convenience API
    
    def convert(self, value, context):
        """Convert the input value to a suitable Python instance which is 
        returned. If the input is invalid, raise an ``InvalidDataError``."""
        return value
    
    def validate(self, converted_value, context):
        """Perform additional checks on the value which was processed 
        successfully before (otherwise this method is not called). Raise an 
        InvalidDataError if the input data is invalid.
        
        You can implement only this method in your validator if you just want to
        add additional restrictions without touching the actual conversion.
        
        This method must not modify the ``converted_value``."""
        pass

    def new_error(self, key, value, context, msg_values=None, is_critical=True):
        if self._exception_if_invalid:
            # all exceptions should be treated as critical because it is hard
            # to ensure all checks did pass so just ignore "is_critical"
            self.raise_error(key, value, context, **(msg_values or {}))
        error = self._error(key, value, context, msg_values=msg_values, is_critical=is_critical)
        result = context['result']
        result.add_error(error)
        return error

    # REFACT: rename to default_value()
    def empty_value(self, context):
        """Return the 'empty' value for this validator (usually None)."""
        if self._default is NoValueSet:
            return None
        return self._default
    
    def is_empty(self, value, context):
        """Decide if the value is considered an empty value."""
        return (value is None)
    
    def is_required(self, set_explicitely=False):
        if self._required == True:
            return True
        elif (not set_explicitely) and (self._required == NoValueSet):
            return True
        return False
    
    # -------------------------------------------------------------------------
    # i18n: public API
    
    def translation_parameters(self, context):
        return {'domain': 'pycerberus'}
    
    def translate_message(self, key, native_message, translation_parameters, context):
        # This method can be overridden on a by-class basis to get translations 
        # to support non-gettext translation mechanisms (e.g. from a db)
        return GettextTranslation(**translation_parameters).ugettext(native_message)
    
    def message(self, key, context, **values):
        # This method can be overridden globally to use a different message 
        # lookup / translation mechanism altogether
        native_message = self._implementation(key, 'message_for_key', context)(key)
        translation_parameters = self._implementation(key, 'translation_parameters', context)()
        translation_function = self._implementation(key, 'translate_message', context)
        translated_template = translation_function(key, native_message, translation_parameters)
        return translated_template % values
    
    # -------------------------------------------------------------------------
    # private 
    
    def _implementation(self, key, methodname, context):
        def context_key_wrapper(*args):
            method = self._implementations[key][methodname]
            args = list(args) + [context]
            if self._is_unbound(method):
                return method(self, *args)
            return method(*args)
        return context_key_wrapper
    
    def _is_unbound(self, method):
        if six.PY2:
            return (method.im_self is None)
        return (getattr(method, '__self__',  None) is None)
    
    def is_internal_state_frozen(self):
        is_frozen = getattr(self, '_is_internal_state_frozen', NoValueSet)
        if is_frozen == NoValueSet:
            return None
        return bool(is_frozen)
    
    def set_internal_state_freeze(self, is_frozen):
        self.__dict__['_is_internal_state_frozen'] = is_frozen
    
    def __setattr__(self, name, value):
        "Prevent non-threadsafe use of Validators by unexperienced developers"
        if self.is_internal_state_frozen():
            raise ThreadSafetyError('Do not store state in a validator instance as this violates thread safety.')
        self.__dict__[name] = value

    def _error(self, key, value, context, msg_values=None, is_critical=True):
        msg = self.message(key, context, **(msg_values or {}))
        return Error(key, msg, value, context, is_critical=is_critical)

    # -------------------------------------------------------------------------


