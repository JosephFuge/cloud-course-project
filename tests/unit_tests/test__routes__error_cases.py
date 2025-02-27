from fastapi import status
from fastapi.testclient import TestClient


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
