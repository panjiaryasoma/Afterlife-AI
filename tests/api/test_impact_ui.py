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

    assert "EXPECTED IMPACT" in javascript
    assert "REALIZED OUTCOME" in javascript
    assert "Model/plan estimate" in javascript
    assert "Operator-confirmed quantity" in javascript
    assert "not persisted by this demo" in javascript
    assert "Mass evidence" in javascript
    assert "Full-batch mass withheld" in javascript
