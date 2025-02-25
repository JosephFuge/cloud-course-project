import pytest
from fastapi.testclient import TestClient
from src.files_api.main import APP


# Fixture for FastAPI test client
@pytest.fixture
def client(mocked_aws) -> TestClient:  # pylint: disable=unused-argument
    with TestClient(APP) as client:
        yield client


def test_upload_file(client: TestClient): ...


def test_list_files_with_pagination(client: TestClient): ...


def test_get_file_metadata(client: TestClient): ...


def test_get_file(client: TestClient): ...


def test_delete_file(client: TestClient): ...
