import boto3
from fastapi import status
from fastapi.testclient import TestClient

from files_api.schemas import DEFAULT_GET_FILES_MAX_PAGE_SIZE
from tests.consts import TEST_BUCKET_NAME
from tests.unit_tests.utils import delete_s3_bucket


def test_get_nonexistant_file(client: TestClient):
    response = client.get("/files/nonexistant_file.txt")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "File not found: nonexistant_file.txt"}

def test_delete_nonexistant_file(client: TestClient):
    response = client.delete("/files/nonexistant_file.txt")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "File not found: nonexistant_file.txt"}

def test_head_nonexistant_file(client: TestClient):
    response = client.head("/files/nonexistant_file.txt")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_files__invalid_page_size(client: TestClient):
    response = client.get("/files?page_size=-1")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = client.get(f"/files?page_size={DEFAULT_GET_FILES_MAX_PAGE_SIZE + 1}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_bad_file_path(client: TestClient):
    response = client.get("/files/🔥a*-;[]'.<>?|\\")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_files_page_token_is_mutually_exclusive_with_page_size_and_directory(client: TestClient):
    response = client.get("/files?page_token=token&page_size=10")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "mutually exclusive" in str(response.json())

    response = client.get("/files?page_token=token&directory=dir")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "mutually exclusive" in str(response.json())

def test_unforeseen_500_error(client: TestClient):
    # delete the S3 bucket and all the objects inside
    delete_s3_bucket(TEST_BUCKET_NAME)

    # make a request to the API to a route that interacts with the S3 bucket
    response = client.get("/files")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Internal server error"}