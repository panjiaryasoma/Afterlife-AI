from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_loads_nextstep_analysis_and_impact_scripts() -> None:
    response = client.get("/")

    assert response.status_code == 200

    html = response.text

    assert '/static/js/app.js' in html
    assert '/static/js/nextstep-analysis.js' in html
    assert '/static/js/impact-ui.js' in html
    assert html.index('/static/js/app.js') < html.index(
        '/static/js/nextstep-analysis.js'
    )
    assert html.index('/static/js/nextstep-analysis.js') < html.index(
        '/static/js/impact-ui.js'
    )


def test_nextstep_web_adapter_calls_impact_aware_analysis_endpoint() -> None:
    response = client.get("/static/js/nextstep-analysis.js")

    assert response.status_code == 200

    javascript = response.text

    assert 'fetch("/api/analyze-nextstep"' in javascript
    assert "rescue_decision_report" in javascript
    assert "sustainability_summary" in javascript
    assert "afterlife:nextstep-report" in javascript
    assert "afterlife:nextstep-clear" in javascript


def test_impact_ui_avoids_global_event_constant_collision() -> None:
    nextstep_response = client.get("/static/js/nextstep-analysis.js")
    impact_response = client.get("/static/js/impact-ui.js")

    assert nextstep_response.status_code == 200
    assert impact_response.status_code == 200

    nextstep_javascript = nextstep_response.text
    impact_javascript = impact_response.text

    assert "const NEXTSTEP_REPORT_EVENT" in nextstep_javascript
    assert "const NEXTSTEP_CLEAR_EVENT" in nextstep_javascript
    assert "const NEXTSTEP_REPORT_EVENT" not in impact_javascript
    assert "const NEXTSTEP_CLEAR_EVENT" not in impact_javascript
    assert "const IMPACT_NEXTSTEP_REPORT_EVENT" in impact_javascript
    assert "const IMPACT_NEXTSTEP_CLEAR_EVENT" in impact_javascript


def test_impact_ui_consumes_typed_sustainability_summary() -> None:
    response = client.get("/static/js/impact-ui.js")

    assert response.status_code == 200

    javascript = response.text

    required_fields = [
        "reconciled_quantity",
        "expected_rescue_quantity",
        "expected_waste_quantity",
        "expected_rescue_ratio",
        "mass_evidence_coverage",
        "expected_rescue_mass_kg",
        "expected_waste_mass_kg",
    ]

    for field in required_fields:
        assert field in javascript

    assert "metricValueByLabel" not in javascript
    assert "parseRenderedNumber" not in javascript


def test_impact_ui_uses_editorial_layout_instead_of_metric_card_grid() -> None:
    javascript_response = client.get("/static/js/impact-ui.js")
    stylesheet_response = client.get("/static/css/impact.css")

    assert javascript_response.status_code == 200
    assert stylesheet_response.status_code == 200

    javascript = javascript_response.text
    stylesheet = stylesheet_response.text

    assert 'class="metric-grid"' not in javascript
    assert 'class="analysis-form"' not in javascript
    assert "impact-overview" in javascript
    assert "impact-ledger" in javascript
    assert "impact-entry" in javascript
    assert "impact-comparison" in javascript
    assert "/static/css/impact.css" in javascript
    assert ".impact-overview__value" in stylesheet
    assert 'font-family: Georgia, "Times New Roman", serif;' in stylesheet
    assert ".impact-field input" in stylesheet
    assert "border-radius: 0;" in stylesheet


def test_impact_ui_exposes_operator_confirmed_outcome_controls() -> None:
    response = client.get("/static/js/impact-ui.js")

    assert response.status_code == 200

    javascript = response.text

    assert "Actual rescued quantity" in javascript
    assert "Actual waste quantity" in javascript
    assert "Unresolved" in javascript
    assert "Realized diversion ratio" in javascript
    assert "Rescue delta" in javascript
    assert "Waste delta" in javascript


def test_impact_ui_calls_stateless_reconciliation_endpoint() -> None:
    response = client.get("/static/js/impact-ui.js")

    assert response.status_code == 200

    javascript = response.text

    assert 'fetch("/api/outcomes/reconcile"' in javascript
    assert "request_id" in javascript
    assert "expected_rescue_quantity" in javascript
    assert "expected_waste_quantity" in javascript
    assert "actual_rescued_quantity" in javascript
    assert "actual_waste_quantity" in javascript


def test_impact_ui_preserves_expected_vs_realized_claim_boundary() -> None:
    response = client.get("/static/js/impact-ui.js")

    assert response.status_code == 200

    javascript = response.text

    assert "EXPECTED RESCUE" in javascript
    assert "REALIZED OUTCOME" in javascript
    assert "Planned impact is model-derived" in javascript
    assert "Actual impact is entered by" in javascript
    assert "operator-confirmed" in javascript
    assert "not persisted by this demo" in javascript
    assert "Mass evidence" in javascript
    assert "Full-batch mass is withheld" in javascript
