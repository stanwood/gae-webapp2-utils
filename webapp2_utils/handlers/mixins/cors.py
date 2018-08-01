import abc


class HandlerMixin(object):
    """
    Abstract class for setting Cross-Origin Resource Sharing Headers.
    """
    __metaclass__ = abc.ABCMeta

    def dispatch(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        super(HandlerMixin, self).dispatch()

    def handle_exception(self, exception, debug):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        super(HandlerMixin, self).handle_exception(exception, debug)

    def options(self, *args, **kwargs):
        allowed_headers = (
            'Origin',
            'X-Requested-With',
            'Content-Type',
            'Accept',
            'X-Auth-Token',
            'X-Contentful-Content-Type',
            'Authorization',
            'X-Contentful-Version'
        )
        self.response.headers['Access-Control-Allow-Headers'] = ','.join(allowed_headers)
        self.response.headers['Access-Control-Allow-Methods'] = 'GET,PATCH,POST,PUT,DELETE'
