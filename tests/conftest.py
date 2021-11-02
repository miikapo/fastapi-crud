import pytest
from fastapi.testclient import TestClient

from tests.app.app import app


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)
