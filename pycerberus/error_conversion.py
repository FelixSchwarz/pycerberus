# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT
"""
Helper functions to convert between pycerberus.Error and InvalidDataError
instances (also recursively). The conversion is lossy but the important parts
("field X contains error Y") must be transportet.

The reason for this code is that there are callers relying on the "classic"
exception-based API and there are validators which are not ported yet (but are
included in result-aware schemas).
"""

from __future__ import absolute_import, print_function, unicode_literals

import six

from .lib.form_data import is_iterable, is_simple_error
from .errors import Error, InvalidDataError


__all__ = [
    'error_from_exception',
    'exception_from_errors',
    'exception_to_errors',
]

def error_from_exception(e, is_critical=True):
    if isinstance(e, Error):
        return e
    d = e.details()
    return Error(
        key=d.key(),
        msg=d.msg(),
        value=d.value(),
        context=d.context(),
        is_critical=is_critical
    )


def exception_to_errors(e):
    if e is None:
        return None

    error_dict = None
    error_list = None
    if hasattr(e, '_error_dict') and e._error_dict:
        error_dict = e._error_dict
    elif hasattr(e, '_error_list') and e._error_list:
        error_list = e._error_list

    if (not error_dict) and (not error_list):
        assert isinstance(e, (Exception, Error)), 'not a single exception: %r' % (e,)
        return error_from_exception(e)
    elif error_dict:
        error_info = dict()
        for field, error in error_dict.items():
            error_info[field] = exception_to_errors(error)
        return error_info
    else: # error_list
        error_info_list = []
        for error in error_list:
            error_info = exception_to_errors(error)
            error_info_list.append(error_info)
        return error_info_list


def exception_from_error(error, error_dict=None, error_list=()):
    if isinstance(error, InvalidDataError):
        return error
    return InvalidDataError(
        error.message, error.value, error.key, error.context,
        error_dict=error_dict,
        error_list=error_list
    )

def exception_from_error_dict(error_dict):
    first_exc = None
    _error_dict = {}
    for field_name, field_errors in error_dict.items():
        if not field_errors:
            continue
        if isinstance(field_errors, dict):
            exc = exception_from_error_dict(field_errors)
        else:
            first_error = field_errors[0]
            # We need to differentiate between a list of errors referring
            # to the same (simple) field and a list of errors referring to
            # a list of fields. We can't deduct that from the container (tuple).
            if is_simple_error(first_error):
                exc = exception_from_errors(first_error)
            else:
                exc = exception_from_errors(field_errors)
        if first_exc is None:
            first_exc = exc
        _error_dict[field_name] = exc

    assert first_exc is not None, 'no error found?'
    first_error = error_from_exception(first_exc)
    return exception_from_error(first_error, error_dict=_error_dict)

def exception_from_error_list(errors):
    first_exc = None
    error_list = []
    for item_errors in errors:
        if is_simple_error(item_errors):
            exc = exception_from_error(item_errors)
        elif not item_errors: # None, (), {}
            exc = None
        elif isinstance(item_errors, dict):
            exc = exception_from_error_dict(item_errors)
        else:
            if is_simple_error(item_errors):
                error = item_errors
            elif is_iterable(item_errors) and not isinstance(item_errors, six.string_types):
                error = item_errors[0]
            else:
                raise ValueError('should not reach this.')

            errors_ = [exception_from_error(error)]
            exc = exception_from_error(error, error_list=errors_)

        if (exc is not None) and (first_exc is None):
            first_exc = exc
        error_list.append(exc)

    if first_exc is None:
        return None
    first_error = error_from_exception(first_exc)
    return exception_from_error(first_error, error_list=tuple(error_list))

def exception_from_errors(errors):
    if is_simple_error(errors):
        return exception_from_error(errors)
    elif isinstance(errors, dict):
        return exception_from_error_dict(errors)
    else:
        return exception_from_error_list(errors)
