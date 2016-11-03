# This file was part of GrumpyWidgets, copyright (c) 2012 Felix Schwarz
# The source code contained in this file is licensed under the MIT license.

from copy import deepcopy


__all__ = ['FieldData', 'FormData']


class undefined(object):
    pass

class FieldData(object):
    def __init__(self, value=None, initial_value=None, errors=(), meta=None):
        self.value = value
        self.initial_value = initial_value
        self.errors = errors
        self.meta = meta if (meta is not None) else {}

    def copy(self):
        klass = self.__class__
        attributes = dict(
            value=deepcopy(self.value),
            errors=deepcopy(self.errors),
            initial_value=deepcopy(self.initial_value),
        )
        return klass(**attributes)
    __deepcopy__ = copy

    def __repr__(self):
        tmpl = 'FieldData(value=%r, initial_value=%r, errors=%r, meta=%r)'
        return tmpl % (self.value, self.initial_value, self.errors, self.meta)

    def contains_errors(self):
        return (self.errors is not None) and (len(self.errors) > 0)

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
            # "or ()" catches "errors=None" which is convenient when passing
            # a form validation result from pycerberus
            self.errors = tuple(errors or ())
        if meta is not undefined:
            self.meta = meta

    # for FieldData classes "set()" is just an alias for "update()". The
    # difference is only important for compound/repeating data containers but
    # all classes must provide the same API.
    set = update

# class RepeatingFieldData(object):
#     def __init__(self, child_creator):
#         self.items = []
#         self.child_creator = child_creator
#         self.count = 0
#
#     def contains_errors(self):
#         for item in self.items:
#             if item.contains_errors():
#                 return True
#         return False
#
#     @property
#     def errors(self):
#         errors_ = []
#         for context in self.items:
#             errors_.append(context.errors)
#         return tuple(errors_)
#
#     def update_value(self, value=None, initial_value=None, errors=None):
#         if initial_value is not None:
#             attr_name = 'initial_value'
#             values = initial_value
#         elif errors is not None:
#             attr_name = 'errors'
#             values = errors
#         else:
#             attr_name = 'value'
#             values = value
#         if len(self.items) == 0:
#             self._create_new_items(n=len(values))
#         else:
#             assert_equals(len(self.items), len(values))
#         for context, value_ in zip(self.items, values):
#             context.update_value(**{attr_name: value_})
#
#     def _create_new_items(self, n):
#         for i in range(n):
#             context = self.child_creator()
#             self.items.append(context)
#
#     @property
#     def value(self):
#         values = []
#         for context in self.items:
#             values.append(context.value)
#         return tuple(values)
#
#     @property
#     def initial_value(self):
#         values = []
#         for context in self.items:
#             values.append(context.initial_value)
#         return tuple(values)


class FormData(object):
    def __init__(self, child_names=None):
        if not child_names:
            children = ()
        else:
            children = ((name, FieldData()) for name in child_names)
        self.children = dict(children)
        self.global_errors = ()

    def __getattr__(self, name):
        if name not in self.children:
            klassname = self.__class__.__name__
            raise AttributeError('%s object has no child with name %r' % (klassname, name))
        return self.children[name]

    def __repr__(self):
        return 'FormData<children=%r>' % self.children

    def contains_errors(self):
        if self.global_errors:
            return True
        for child in self.children.values():
            if child.contains_errors():
                return True
        return False

    @property
    def errors(self):
        errors_ = {}
        for name, contexts in self.children.items():
            errors_[name] = contexts.errors
        return errors_

    def _set_global_errors(self, errors):
        self.global_errors = errors

    def _set_values(self, value, initial_value, errors, meta, clear_missing):
        def value_for(child_name, values, default_value=None):
            if values is undefined:
                return undefined
            return values.get(child_name, default_value)

        def ensure_all_keys_known(values):
            if values is undefined:
                return
            for key in values:
                if key not in self.children:
                    raise ValueError('unknown key %r' % (key, ))

        # setting "errors=None" seems to be quite natural to me and hopefully
        # leads to fewer surprises by callers.
        if errors is None:
            errors = {}
        is_dict_like = isinstance(errors, dict)
        if (not is_dict_like) and (errors is not undefined):
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

    def update(self, value=undefined, initial_value=undefined, errors=undefined):
        self._set_values(value, initial_value, errors, undefined, clear_missing=False)

    def set(self, value=undefined, initial_value=undefined, errors=undefined, meta=undefined):
        self._set_values(value, initial_value, errors, meta, clear_missing=True)

    def copy(self):
        context = self.__class__()
        for name, child in self.children.items():
            context.children[name] = child.copy()
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
        return self._collect_attribute_values('meta')

    def _collect_attribute_values(self, attribute_name):
        values = {}
        for name, contexts in self.children.items():
            values[name] = getattr(contexts, attribute_name)
        return values

    def get(self, name):
        return self.children.get(name)
