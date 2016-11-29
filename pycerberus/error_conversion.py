# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
"""
Helper functions to convert between pycerberus.Error and InvalidDataError
instances (also recursively). The conversion is lossy but the important parts
("field X contains error Y") must be transportet.

The reason for this code is that there are callers relying on the "classic"
exception-based API and there are validators which are not ported yet (but are
included in result-aware schemas).
"""

from .errors import Error


__all__ = [
    'error_from_exception',
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

