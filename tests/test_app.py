from fastapi.testclient import TestClient


def test_index(test_client: TestClient):
    r = test_client.get("/")
    assert r.status_code == 200
    assert r.json() == {"status": "OK"}


def test_read_companies_empty(test_client: TestClient):
    r = test_client.get("/companies")
    assert r.status_code == 200
    assert r.json() == {"data": []}
