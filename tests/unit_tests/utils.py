"""Define commonly used utils."""

from typing import Tuple

import boto3

from files_api.s3.write_objects import upload_s3_object
from tests.consts import TEST_BUCKET_NAME


def delete_s3_bucket(bucket_name: str) -> None:
    """Delete an S3 bucket and all objects inside."""
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()
    bucket.delete()


def upload_test_object() -> Tuple[str, bytes, str]:
    """Upload a simple object to bucket for testing."""
    object_key = "test.txt"
    file_content: bytes = b"Hello, world!"
    content_type = "text/plain"
    upload_s3_object(
        bucket_name=TEST_BUCKET_NAME, object_key=object_key, file_content=file_content, content_type=content_type
    )
    return object_key, file_content, content_type
