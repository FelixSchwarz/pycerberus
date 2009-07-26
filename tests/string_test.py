# -*- coding: UTF-8 -*-

from unittest import TestCase

from inputvalidation import InvalidDataError
from inputvalidation.validators import StringValidator


class StringValidatorTest(TestCase):
    def setUp(self):
        self.validator = StringValidator()
    
    def validate(self, *args, **kwargs):
        return self.validator.process(*args, **kwargs)
    
    def test_accept_string_and_unicode(self):
        self.assertEqual('foo', self.validate('foo'))
        self.assertEqual(u'bär', self.validate(u'bär'))
    
    def test_validator_rejects_bad_types(self):
        self.assertRaises(InvalidDataError, self.validate, [])
        self.assertRaises(InvalidDataError, self.validate, {})
        self.assertRaises(InvalidDataError, self.validate, object)
        self.assertRaises(InvalidDataError, self.validate, 5)


