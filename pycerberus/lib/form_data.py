# This file was part of GrumpyWidgets, copyright (c) 2012 Felix Schwarz
# The source code contained in this file is licensed under the MIT license.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

from copy import deepcopy
import warnings

from pycerberus.compat import OrderedDict


__all__ = ['is_result', 'FieldData', 'FormData', 'RepeatingFieldData']

def is_result(value):
    return (
        hasattr(value, 'value') and
        hasattr(value, 'initial_value') and
        hasattr(value, 'errors') and
        hasattr(value, 'meta')
    )

def is_iterable(value):
    try:
        iter(value)
    except TypeError:
        return False
    if isinstance(value, Exception):
        # exceptions are iterable too (in Python 2), will iterable over .args
        return False
    return True

def is_simple_error(e):
    """
    The module should work will all kind of "error" instances but we should
    have some kind of duck typing here.
    """
    if hasattr(e, 'details') and callable(e.details):
        # InvalidDataError
        return True
    attr_names = ('key', 'message', 'value', 'context')
    for attr_name in attr_names:
        if not hasattr(e, attr_name):
            return False
    return True


class undefined(object):
    pass

class FieldData(object):
    def __init__(self, value=None, initial_value=None, errors=(), meta=None):
        self.value = value
        self.initial_value = initial_value
        self.errors = errors
        self.meta = meta if (meta is not None) else {}

    def copy(self, memo=None):
        klass = self.__class__
        value_ = deepcopy(self.value, memo=memo)
        errors_ = deepcopy(self.errors, memo=memo)
        initial_value_ = deepcopy(self.initial_value, memo=memo)
        meta_ = deepcopy(self.meta, memo=memo)
        attributes = dict(
            value=value_,
            errors=errors_,
            initial_value=initial_value_,
            meta=meta_,
        )
        return klass(**attributes)
    __deepcopy__ = copy

    def __repr__(self):
        tmpl = 'FieldData(value=%r, initial_value=%r, errors=%r, meta=%r)'
        return tmpl % (self.value, self.initial_value, self.errors, self.meta)

    @property
    def error_count(self):
        if self.errors is None:
            return 0
        return len(self.errors)

    def nr_errors(self):
        warnings.warn('"nr_errors()" is deprecated, use "error_count" instead')
        return self.error_count

    def contains_error(self):
        return (self.error_count > 0)

    def contains_errors(self):
        # will be deprecated after the next major release
        return self.contains_error()

    def contains_critical_error(self):
        if not self.contains_error():
            return False
        for error in self.errors:
            if error.is_critical:
                return True
        return False

    def add_error(self, error):
        _errors = list(self.errors)
        _errors.append(error)
        self.errors = tuple(_errors)

    def update(self, value=undefined, initial_value=undefined, errors=undefined, meta=undefined):
        if value is not undefined:
            self.value = value
        if initial_value is not undefined:
            self.initial_value = initial_value
        if errors is not undefined:
            if errors is None:
                # I find this convenient when passing a form validation result from pycerberus
                errors = ()
            elif is_simple_error(errors) or isinstance(errors, Exception):
                # exceptions are iterable too (in Python 2), see is_iterable()
                errors = (errors, )
            else:
                errors = tuple(errors)
            self.errors = errors
        if meta is not undefined:
            self.meta = meta

    # for FieldData classes "set()" is just an alias for "update()". The
    # difference is only important for compound/repeating data containers but
    # all classes must provide the same API.
    set = update


class RepeatingFieldData(object):
    def __init__(self, child_creator):
        self.items = []
        self.child_creator = child_creator
        self.count = 0
        self.global_errors = ()

    def __repr__(self):
        return 'RepeatingFieldData<items=%r>' % (self.items)

    def add_error(self, error):
        _errors = list(self.global_errors)
        _errors.append(error)
        self.global_errors = tuple(_errors)

    def contains_error(self):
        return (self.error_count > 0)

    def contains_errors(self):
        # will be deprecated after the next major release
        return self.contains_error()

    @property
    def error_count(self):
        count = len(self.global_errors)
        for item in self.items:
            count += item.error_count
        return count

    def nr_errors(self):
        warnings.warn('"nr_errors()" is deprecated, use "error_count" instead')
        return self.error_count

    @property
    def errors(self):
        if not self.contains_error():
            return None
        errors_ = []
        for context in self.items:
            errors_.append(context.errors or None)
        has_field_errors = len(tuple(filter(None, errors_))) > 0
        # this is one of the places where the "global errors" concept shows its
        # ugly side.
        if (not has_field_errors) and self.global_errors:
            errors_ = self.global_errors
        return tuple(errors_)

    def update(self, value=undefined, initial_value=undefined, errors=undefined, meta=undefined):
        # LATER: meta not implemented
        values = None
        if initial_value is not undefined:
            attr_name = 'initial_value'
            values = initial_value
        elif errors is not undefined:
            attr_name = 'errors'
            values = errors
        elif value is not undefined:
            attr_name = 'value'
            values = value
        if values is None:
            return

        if len(self.items) == 0:
            if not is_iterable(values):
                values = (values,)
            self._create_new_items(n=len(values))
        else:
            assert (len(self.items) == len(values))
        for context, value_ in zip(self.items, values):
            context.update(**{attr_name: value_})
    set = update

    def _create_new_items(self, n):
        for i in range(n):
            context = self.child_creator()
            self.items.append(context)

    @property
    def value(self):
        values = []
        for context in self.items:
            values.append(context.value)
        return tuple(values)

    @property
    def initial_value(self):
        values = []
        for context in self.items:
            values.append(context.initial_value)
        return tuple(values)

    @property
    def meta(self):
        values = []
        for item in self.items:
            values.append(item.meta)
        return tuple(values)


