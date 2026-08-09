from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_renders_upload_interface() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    html = response.text

    assert 'id="analysis-form"' in html
    assert 'name="inventory_file"' in html
    assert "/static/css/app.css" in html
    assert "/static/js/app.js" in html
    assert "Analyze Inventory" in html