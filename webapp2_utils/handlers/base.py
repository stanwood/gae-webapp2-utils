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
import datetime
import json
import logging

import webapp2
from google.appengine.ext import ndb


class JsonEncoder(json.JSONEncoder):
    """
    JSON body encoder.

    Usage:
        import json

        json_encoder = JsonEncoder
        json_encoder.DATETIME_FORMAT = '%Y-%m-%d'
        body = json.dumps({'msg': 'my message'}, cls=JsonEncoder)
    """

    DATETIME_FORMAT = None

    def default(self, obj):
        """
        Recursive method for parsing Python types to JSON body format.
        Supports parser for ndb.Model.

        :param obj: Any Python object
        :return: JSON parsable object
        """
        if isinstance(obj, list):
            return map(lambda x: self.default(x), obj)

        if isinstance(obj, dict):
            return {key: self.default(value) for key, value in obj.iteritems()}

        if isinstance(obj, ndb.Model):
            data = obj.to_dict()
            data['id'] = str(obj.key.id())
            return self.default(data)

        if isinstance(obj, datetime.datetime):
            return obj.isoformat() if not self.DATETIME_FORMAT else obj.strftime(self.DATETIME_FORMAT)

        if isinstance(obj, (unicode, str, int, float)) or obj is None:
            return obj

        if isinstance(obj, ndb.Key):
            return str(obj.id())

        if isinstance(obj, ndb.GeoPt):
            return obj.__str__()

        return super(JsonEncoder, self).default(obj)


class BaseHandler(webapp2.RequestHandler):
    """Abstract base handler for Requests Handlers."""
    __metaclass__ = abc.ABCMeta

    def dispatch(self):
        """
        Dispatches handler and sets content type header to application/json by default.
        """
        self.response.content_type = 'application/json'
        super(BaseHandler, self).dispatch()

    def handle_exception(self, exception, debug):
        if isinstance(exception, webapp2.HTTPException):
            self.response.status_int = exception.code

        logging.exception(exception)

        self.response.write(
            json.dumps(
                {
                    'error': u'{}'.format(exception)
                }
            )
        )

    def json_response(self, data, status=200):
        """
        Sets response content and content type as json body.

        :param data: JSON parsable object.
        :param (int) status: HTTP status code. Default 200
        """
        self.response.headers['Content-Type'] = 'application/json'
        self.response.status_int = status
        self.response.write(json.dumps(data, cls=JsonEncoder))

    def xml_response(self, data, status=200):
        """
        Sets response content and content type as xml body.

        :param (str) data: XML body.
        :param (int) status: HTTP status code. Default 200
        """
        self.response.headers['Content-Type'] = 'application/xml'
        self.response.status_int = status
        self.response.write(data)
