from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_ui_exposes_report_download_control() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert 'id="download-report"' in response.text


def test_impact_ui_loads_markdown_report_exporter_and_tracks_nextstep_state() -> None:
    response = client.get("/static/js/impact-ui.js")

    assert response.status_code == 200

    javascript = response.text

    assert "/static/js/report-markdown.js" in javascript
    assert "AfterlifeReportExportState" in javascript
    assert "sustainabilitySummary" in javascript
    assert "payload.reconciliation" in javascript


def test_markdown_exporter_builds_human_readable_report() -> None:
    response = client.get("/static/js/report-markdown.js")

    assert response.status_code == 200

    javascript = response.text

    assert "Download Markdown Report" in javascript
    assert 'type: "text/markdown;charset=utf-8"' in javascript
    assert "afterlife-ai-rescue-report-" in javascript
    assert ".md`" in javascript
    assert "# Afterlife AI — Rescue Decision Report" in javascript
    assert "## Decision Summary" in javascript
    assert "## Sustainability Impact" in javascript
    assert "## Selected Rescue Plan" in javascript
    assert "## Outcome Reconciliation" in javascript
    assert "## Human Review" in javascript
    assert "## Evidence & Provenance" in javascript
    assert "## Limitations" in javascript
    assert "URL.createObjectURL" in javascript


def test_markdown_export_preserves_expected_vs_realized_claim_boundary() -> None:
    response = client.get("/static/js/report-markdown.js")

    assert response.status_code == 200

    javascript = response.text

    assert "Expected impact is model/plan-derived" in javascript
    assert "No operator-confirmed outcome has been reconciled" in javascript
    assert "confirmed outcomes only" in javascript
    assert "Unresolved quantity is excluded" in javascript
    assert "not persisted by this demo" in javascript
