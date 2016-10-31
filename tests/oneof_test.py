# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.

from pythonic_testcase import *

from pycerberus.test_util import ValidationTest
from pycerberus.validators import OneOf



class OneOfTest(ValidationTest):
    
    validator_class = OneOf
    validator_args = (['foo', 'bar'], )
    
    def test_passes_if_item_is_in_allowed_values(self):
        self.process('foo')
        self.process('bar')
    
    def test_rejects_values_missing_in_allowed_values(self):
        self.assert_error('baz')
        self.assert_error('foobar')
        self.assert_error(None)
    
    def assert_raises_error_with_key(self, value, error_key):
        assert_equals(error_key, self.assert_error(value).details().key())

