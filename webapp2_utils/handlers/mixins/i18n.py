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
import abc
import dateutil.tz
import json
import logging

import webapp2_extras.i18n


class I18nRequestHandler(object):
    """Internationalization abstract class for Request Handlers."""

    __metaclass__ = abc.ABCMeta

    @property
    def locale(self):
        return self.request.headers.get('Accept-Language', 'de_DE')

    def log_request_body(self):
        logging.info(
            json.dumps(
                dict(self.request.headers.iteritems()),
                indent=2,
            )
        )
        logging.info(self.request.body)

    def log_response_body(self):
        try:
            logging.info(
                json.dumps(
                    self.response.json,
                    indent=2,
                )
            )
        except ValueError:
            logging.info(self.response.body)

    def set_locale(self):
        """
        Sets i18n locale for the request.
        """
        i18n = webapp2_extras.i18n.get_i18n()

        logging.info('Locale: {}'.format(self.locale))

        i18n.set_locale(self.locale.replace('-', '_'))

        i18n.tzinfo = dateutil.tz.gettz('Europe/Berlin')

    def dispatch(self):
        """
        Dispatches handler and sets locale for the request.
        """

        self.log_request_body()
        self.set_locale()

        super(I18nRequestHandler, self).dispatch()

        self.log_response_body()
