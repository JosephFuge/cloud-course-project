from moto import mock_aws

from files_api.s3.read_objects import (
    fetch_s3_object,
    fetch_s3_objects_metadata,
    fetch_s3_objects_using_page_token,
    object_exists_in_s3,
)
from files_api.s3.write_objects import upload_s3_object
from tests.consts import TEST_BUCKET_NAME

# from tests.consts import TEST_BUCKET_NAME


@mock_aws
def test__object_exists_in_s3(mocked_aws: None):
    # Upload a file to the bucket
    object_key = "test.txt"
    file_content: bytes = b"Hello, world!"
    content_type = "text/plain"

    # Check that the file does not exist before uploading it
    response = object_exists_in_s3(bucket_name=TEST_BUCKET_NAME, object_key=object_key)
    assert not response

    upload_s3_object(
        bucket_name=TEST_BUCKET_NAME,
        object_key=object_key,
        file_content=file_content,
        content_type=content_type
    )

    # Check that the file exists after uploading it
    response = object_exists_in_s3(bucket_name=TEST_BUCKET_NAME, object_key=object_key)
    
    assert bool(response)

@mock_aws
def test__fetch_s3_objects_metadata(mocked_aws: None):
    num_files = 5
    # Upload files to the bucket
    for i in range(num_files):
        upload_s3_object(
            bucket_name=TEST_BUCKET_NAME,
            object_key=f'test{i}.txt',
            file_content=b"Hello, world " + i.to_bytes(2, 'big') + b"!",
            content_type="text/plain"
        )

    # Check that the file does not exist before uploading it
    response = fetch_s3_objects_metadata(bucket_name=TEST_BUCKET_NAME, max_keys=3)

    assert response[1] is not None
    assert len(response[0]) == 3
    assert response[0][0]["Key"] == "test0.txt"

    response = fetch_s3_objects_metadata(bucket_name=TEST_BUCKET_NAME)

    assert len(response[0]) == num_files
    assert response[1] is None

@mock_aws
def test__fetch_s3_object(mocked_aws: None):
    object_key = "test.txt"
    file_content: bytes = b"Hello, world! - Testing fetch_s3_object"
    content_type = "text/plain"

    upload_s3_object(
        bucket_name=TEST_BUCKET_NAME,
        object_key=object_key,
        file_content=file_content,
        content_type=content_type
    )

    response = fetch_s3_object(bucket_name=TEST_BUCKET_NAME, object_key=object_key)
    assert response["ContentType"] == content_type
    stream = response.get('Body')
    assert stream.read() == file_content

@mock_aws
def test__fetch_s3_objects_using_page_token(mocked_aws: None):
    num_files = 10
    # Upload files to the bucket
    for i in range(num_files):
        upload_s3_object(
            bucket_name=TEST_BUCKET_NAME,
            object_key=f'test{i}.txt',
            file_content=b"Hello, world " + i.to_bytes(2, 'big') + b"!",
            content_type="text/plain"
        )
    
    (_, continuation_token) = fetch_s3_objects_metadata(bucket_name=TEST_BUCKET_NAME, max_keys=2)
    
    (objects, continuation_token) = fetch_s3_objects_using_page_token(bucket_name=TEST_BUCKET_NAME, continuation_token=continuation_token, max_keys=2)

    assert continuation_token is not None
    assert objects[0]["Key"] == 'test2.txt'