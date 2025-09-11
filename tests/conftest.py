import pytest
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app instance

@pytest.fixture(scope="module")
def client():
    """
    Pytest fixture to create a TestClient for the FastAPI app.
    """
    with TestClient(app) as c:
        yield c