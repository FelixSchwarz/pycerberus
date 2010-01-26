# -*- coding: UTF-8 -*-

from pycerberus import InvalidDataError
from pycerberus.lib import PythonicTestCase


class ValidationTest(PythonicTestCase):
    
    def setUp(self):
        self.super()
        self._validator = None
        if hasattr(self, 'validator_class'):
            self.init_validator()
    
    def init_validator(self, validator=None, *args, **kwargs):
        if (validator is None) and hasattr(self, 'validator_class'):
            validator = self.validator_class(*args, **kwargs)
        self._validator = validator
        return self._validator
    
    def validator(self):
        """Return a validator instance (initializes a new one if none was 
        created yet."""
        if self._validator is not None:
            return self._validator
        return self.init_validator()
    
    def process(self, *args, **kwargs):
        if len(args) == 1 and 'context' not in kwargs:
            kwargs['context'] = {}
        return self._validator.process(*args, **kwargs)
    
    def get_error(self, value, locale='en', *args, **kwargs):
        """Process the given value and assert that this raises a validation
        exception - return that exception."""
        context = {'locale': locale}
        return self.assert_raises(InvalidDataError, self.process, value, context=context, *args, **kwargs)
    
    def message_for_key(self, key, locale='de'):
        "Return the error message for the given key."
        error = self.assert_raises(InvalidDataError, self.validator().error, key, None, {'locale': locale})
        return error.msg

