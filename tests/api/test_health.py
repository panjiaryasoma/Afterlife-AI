from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_is_available() -> None:
    response = client.get("/")

    assert response.status_code == 200


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "afterlife-ai",
    }
