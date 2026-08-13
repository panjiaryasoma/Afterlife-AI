from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_demo_ui_exposes_production_decision_controls() -> None:
    response = client.get("/")

    assert response.status_code == 200

    html = response.text

    assert 'name="inventory_file"' in html
    assert 'name="optimization_objective"' in html
    assert 'name="max_logistics_budget"' in html
    assert 'name="minimum_expected_rescue_ratio"' in html
    assert 'name="rescue_deadline_at"' in html


def test_demo_ui_exposes_explainability_sections() -> None:
    response = client.get("/")

    assert response.status_code == 200

    html = response.text

    assert 'id="metrics"' in html
    assert 'id="allocations"' in html
    assert 'id="rejected-candidates"' in html
    assert 'id="review-banner"' in html
    assert 'id="provenance"' in html
    assert 'id="limitations"' in html
    assert 'id="download-report"' in html


def test_demo_javascript_forwards_decision_context() -> None:
    response = client.get("/static/js/app.js")

    assert response.status_code == 200

    javascript = response.text

    assert 'data.append("optimization_objective"' in javascript
    assert 'data.append("max_logistics_budget"' in javascript
    assert (
        'data.append("minimum_expected_rescue_ratio"'
        in javascript
    )
    assert 'data.append("rescue_deadline_at"' in javascript


def test_demo_javascript_renders_explainability() -> None:
    response = client.get("/static/js/app.js")

    assert response.status_code == 200

    javascript = response.text

    required_fields = [
        "expected_physical_rescue_quantity",
        "expected_waste_quantity",
        "expected_rescue_ratio",
        "destination_id",
        "estimated_rescue_success_score",
        "binding_constraint_codes",
        "rejected_candidates",
        "partner_registry_snapshot_id",
        "partner_registry_source_type",
        "partner_registry_real_world_verified",
        "human_exception_review_required",
        "deterministic_execution",
    ]

    for field in required_fields:
        assert field in javascript
