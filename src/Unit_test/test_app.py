import pytest
from fastapi.testclient import TestClient
from main import app  # Adjust as necessary

@pytest.fixture(scope="function")
def app_test():
    yield app

def test_app_functionality(app_test):
    client = TestClient(app_test)
    response = client.get("/")
    assert response.status_code == 200  # Adjust the URL and status code as necessary
