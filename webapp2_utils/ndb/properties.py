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
