from moto import mock_aws

from files_api.s3.delete_objects import delete_s3_object
from files_api.s3.read_objects import object_exists_in_s3
from files_api.s3.write_objects import upload_s3_object
from tests.consts import TEST_BUCKET_NAME

# from tests.consts import TEST_BUCKET_NAME


@mock_aws
def test__object_exists_in_s3(mocked_aws: None):
    # Upload a file to the bucket
    object_key = "test.txt"
    file_content: bytes = b"Hello, world!"
    content_type = "text/plain"

    upload_s3_object(
        bucket_name=TEST_BUCKET_NAME,
        object_key=object_key,
        file_content=file_content,
        content_type=content_type
    )

    # Check that the file exists after uploading it
    response = object_exists_in_s3(bucket_name=TEST_BUCKET_NAME, object_key=object_key)
    assert bool(response)

    delete_s3_object(bucket_name=TEST_BUCKET_NAME, object_key=object_key)

    # Check that the file does not exist after deleting it
    response = object_exists_in_s3(bucket_name=TEST_BUCKET_NAME, object_key=object_key)
    assert not response
