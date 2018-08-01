import abc


class PublicCachingMixin(object):
    """
    Abstract class for setting public cache_control, cache_control max_age and s_max_age.
    """
    __metaclass__ = abc.ABCMeta

    CLIENT_CACHE_TTL_SECONDS = 60  # client side cache in second
    CDN_CACHE_TTL_SECONDS = 60  # CDN / proxy cache
    CACHE_STATUS = frozenset((
        200,
        203,
        300,
        301,
        302,
        307,
        410,
    ))

    def dispatch(self):
        super(PublicCachingMixin, self).dispatch()
        if self.request.method == 'GET' and self.response.status_int in self.CACHE_STATUS:
            self.response.cache_control = 'public'
            self.response.cache_control.max_age = self.CLIENT_CACHE_TTL_SECONDS
            self.response.cache_control.s_max_age = self.CDN_CACHE_TTL_SECONDS
            self.response.md5_etag()
