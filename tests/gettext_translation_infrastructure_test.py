# -*- coding: UTF-8 -*-
# This file is a part of pycerberus.
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# SPDX-License-Identifier: MIT

from __future__ import absolute_import, print_function, unicode_literals

import os

from pythonic_testcase import *

from pycerberus.i18n import GettextTranslation


class GettextTranslationInfrastructureTest(PythonicTestCase):
    
    def test_domain(self):
        assert_equals('messages', GettextTranslation()._domain())
        assert_equals('foobar', GettextTranslation(domain='foobar')._domain())

    def _localedir(self, **kwargs):
        return GettextTranslation(**kwargs)._args(None)['localedir']
    
    def test_default_localedir_is_in_source_folder(self):
        this_file = os.path.abspath(__file__)
        source_root_dir = os.path.dirname(os.path.dirname(this_file))
        default_locale_dir = self._localedir()
        assert_true(default_locale_dir.startswith(source_root_dir), default_locale_dir)

    def test_can_specify_localedir(self):
        localedir = '/usr/share/locale'
        assert_equals(localedir, self._localedir(localedir=localedir))

    def test_can_extract_locale_name_from_context(self):
        translation = GettextTranslation()
        assert_equals('en', translation._locale(None))
        assert_equals('en', translation._locale({}))
        assert_equals('fr', translation._locale({'locale': 'fr'}))


