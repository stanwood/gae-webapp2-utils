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
from google.appengine.ext import ndb


class TimeoutError(Exception):
    pass


class Semaphore(object):

    SLEEP = 1.0
    DEADLINE = 60

    def __init__(self, key, value):
        self._key = key
        self._value = value

    def __enter__(self):
        self.acquire().get_result()

    def __exit__(self, *args):
        self.release().get_result()

    @ndb.tasklet
    def acquire(self, timeout=None):

        ctx = ndb.get_context()
        locked = False

        while not locked:

            value = yield ctx.memcache_get(self._key, for_cas=True)

            if value is None:
                locked = yield ctx.memcache_add(
                    self._key,
                    self._value,
                    self.DEADLINE,
                )
            elif not isinstance(value, int):
                raise TimeoutError
            elif value > 0:
                locked = yield ctx.memcache_cas(
                    self._key,
                    value - 1,
                    self.DEADLINE,
                )

            if locked:
                raise ndb.Return(self)

            if timeout is not None:
                if timeout <= 0:
                    raise TimeoutError

                timeout -= self.SLEEP

            yield ndb.sleep(self.SLEEP)

    @ndb.tasklet
    def release(self):
        yield ndb.get_context().memcache_incr(self._key)


class Lock(Semaphore):

    def __init__(self, key):
        super(Lock, self).__init__(key, 1)


class Event(object):

    SLEEP = 1.0
    DEADLINE = 60

    def __init__(self, key):
        self._key = key

    def clear(self):
        return ndb.get_context().memcache_delete(self._key)

    def is_set(self):
        return ndb.get_context().memcache_get(self._key)

    @ndb.tasklet
    def wait(self, timeout=None):

        while not (yield self.is_set()):

            if timeout is not None:
                if timeout <= 0:
                    raise TimeoutError

                timeout -= self.SLEEP

            yield ndb.sleep(self.SLEEP)

        raise ndb.Return(self)

    @ndb.tasklet
    def set(self):
        yield ndb.get_context().memcache_set(self._key, True, self.DEADLINE)
