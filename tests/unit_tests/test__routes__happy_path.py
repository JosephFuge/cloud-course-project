"""Test API Routes happy paths."""

from fastapi import status
from fastapi.testclient import TestClient

from files_api.s3.read_objects import object_exists_in_s3
from tests.consts import TEST_BUCKET_NAME

TEST_FILE_PATH = "some/file.txt"
TEST_FILE_CONTENT = b"some content"
TEST_FILE_CONTENT_TYPE = "text/plain"


def test_upload_file(client: TestClient):
    """Test the file upload route."""
    # create a file
    response = client.put(
        f"/v1/files/{TEST_FILE_PATH}", files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"file_path": TEST_FILE_PATH, "message": f"New file uploaded at path: /{TEST_FILE_PATH}"}

    # update an existing file
    updated_content = b"updated content"
    response = client.put(
        f"/v1/files/{TEST_FILE_PATH}", files={"file": (TEST_FILE_PATH, updated_content, TEST_FILE_CONTENT_TYPE)}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "file_path": TEST_FILE_PATH,
        "message": f"Existing file updated at path: /{TEST_FILE_PATH}",
    }


def test_list_files_with_pagination(client: TestClient):
    """Test the list files with paging route."""
    for i in range(13):
        client.put(
            f"/v1/files/file{i}.txt", files={"file": (f"file{i}.txt", TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)}
        )

    response = client.get("/v1/files?page_size=10")
    assert response

    assert response.status_code == 200
    data = response.json()
    assert len(data["files"]) == 10
    assert "next_page_token" in data


def test_get_file_metadata(client: TestClient):
    """Test the fetch file metadata route."""
    client.put(
        f"/v1/files/{TEST_FILE_PATH}", files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)}
    )

    response = client.head(f"/v1/files/{TEST_FILE_PATH}")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == TEST_FILE_CONTENT_TYPE
    assert response.headers["Content-Length"] == str(len(TEST_FILE_CONTENT))

    # format_string = "%Y-%m-%d %H:%M:%S+00:00"
    # last_modified: datetime.datetime = datetime.datetime.strptime(response.headers["Last-Modified"], format_string)
    assert "Last-Modified" in response.headers


def test_get_file(client: TestClient):
    """Test the fetch file route."""
    client.put(
        f"/v1/files/{TEST_FILE_PATH}", files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)}
    )

    response = client.get(f"/v1/files/{TEST_FILE_PATH}")

    assert response.status_code == status.HTTP_200_OK
    assert response.content == TEST_FILE_CONTENT


def test_delete_file(client: TestClient):
    """Test the delete file route."""
    client.put(
        f"/v1/files/{TEST_FILE_PATH}", files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)}
    )

    response = client.delete(f"/v1/files/{TEST_FILE_PATH}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # My solution to check if the file exists:
    obj_exists = object_exists_in_s3(TEST_BUCKET_NAME, TEST_FILE_PATH)
    print(f"Object exists after deletion: {obj_exists}")
    assert not obj_exists

def test_generate_text_file(client: TestClient):
    """Test the generate file route for generating text."""
    response = client.post(f"/v1/files/generate/text/{TEST_FILE_PATH}", params={"prompt": "A short poem about python"})

    assert response.status_code == status.HTTP_201_CREATED

    # My solution to check if the file exists:
    obj_exists = object_exists_in_s3(TEST_BUCKET_NAME, TEST_FILE_PATH)
    print(f"Object exists after generation: {obj_exists}")
    assert obj_exists