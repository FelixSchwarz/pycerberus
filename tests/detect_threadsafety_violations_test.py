# -*- coding: UTF-8 -*-

from pycerberus.api import Validator
from pycerberus.errors import ThreadSafetyError
from pycerberus.test_util import ValidationTest


class DetectThreadSafetyViolationInValidatorTest(ValidationTest):
    class NonThreadSafeValidator(Validator):
        def validate(self, value, context):
            self.fnord = 42
    
    validator_class = NonThreadSafeValidator
    
    def test_can_detect_threadsafety_violations(self):
        self.assert_raises(ThreadSafetyError, self.process, 42)
    
    def test_can_disable_threadsafety_detection(self):
        class ValidatorWrittenByExpert(self.validator_class):
            def __init__(self, *args, **kwargs):
                self._is_internal_state_frozen = False
                self.super()
        self.init_validator(ValidatorWrittenByExpert())
        self.assert_equals(42, self.process(42))


