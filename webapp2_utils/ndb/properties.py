# The MIT License (MIT)
# 
# Copyright (c) 2018 stanwood GmbH
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
import json

import webapp2_extras.i18n

from google.appengine.ext import ndb


class TextProperty(ndb.BlobProperty):

    class I18NString(unicode):

        def __new__(cls, kwargs):

            try:
                locale = webapp2_extras.i18n.get_i18n().locale
            except AssertionError:
                locale = ''

            if locale:
                locale = locale.replace('_', '-').lower()
                locale = locale.split('-')[0]

            try:
                value = kwargs[locale]
            except KeyError:
                value = kwargs.get('en', '')

            if value is None:
                value = ''

            self = super(TextProperty.I18NString, cls).__new__(cls, value)
            self.i18n = kwargs

            return self

        def __getitem__(self, key):
            return self.i18n.get(key, None)

        def __setitem__(self, key, value):
            self.i18n[key] = value

    def _from_base_type(self, value):

        return json.loads(
            value,
            object_hook=TextProperty.I18NString,
        )

    def _to_base_type(self, value):

        if isinstance(value, TextProperty.I18NString):
            value = value.i18n

        return json.dumps(value)
