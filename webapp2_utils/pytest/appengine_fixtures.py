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
import base64
import json
import os.path

import mock
import pytest
from google.appengine.ext import ndb


@pytest.fixture(autouse=True)
def freezegun_patch(monkeypatch):
    """Helps with datetime patching using Google App Engine modules."""

    import freezegun
    from google.appengine.api import datastore_types

    fix = datastore_types._VALIDATE_PROPERTY_VALUES.copy()
    fix[freezegun.api.FakeDatetime] = fix[freezegun.api.real_datetime]

    monkeypatch.setattr(datastore_types, '_VALIDATE_PROPERTY_VALUES', fix)

    fix = datastore_types._PACK_PROPERTY_VALUES.copy()
    fix[freezegun.api.FakeDatetime] = fix[freezegun.api.real_datetime]

    monkeypatch.setattr(datastore_types, '_PACK_PROPERTY_VALUES', fix)


@pytest.fixture
def deferred(testbed):
    """Allows to run all deferred tasks which were fired during test case."""

    class Deferred(object):

        def __init__(self, testbed):
            self.stub = testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

        def __enter__(self):
            pass

        def __exit__(self, type, value, traceback):

            from google.appengine.ext.deferred import deferred

            queues = (
                queue['name']
                for queue in self.stub.GetQueues()
            )

            for queue in queues:

                tasks = self.stub.get_filtered_tasks(queue_names=[queue])
                tasks = (
                    task
                    for task in tasks
                    if 'deferred' in task.url
                )

                for task in tasks:
                    deferred.run(task.payload)
                    self.stub.DeleteTask(queue, task.name)

    return Deferred(testbed)


@pytest.fixture(scope='session')
def responses():
    """Allows to mock responses and set their content from file."""

    class Responses(object):

        DIR = os.path.join(
            'tests',
            'responses',
        )

        def __getitem__(self, path):

            path = os.path.join(self.DIR, path)

            response = mock.MagicMock()
            response.status_code = 200

            with open(path) as response_file:
                response.content = response_file.read()

            future = ndb.Future()
            future.set_result(response)

            return future

    return Responses()


@pytest.fixture
def taskqueues(testbed):
    """Allows to obtain queued tasks from requests."""

    class TaskQueues(object):

        def __init__(self, testbed):
            self.stub = testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

        def __getitem__(self, queue):
            return tuple(
                base64.b64decode(task['body'])
                for task in self.stub.GetTasks(queue)
            )

    return TaskQueues(testbed)


@pytest.fixture
def testbed():
    """Helps with manipulate stubs for API testing on Google App Engine"""

    from google.appengine.datastore import datastore_stub_util
    from google.appengine.ext import testbed

    tb = testbed.Testbed()
    tb.consistency = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
        probability=1,
    )
    tb.activate()
    tb.init_app_identity_stub()
    tb.init_datastore_v3_stub(consistency_policy=tb.consistency)
    tb.init_memcache_stub()
    tb.init_urlfetch_stub()
    tb.init_app_identity_stub()
    tb.init_search_stub()

    tb.init_taskqueue_stub(root_path='.')
    tb.MEMCACHE_SERVICE_NAME = testbed.MEMCACHE_SERVICE_NAME
    tb.TASKQUEUE_SERVICE_NAME = testbed.TASKQUEUE_SERVICE_NAME

    yield tb

    tb.deactivate()


@pytest.fixture
def response(testbed):

    def get_response(json_response, status_code=200):
        response_mock = mock.MagicMock()
        response_mock.status_code = status_code
        response_mock.content = json.dumps(json_response)
        return response_mock

    yield get_response
