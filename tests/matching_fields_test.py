# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.test_util import ValidationTest
from pycerberus.validators import MatchingFields


class MatchingFieldsTest(ValidationTest):
    
    validator_class = MatchingFields
    validator_args = ('foo', 'bar')
    
    def test_accepts_if_both_fields_are_equal(self):
        self.process(dict(foo='', bar=''))
        self.process(dict(foo=None, bar=None))
        self.process(dict(foo='value', bar='value'))
    
    def test_rejects_fields_with_unequal_content(self):
        self.assert_error(dict(foo='', bar=None))
        self.assert_error(dict(foo='first', bar='second'))
    
    def test_marks_second_field_as_faulty(self):
        e = self.assert_error(dict(foo='', bar=None))
        
        errors = e.unpack_errors()
        assert_equals(['bar'], list(errors))
        assert_not_none(errors['bar'])
        bar_error = errors['bar'].details()
        assert_equals('mismatch', bar_error.key())
