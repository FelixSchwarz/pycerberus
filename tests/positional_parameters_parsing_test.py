# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.schemas import PositionalArgumentsParsingSchema
from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator, StringValidator


class TestPositionalArgumentsWithoutData(ValidationTest):
    
    validator_class = PositionalArgumentsParsingSchema
    
    def test_accept_input_without_parameters(self):
        self.init_validator(self.schema())
        self.assert_is_valid('', expected={})
        self.assert_is_valid(None, expected={})

    def test_bails_out_if_additional_parameters_are_passed(self):
        e = self.assert_error('foo bar')
        assert_equals(u'Unknown parameter "foo bar"', e.msg())


class TestPositionalArgumentsWithSingleParameter(ValidationTest):
    
    class SingleParameterSchema(PositionalArgumentsParsingSchema):
        foo = StringValidator()
        parameter_order = ('foo', )
    validator_class = SingleParameterSchema    
    
    def test_bails_out_if_no_parameter_is_passed(self):
        self.assert_error('')
        self.assert_error(None)
    
    def test_bails_out_if_too_many_parameters_are_passed(self):
        e = self.assert_error('foo, bar, baz')
        assert_equals(u'Unknown parameter "bar, baz"', e.msg())

    def test_accepts_one_parameter(self):
        self.init_validator(self.schema())
        self.assert_is_valid('fnord', expected={'foo': 'fnord'})


class TestPositionalArgumentsWithMultipleParameters(ValidationTest):
    
    class MultipleParametersSchema(PositionalArgumentsParsingSchema):
        foo = StringValidator()
        bar = IntegerValidator()
        parameter_order = ('foo', 'bar')
    validator_class = MultipleParametersSchema    
    
    def test_bails_out_if_only_one_parameter_is_passed(self):
        self.assert_error('fnord')
    
    def test_accepts_two_parameter(self):
        self.init_validator(self.schema())
        self.assert_is_valid('fnord, 42', expected={'foo': 'fnord', 'bar': 42})



class TestProgrammaticSchemaConstructionForPositionalArguments(ValidationTest):
    def setUp(self):
        schema = PositionalArgumentsParsingSchema()
        schema.set_internal_state_freeze(False)
        schema.add('id', IntegerValidator())
        schema.set_parameter_order(['id'])
        schema.set_internal_state_freeze(True)
        # the helper methods will use this private attribute
        self._validator = schema
        
    def test_can_instantiate_schema_programmatically(self):
        self.assert_is_valid('42', expected={'id': 42})
        self.assert_error('foo')
        self.assert_error('foo, bar')
        

