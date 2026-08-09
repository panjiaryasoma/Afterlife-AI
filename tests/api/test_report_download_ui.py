from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_ui_exposes_json_report_download() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert 'id="download-report"' in response.text
    assert "Download JSON Report" in response.text


def test_frontend_javascript_builds_json_download() -> None:
    response = client.get("/static/js/app.js")

    assert response.status_code == 200

    javascript = response.text

    assert "application/json" in javascript
    assert "rescue-decision-report-" in javascript
    assert "URL.createObjectURL" in javascript