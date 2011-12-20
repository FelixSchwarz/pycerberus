# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2010 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pycerberus.api import Validator
from pycerberus.errors import InvalidDataError
from pycerberus.compat import set
from pycerberus.lib import PythonicTestCase
from pycerberus.lib.pythonic_testcase import *
from pycerberus.schema import SchemaValidator
from pycerberus.test_util import ValidationTest
from pycerberus.validators import IntegerValidator, StringValidator



class DeclarativeSchemaTest(ValidationTest):
    
    class DeclarativeSchema(SchemaValidator):
        allow_additional_parameters = False
        
        id = IntegerValidator()
        amount = IntegerValidator
        formvalidators = (Validator(), )
    validator_class = DeclarativeSchema
    
    def schema(self, schema_class=None, **kwargs):
        if schema_class is None:
            schema_class = self.__class__.DeclarativeSchema
        return schema_class(**kwargs)
    
    # -------------------------------------------------------------------------
    # setup / introspection
    
    def test_knows_its_fieldvalidators(self):
        self.assert_contains('id', self.schema().fieldvalidators().keys())
    
    def test_also_can_use_validator_classes(self):
        self.assert_contains('amount', self.schema().fieldvalidators().keys())
        self.assert_equals(set(['id', 'amount']), set(self.schema().fieldvalidators().keys()))
    
    def test_instance_uses_instances_of_validators_declared_as_class(self):
        first = self.schema().validator_for('amount')
        second = self.schema().validator_for('amount')
        self.assert_not_equals(first, second)
    
    def test_declared_validators_are_no_class_attributes_after_initialization(self):
        for fieldname in self.schema().fieldvalidators():
            self.assert_false(hasattr(self.schema(), fieldname))
    
    def test_can_have_formvalidators(self):
        assert_callable(self.schema().formvalidators)
        assert_length(1, self.schema().formvalidators())
    
    # -------------------------------------------------------------------------
    # warn about additional parameters
    
    def test_can_bail_out_if_additional_items_are_detected(self):
        e = self.assert_raises(InvalidDataError, lambda: self.schema().process(dict(id=42, amount=21, extra='foo')))
        self.assert_equals('Undeclared field detected: "extra".', e.msg())
    
    def test_can_override_additional_items_parameter_on_class_instantiation(self):
        schema = self.schema(allow_additional_parameters=True)
        schema.process(dict(id=42, amount=21, extra='foo'))
    
    def test_additional_items_parameter_is_inherited_for_schema_subclasses(self):
        class DerivedSchema(self.DeclarativeSchema):
            pass
        schema = DerivedSchema()
        self.assert_raises(InvalidDataError, lambda: schema.process(dict(id=42, amount=21, extra='foo')))
    
    # -------------------------------------------------------------------------
    # pass unvalidated parameters
    
    class PassValuesSchema(SchemaValidator):
        filter_unvalidated_parameters=False
        id = IntegerValidator()
    
    def test_passes_unvalidated_parameters_if_specified(self):
        self.init_validator(self.PassValuesSchema())
        assert_equals({'id': 42, 'foo': 'bar'}, self.process({'id': '42', 'foo': 'bar'}))
    
    def test_filter_unvalidated_parameter_is_inherited_for_schema_subclasses(self):        
        class DerivedSchema(self.PassValuesSchema):
            pass
        
        self.init_validator(DerivedSchema())
        assert_equals({'id': 42, 'foo': 'bar'}, self.process({'id': '42', 'foo': 'bar'}))
    
    def test_can_override_filter_unvalidated_parameter_on_class_instantiation(self):
        self.init_validator(self.PassValuesSchema(filter_unvalidated_parameters=True))
        assert_equals({'id': 42}, self.process({'id': '42', 'foo': 'bar'}))
    
    # -------------------------------------------------------------------------
    # sub-schemas
    
    def test_can_declare_schema_with_subschema(self):
        class PersonSchema(SchemaValidator):
            first_name = StringValidator
            last_name = StringValidator
        
        class UserSchema(SchemaValidator):
            user = PersonSchema
        self.init_validator(UserSchema())
        
        user_input = {'user': {'first_name': 'Foo', 'last_name': 'Bar'}}
        assert_equals(user_input, self.process(user_input))
    


