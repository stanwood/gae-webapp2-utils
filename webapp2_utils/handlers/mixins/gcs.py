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

import google.cloud.storage
import webapp2

from google.appengine.api.app_identity import app_identity
from retrying import retry


class CloudStorageMixin(object):
    """Abstract class to manage the Google Cloud Storage client."""
    __metaclass__ = abc.ABCMeta

    @property
    def storage(self):
        """
        Create GCS client for each request.

        ..note:
            It's a workaround for NotAllowed exception when calling app_identity methods.

        API Reference:
            https://googlecloudplatform.github.io/google-cloud-python/latest/storage/client.html#google.cloud.storage.client.Client

        :return: Client object
        :rtype: class google.cloud.storage.client.Client
        """
        return google.cloud.storage.Client()

    @abc.abstractproperty
    def folder(self):
        """Path to the folder where files should be stored on GCS"""
        pass

    @webapp2.cached_property
    def bucket(self):
        """Google Cloud Storage bucket.

        API Reference:
            https://googlecloudplatform.github.io/google-cloud-python/latest/storage/client.html#google.cloud.storage.client.Client.bucket

        :return: Bucket object
        :rtype: google.cloud.storage.bucket.Bucket
        """
        return self.storage.bucket(
            app_identity.get_default_gcs_bucket_name()
        )

    @retry(stop_max_attempt_number=3)
    def store(
        self, file_name, file_data,
        content_type='application/octet-stream',
        directory=None, metadata=None,
    ):
        """
        Saves file to Google Cloud Storage bucket.

        :param (str) file_name: Name of file.
        :param (str) file_data: File content.
        :param (str) content_type: File content type. Default: `application/octet-stream`
        :param (str) directory: File folder path in GCS
        :param (dict or None) metadata: File metadata

        :return: Blob object
        :rtype: google.cloud.storage.blob.Blob

        ..note:
            When this method fails, is it retried max 3 times.
        """
        blob_name = u'{}/{}'.format(directory or self.folder, file_name)
        blob_name = blob_name.encode('utf-8')
        blob = self.bucket.blob(blob_name)

        if metadata:
            blob.metadata = metadata

        blob.upload_from_string(file_data, content_type)

        return blob
