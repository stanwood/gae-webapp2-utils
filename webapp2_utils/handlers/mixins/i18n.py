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
