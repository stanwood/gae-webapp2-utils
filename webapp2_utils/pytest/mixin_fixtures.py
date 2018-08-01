import mock
import pytest


@pytest.fixture
def bucket(testbed):
    with mock.patch(
        'webapp2_utils.handlers.mixins.gcs.CloudStorageMixin.bucket',
        new_callable=mock.PropertyMock,
    ) as bucket_mock:
        yield bucket_mock
