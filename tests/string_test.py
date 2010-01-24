# -*- coding: UTF-8 -*-

from inputvalidation import InvalidDataError
from inputvalidation.lib import PythonicTestCase
from inputvalidation.validators import StringValidator


class StringValidatorTest(PythonicTestCase):
    def setUp(self):
        self.super()
        self.validator = StringValidator()
    
    def validate(self, *args, **kwargs):
        return self.validator.process(*args, **kwargs)
    
    def test_accept_string_and_unicode(self):
        self.assert_equals('foo', self.validate('foo'))
        self.assert_equals(u'bär', self.validate(u'bär'))
    
    def test_validator_rejects_bad_types(self):
        self.assert_raises(InvalidDataError, self.validate, [])
        self.assert_raises(InvalidDataError, self.validate, {})
        self.assert_raises(InvalidDataError, self.validate, object)
        self.assert_raises(InvalidDataError, self.validate, 5)


