"""Set up api test client fixture for tests."""

import pytest
from fastapi.testclient import TestClient

from files_api.settings import Settings
from src.files_api.main import create_app
from tests.consts import TEST_BUCKET_NAME


# Fixture for FastAPI test client
@pytest.fixture
def client(mocked_aws) -> TestClient:  # type: ignore # pylint: disable=unused-argument
    """Create standard api test client for tests."""
    settings = Settings(s3_bucket_name=TEST_BUCKET_NAME)
    app = create_app(settings=settings)
    with TestClient(app) as client:
        yield client