class FormData(object):
    def __init__(self, child_names=None, children=None):
        if child_names and children:
            raise ValueError('You can not specify "children" and "child_names"')

        self.children = OrderedDict()
        if children:
            for name, child in children.items():
                self.children[name] = child
            child_names = tuple(self.children)
        self.child_names = child_names or ()
        self._schema_meta = {}
        self.global_errors = ()

    def __getattr__(self, name):
        if name not in self.children:
            klassname = self.__class__.__name__
            raise AttributeError('%s object has no child with name %r' % (klassname, name))
        return self.children[name]

    def __repr__(self):
        return 'FormData<children=%r>' % self.children

    def contains_error(self):
        return (self.error_count > 0)

    def contains_errors(self):
        # will be deprecated after the next major release
        return self.contains_error()

    @property
    def error_count(self):
        count = len(self.global_errors)
        for child in self.children.values():
            count += child.error_count
        return count

    def nr_errors(self):
        warnings.warn('"nr_errors()" is deprecated, use "error_count" instead')
        return self.error_count

    def contains_critical_error(self):
        if not self.contains_error():
            return False
        for error in (self.global_errors or ()):
            if error.is_critical:
                return True
        for child in self.children.values():
            if child.contains_critical_error():
                return True
        return False

    def add_errors(self, errors):
        is_dict_like = isinstance(errors, dict)
        if is_dict_like:
            for child_name, error in errors.items():
                self.children[child_name].add_error(error)
        else:
            assert isinstance(errors, (list, tuple))
            global_errors = list(self.global_errors) + list(errors)
            self._set_global_errors(tuple(global_errors))

    @property
    def errors(self):
        errors_ = {}
        for name, contexts in self.children.items():
            if not contexts.errors:
                continue
            errors_[name] = contexts.errors
        return errors_

    def _set_global_errors(self, errors):
        self.global_errors = errors

    def _set_values(self, value, initial_value, errors, meta, clear_missing):
        def value_for(child_name, values, default_value=None):
            if values is undefined:
                return undefined
            if hasattr(values, 'get'):
                return values.get(child_name, default_value)
            # If the caller does not pass a dict-like object just ignore the
            # input to avoid exceptions later.
            return default_value

        def ensure_all_keys_known(values):
            if values is undefined:
                return
            for key in values:
                if key in self.children:
                    continue
                elif key in self.child_names:
                    self._add_child_data(key)
                else:
                    raise ValueError('unknown key %r' % (key, ))

        # setting "errors=None" seems to be quite natural to me and hopefully
        # leads to fewer surprises by callers.
        if errors is None:
            errors = {}
        is_dict_like = isinstance(errors, dict)
        if (not is_dict_like) and (errors is not undefined):
            if errors:
                self._set_global_errors(errors)
            errors = {}
        ensure_all_keys_known(value)
        ensure_all_keys_known(errors)
        ensure_all_keys_known(meta)

        for child_name in self.children:
            child = self.get(child_name)
            has_children = hasattr(child, 'children')

            if clear_missing:
                if has_children:
                    value_default = {}
                else:
                    value_default = None
                error_default = ()
            else:
                value_default = undefined
                error_default = undefined
            c_value = value_for(child_name, value, default_value=value_default)
            c_initial = value_for(child_name, initial_value, default_value=value_default)
            c_errors = value_for(child_name, errors, default_value=error_default)
            c_meta = value_for(child_name, meta, default_value=value_default)

            if has_children:
                child._set_values(c_value, c_initial, c_errors, c_meta, clear_missing)
                continue
            child.update(
                value=c_value, initial_value=c_initial, errors=c_errors, meta=c_meta,
            )

    def _add_child_data(self, child_name):
        assert (child_name not in self.children)
        assert (child_name in self.child_names)
        self.children[child_name] = FieldData()

    def update(self, value=undefined, initial_value=undefined, errors=undefined, schema_meta=undefined):
        self._set_values(value, initial_value, errors, undefined, clear_missing=False)
        if schema_meta is not undefined:
            self._schema_meta = schema_meta

    def set(self, value=undefined, initial_value=undefined, errors=undefined, meta=undefined, schema_meta=undefined):
        self._set_values(value, initial_value, errors, meta, clear_missing=True)
        if schema_meta is not undefined:
            self._schema_meta = schema_meta

    def copy(self):
        context = self.__class__()
        for name, child in self.children.items():
            context.children[name] = child.copy()
        context._schema_meta = deepcopy(self._schema_meta)
        return context
    __deepcopy__ = copy

    @property
    def value(self):
        return self._collect_attribute_values('value')

    @property
    def initial_value(self):
        return self._collect_attribute_values('initial_value')

    @property
    def meta(self):
        _meta = self._collect_attribute_values('meta')
        if self.schema_meta:
            assert '_schema_meta' not in _meta
            _meta['_schema_meta'] = self._schema_meta
        return _meta

    @property
    def schema_meta(self):
        return self._schema_meta

    def _collect_attribute_values(self, attribute_name):
        values = {}
        for name, contexts in self.children.items():
            values[name] = getattr(contexts, attribute_name)
        return values

    def get(self, name):
        return self.children.get(name)
