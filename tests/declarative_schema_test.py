# -*- coding: UTF-8 -*-

from pycerberus.api import Validator
from pycerberus.lib import PythonicTestCase
from pycerberus.schema import SchemaValidator
from pycerberus.validators import IntegerValidator



class DeclarativeSchemaTest(PythonicTestCase):
    
    class DeclarativeSchema(SchemaValidator):
        id = IntegerValidator()
        amount = IntegerValidator
        formvalidators = (Validator(), )
    
    def schema(self, schema_class=None):
        if schema_class is None:
            schema_class = self.__class__.DeclarativeSchema
        return schema_class()
    
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
        self.assert_callable(self.schema().formvalidators)
        self.assert_length(1, self.schema().formvalidators())


