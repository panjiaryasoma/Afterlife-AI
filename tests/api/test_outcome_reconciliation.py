from decimal import Decimal

from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _decimal(value: object) -> Decimal:
    return Decimal(str(value))


def test_reconcile_outcome_returns_realized_impact() -> None:
    response = client.post(
        "/api/outcomes/reconcile",
        json={
            "request_id": "REQ-NEXTSTEP-001",
            "observation": {
                "reconciled_quantity": "100",
                "actual_rescued_quantity": "60",
                "actual_waste_quantity": "20",
            },
            "expected_rescue_quantity": "80",
            "expected_waste_quantity": "20",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    result = payload["reconciliation"]

    assert payload["request_id"] == "REQ-NEXTSTEP-001"
    assert _decimal(result["unresolved_quantity"]) == Decimal("20")
    assert _decimal(result["realized_diversion_ratio"]) == Decimal("0.75")
    assert _decimal(result["rescue_quantity_delta"]) == Decimal("-20")
    assert _decimal(result["waste_quantity_delta"]) == Decimal("0")


def test_reconcile_outcome_rejects_confirmed_quantity_above_scope() -> None:
    response = client.post(
        "/api/outcomes/reconcile",
        json={
            "request_id": "REQ-NEXTSTEP-002",
            "observation": {
                "reconciled_quantity": "100",
                "actual_rescued_quantity": "90",
                "actual_waste_quantity": "20",
            },
            "expected_rescue_quantity": "80",
            "expected_waste_quantity": "20",
        },
    )

    assert response.status_code == 422


def test_reconcile_outcome_rejects_expected_quantity_scope_mismatch() -> None:
    response = client.post(
        "/api/outcomes/reconcile",
        json={
            "request_id": "REQ-NEXTSTEP-003",
            "observation": {
                "reconciled_quantity": "100",
                "actual_rescued_quantity": "60",
                "actual_waste_quantity": "20",
            },
            "expected_rescue_quantity": "70",
            "expected_waste_quantity": "20",
        },
    )

    assert response.status_code == 422


def test_reconcile_outcome_with_no_confirmed_outcome_has_no_realized_ratio() -> None:
    response = client.post(
        "/api/outcomes/reconcile",
        json={
            "request_id": "REQ-NEXTSTEP-004",
            "observation": {
                "reconciled_quantity": "100",
                "actual_rescued_quantity": "0",
                "actual_waste_quantity": "0",
            },
            "expected_rescue_quantity": "80",
            "expected_waste_quantity": "20",
        },
    )

    assert response.status_code == 200

    result = response.json()["reconciliation"]

    assert _decimal(result["unresolved_quantity"]) == Decimal("100")
    assert result["realized_diversion_ratio"] is None


def test_reconcile_outcome_is_stateless_and_does_not_claim_persistence() -> None:
    payload = {
        "request_id": "REQ-NEXTSTEP-005",
        "observation": {
            "reconciled_quantity": "50",
            "actual_rescued_quantity": "30",
            "actual_waste_quantity": "10",
        },
        "expected_rescue_quantity": "40",
        "expected_waste_quantity": "10",
    }

    first = client.post("/api/outcomes/reconcile", json=payload)
    second = client.post("/api/outcomes/reconcile", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert "stored" not in first.json()
    assert "persisted" not in first.json()
