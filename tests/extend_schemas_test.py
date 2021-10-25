# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from pycerberus.api import Validator
from pycerberus.schema import SchemaValidator
from pycerberus.validators import StringValidator


class ExtendSchemaTest(PythonicTestCase):
    
    class BasicSchema(SchemaValidator):
        id = Validator(exception_if_invalid=False)
        formvalidators = (Validator(exception_if_invalid=False),)
    
    def schema_class(self):
        return self.__class__.BasicSchema
    
    def schema(self):
        return self.schema_class()()
    
    def known_fields(self, schema):
        return set(schema.fieldvalidators().keys())
    
    # test functions
    
    def test_can_add_additional_validators_to_existing_schema(self):
        schema = self.schema()
        extended_schema = SchemaValidator()
        extended_schema.add('name', StringValidator())
        extended_schema.add_missing_validators(schema)

        assert_equals(set(['id', 'name']), self.known_fields(extended_schema))
        assert_length(1, schema.formvalidators())

    def test_existing_keys_are_kept(self):
        schema = self.schema()
        extended_schema = SchemaValidator()
        extended_schema.add('id', StringValidator())
        extended_schema.add_missing_validators(schema)

        assert_equals(set(['id']), self.known_fields(schema))
        assert_isinstance(extended_schema.validator_for('id'), StringValidator)

    def test_adding_validators_appends_formvalidators(self):
        schema = self.schema()
        extended_schema = SchemaValidator()
        extended_schema.add('id', StringValidator())
        extended_schema.add_formvalidator(StringValidator())
        extended_schema.add_missing_validators(schema)

        assert_length(2, extended_schema.formvalidators())

    def test_can_add_validators_from_schema_in_a_declarative_way(self):
        class ExtendedSchema(self.schema_class()):
            name = StringValidator()
            formvalidators = (StringValidator(), )
        
        extended_schema = ExtendedSchema()
        assert_equals(set(['id', 'name']), self.known_fields(extended_schema))
        assert_length(2, extended_schema.formvalidators())
        assert_isinstance(extended_schema.formvalidators()[1], StringValidator)

    def test_existing_names_from_superclass_are_replaced(self):
        class ExtendedSchema(self.schema_class()):
            id = StringValidator()
        
        extended_schema = ExtendedSchema()
        assert_isinstance(extended_schema.validator_for('id'), StringValidator)

