# -*- coding: UTF-8 -*-

from inputvalidation import InvalidDataError
from inputvalidation.test_util import ValidationTest
from inputvalidation.validators import StringValidator



class StringValidatorTest(ValidationTest):
    
    validator_class = StringValidator
    
    def test_accept_string_and_unicode(self):
        self.assert_equals('foo', self.process('foo'))
        self.assert_equals(u'bär', self.process(u'bär'))
    
    def test_validator_rejects_bad_types(self):
        self.assert_raises(InvalidDataError, self.process, [])
        self.assert_raises(InvalidDataError, self.process, {})
        self.assert_raises(InvalidDataError, self.process, object)
        self.assert_raises(InvalidDataError, self.process, 5)


