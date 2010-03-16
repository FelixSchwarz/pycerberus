# -*- coding: UTF-8 -*-

from pycerberus import InvalidDataError
from pycerberus.test_util import ValidationTest
from pycerberus.validators import StringValidator



class StringValidatorTest(ValidationTest):
    
    validator_class = StringValidator
    
    def test_accept_string_and_unicode(self):
        self.assert_equals('foo', self.process('foo'))
        self.assert_equals(u'bär', self.process(u'bär'))
    
    def test_reject_bad_types(self):
        self.assert_raises(InvalidDataError, self.process, [])
        self.assert_raises(InvalidDataError, self.process, {})
        self.assert_raises(InvalidDataError, self.process, object)
        self.assert_raises(InvalidDataError, self.process, 5)
    
    def test_show_class_name_in_error_message(self):
        e = self.assert_raises(InvalidDataError, self.process, [])
        self.assert_contains(u'(expected string, got "list")', e.details().msg())


