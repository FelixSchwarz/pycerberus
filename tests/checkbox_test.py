# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.schema import SchemaValidator
from pycerberus.test_util import ValidationTest
from pycerberus.validators import BooleanCheckbox


class BooleanCheckboxTest(ValidationTest):
    
    validator_class = BooleanCheckbox
    
    def test_false_values(self):
        assert_false(self.process('off'))
        assert_false(self.process('false'))
        assert_false(self.process(False))
        assert_false(self.process(None))
        assert_false(self.process(''))
    
    def test_true_values(self):
        assert_true(self.process('on'))
        assert_true(self.process('true'))
        assert_true(self.process(True))

    def test_can_set_trueish_and_falsish_values(self):
        self.init_validator(trueish=('a',), falsish=('b',))
        assert_true(self.process('a'))
        assert_false(self.process('b'))
        self.assert_error('0')
        self.assert_error('1')

    def test_accepts_all_trueish_values(self):
        trueish = (42, 'fnord', 'on', 'true')
        self.init_validator(trueish=trueish)
        for value in trueish:
            assert_true(self.process(value),
                message='should treat %r as True' % (value,))

    def test_can_handle_trueish_zero_and_falsish_one(self):
        # 0/1 (integers) in Python are a bit special:
        # "1 == True" but "1 is not True"
        # "0 == False" but "0 is not False"
        # still we go the extra mile to allow using 0 as trueish/1 as falsish
        # (while at the same time True should still be trueish/False should be
        # falsish)
        self.init_validator(trueish=(0,), falsish=(1,))
        assert_true(self.process(0))
        assert_false(self.process(1))

    def test_strips_by_default(self):
        assert_true(self.process('  true  '))
    
    def test_ignores_case(self):
        assert_true(self.process('ON'))
        assert_true(self.process('TrUe'))
        assert_false(self.process('oFf'))
        assert_false(self.process('FaLsE'))
    
    def test_rejects_values_which_are_neither_true_nor_false(self):
        e = self.assert_error('maybe')
        assert_equals('unknown_bool', e.details().key())
    
    def test_treat_missing_value_in_schema_as_false(self):
        # regression test!
        class CheckboxSchema(SchemaValidator):
            allow_additional_parameters = True
            decision = BooleanCheckbox()
        assert_equals({'decision': False}, CheckboxSchema().process({}))
        assert_equals({'decision': False}, CheckboxSchema().process({'foo': 'bar'}))
    
    def test_can_revert_conversion_for_falsish_values(self):
        assert_false(self.revert_conversion(False))
        assert_false(self.revert_conversion('false'))
        assert_false(self.revert_conversion('FALSE'))
        assert_false(self.revert_conversion('off'))
        assert_false(self.revert_conversion(None))
        assert_false(self.revert_conversion([]))
        assert_false(self.revert_conversion('invalid'))
    
    def test_can_revert_conversion_for_trueish_values(self):
        assert_true(self.revert_conversion(True))
        assert_true(self.revert_conversion('true'))
        assert_true(self.revert_conversion('TRUE'))
        assert_true(self.revert_conversion('on'))
        assert_true(self.revert_conversion('t'))

