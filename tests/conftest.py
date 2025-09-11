import pytest, os, sys
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app instance

# Add the project's root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="module")
def client():
    """
    Pytest fixture to create a TestClient for the FastAPI app.
    """
    with TestClient(app) as c:
        yield c