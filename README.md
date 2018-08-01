# GAE Webapp2 utils

## About

Helper module for most common features used in webapp2 and Google App Engine.

## Install

Add folder as a git submodule:
```
git submodule add git:...
```

Add submodule folder to the `appengine_config.py`:
```python
import os

from google.appengine.ext import vendor

vendor.add(os.path.join(os.path.dirname(__file__), 'path/to/submodule/webapp2_utils'))
```

## Usage

### Handlers

Create simple webapp2 handler which returns JSON body with CORS and Public Cache

```python
from webapp2_utils.handlers import base
from webapp2_utils.handlers.mixins import cache
from webapp2_utils.handlers.mixins import cors


class SampleHandler(base.BaseHandler, cors.HandlerMixin, cache.PublicCachingMixin):
    def get(self):
        self.json_response({'msg': 'My sample response in json'})
```

--- 

Create simple webapp2 handler which downloads file from Google Cloud Storage

```python
from webapp2_utils.handlers import base
from webapp2_utils.handlers.mixins import gcs


class BlobHandler(base.BaseHandler, gcs.CloudStorageMixin):
    def get(self):
        file_name = self.request.GET.get('file_name')
        blob = self.bucket.get_blob(file_name)
        if not blob:
            self.abort(404, 'File does not exist on GCS')
        
        self.json_response({'file_url': blob.generate_signed_url()})
```

---

Create secured handler with auth token

```python
from webapp2_utils.handlers import base
from webapp2_utils.handlers import decorators

class SecuredHandler(base.BaseHandler):
    @decorators.token_required('my-auth-token')
    def get(self):
        self.json_response({'msg': 'Success auth'})
```

---

Create internationalized handler
```python
from webapp2_extras.i18n import gettext as _

from webapp2_utils.handlers import base
from webapp2_utils.handlers.mixins import i18n as i18n_mixin


class TranslatedHandler(base.BaseHandler, i18n_mixin.I18nRequestHandler):
    def get(self):
        self.json_response({'msg': _('This is my translated text')})
```

## Pytest

Test webapp2 handler
```python
import pytest
import webtest

@pytest.fixture
def app(testbed):
    from main import app
    return webtest.TestApp(app)
    

from webapp2_utils.pytest.appengine_fixtures import *

def test_handler(app):
    
    response = app.get('/my/url')
    assert response.status_code == 200
```

Using `freezegun` in Google App Engine test config

```python
import datetime

import freezegun

from webapp2_utils.handlers import base

class DateHandler(base.BaseHandler):
    """Routed as /date url"""
    def get(self):
        self.json_response({'date': datetime.datetime.now().date().isoformat()})


from webapp2_utils.pytest.appengine_fixtures import *  # import it in conftest

@freezegun.freeze_time('2018-08-08')
def test_date_handler(app, freezegun_patch):
    response = app.get('/date')
    
    assert response.json['date'] == '2018-08-08'
```

Testing `taskqueues` in Google App Engine

```python
import webapp2
from google.appengine.api import taskqueue

from webapp2_utils.handlers import base

class TaskHandler(base.BaseHandler):
    @webapp2.cached_property
    def queue(self):
        return taskqueue.Queue('sampleTask')

    def get(self):
        url = '/_ah/queue/sample/task'
        self.queue.add(taskqueue.Task(url=url))


from webapp2_utils.pytest.appengine_fixtures import *  # import it in conftest

def test_task_handler(app, taskqueue):
    app.get('/task')
    
    tasks = taskqueue.GetTasks(queue_name='queueName')

    assert len(tasks) == 1
    assert tasks[0]['url'] == '/_ah/queue/sample/task'
```


## ndb

Create base model with created and updated fields

```python
from google.appengine.ext import ndb

from webapp2_utils.ndb.models.base import Model


class MyModel(Model):
    new_field = ndb.StringProperty()
```