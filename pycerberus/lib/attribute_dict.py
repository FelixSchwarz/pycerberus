# -*- coding: UTF-8 -*-

# License: Public Domain
# Authors: Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Version 1.1
#
# 1.1 (08.09.2015)
#   - set items via attributes
#
# 1.0 (06.02.2010)
#   - initial release

from unittest import TestCase


__all__ = ['AttrDict']


class AttrDict(dict):
    def __getattr__(self, name):
        if name not in self:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
        return self[name]

    def __setattr__(self, name, value):
        if name not in self:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
        self[name] = value


class AttributDictTests(TestCase):
    def test_can_use_class_as_dict(self):
        obj = AttrDict(foo=1, bar=2)
        self.assertEquals(1, obj['foo'])
        self.assertEquals(2, obj['bar'])

    def test_can_access_items_as_attributes(self):
        obj = AttrDict(foo=1, bar=2)
        self.assertEquals(1, obj.foo)
        self.assertEquals(2, obj.bar)

    def test_can_set_values_via_attributes(self):
        obj = AttrDict(foo=1, bar=2)
        obj.foo = 21
        self.assertEquals(21, obj.foo)
        obj.bar = 42
        self.assertEquals(42, obj.bar)

    def test_raise_attribute_error_for_non_existent_keys(self):
        obj = AttrDict(foo=1)
        self.assertRaises(AttributeError, getattr, obj, 'invalid')
        self.assertRaises(AttributeError, setattr, obj, 'invalid', 'something')

