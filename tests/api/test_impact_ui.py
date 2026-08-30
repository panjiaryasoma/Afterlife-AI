from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_loads_nextstep_impact_ui_script() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert '/static/js/impact-ui.js' in response.text


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
