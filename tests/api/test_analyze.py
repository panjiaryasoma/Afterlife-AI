from decimal import Decimal
from pathlib import Path

from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

FIXTURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integration_001"
)

WORKBOOK_PATH = FIXTURE_DIR / "RAW_INVENTORY_FIXTURE.xlsx"


def test_analyze_accepts_one_xlsx_and_returns_report() -> None:
    with WORKBOOK_PATH.open("rb") as handle:
        response = client.post(
            "/api/analyze",
            files={
                "inventory_file": (
                    "inventory.xlsx",
                    handle,
                    (
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                )
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["feature_schema_version"] == "2.0.0"
    assert payload["execution_performed"] is False

    metrics = payload["batch_metrics"]

    assert metrics["input_lots"] == 6

    planning_quantity = Decimal(
        metrics["planning_quantity"]
    )
    allocated_quantity = Decimal(
        metrics["allocated_planning_quantity"]
    )
    unallocated_quantity = Decimal(
        metrics["unallocated_planning_quantity"]
    )

    assert planning_quantity > Decimal("0")

    assert (
        allocated_quantity
        + unallocated_quantity
        == planning_quantity
    )

    assert payload["score_provenance"]["provider_name"] in {
        "M1_HIST_GRADIENT_BOOSTING",
        "DETERMINISTIC_FALLBACK_V1",
    }