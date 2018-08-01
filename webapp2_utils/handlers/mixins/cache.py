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
