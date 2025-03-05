"""Test write file operations."""

import boto3
from moto import mock_aws

from tests.consts import TEST_BUCKET_NAME
from tests.unit_tests.utils import upload_test_object

# from tests.consts import TEST_BUCKET_NAME


@mock_aws
def test__upload_s3_object(mocked_aws: None):
    """Test uploading an object."""
    # Upload a file to the bucket
    object_key, file_content, content_type = upload_test_object()

    # Check that the file was uploaded with the correct content type
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=TEST_BUCKET_NAME, Key=object_key)
    assert response["ContentType"] == content_type
    assert response["Body"].read() == file_content
