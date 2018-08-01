import functools
import logging
import time

from google.appengine.api import memcache
import webob.exc


def cache_control(
    max_age=None,
    s_max_age=None,
    status=frozenset((
        200,
        203,
        300,
        301,
        302,
        307,
        410,
    )),
):
    """
    Customize HTTP Cache-Control Header Value

    :param max_age: Specifies the maximum amount of time a resource will be considered fresh
    :param s_max_age: Takes precedence over max-age or the Expires header,
                      but it only applies to shared caches (e.g., proxies) and is ignored by a private cache.
    :param status: HTTP status code set
    """
    def decorator(f):

        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):

            f(self, *args, **kwargs)

            if self.response.status_code in status:
                self.response.cache_control = 'public'
                self.response.cache_control.max_age = max_age
                self.response.cache_control.s_max_age = s_max_age

        return wrapper

    return decorator


def rate_limit(
    limit,
    seconds,
    path='',
    key=lambda self: self.request.remote_addr,
):
    """
    Limits request calls

    :param limit: Defines max number of request to the handler
    :param seconds: Time in seconds to define timestamp in memcache_key
                    of cache by formula: timestamp - timestamp % seconds
    :param path: Path used for unique memcache key combined with timestamp and key
    :param key: Part of memcache_key. Default remote address of the request
    """

    def decorator(f):

        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):

            timestamp = long(time.time())
            timestamp = timestamp - timestamp % seconds

            rate = memcache.incr(
                '{timestamp}|{key}|{path}'.format(
                    key=key(self),
                    path=path,
                    timestamp=timestamp,
                ),
                initial_value=0,
            )

            if rate > limit:
                raise webob.exc.HTTPTooManyRequests()

            f(self, *args, **kwargs)

        return wrapper

    return decorator


def schema(schema):
    """
    Validate Request's Payload with provided JSON Schema

    :param (dict) schema: JSON schema with fields specification

    API Reference for schema format:
        https://pypi.org/project/jsonschema/
    """

    import jsonschema

    def decorator(f):

        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):

            if f.__name__ == 'get':
                data = self.request.GET.mixed()
            else:
                try:
                    data = self.request.json
                except ValueError as e:
                    raise jsonschema.ValidationError(e.message)

            jsonschema.validate(data, schema)

            f(self, *args, **kwargs)

        return wrapper

    return decorator


def token_required(token):
    """
    Verifies token sent in request in `X-Auth-Token` header.
    If token is correct decorated method is executed. Otherwise request raises 401 HTTP error.

    :param (str) token: Secret token used to authorization.
    """

    def wrap(func):

        def func_wrapper(self, *args, **kwargs):
            auth_token = self.request.headers.get('X-Auth-Token') or self.request.get('token')

            if auth_token != token:
                logging.error('401: {}'.format(auth_token))
                return self.abort(401, 'Unauthorized')

            return func(self, *args, **kwargs)

        return func_wrapper

    return wrap
