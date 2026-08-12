from decimal import Decimal
from io import BytesIO
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
XLSX_MIME_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)


def test_analyze_accepts_one_xlsx_and_returns_report() -> None:
    with WORKBOOK_PATH.open("rb") as handle:
        response = client.post(
            "/api/analyze",
            files={
                "inventory_file": (
                    "inventory.xlsx",
                    handle,
                    XLSX_MIME_TYPE,
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

def test_analyze_rejects_missing_inventory_file() -> None:
    response = client.post(
        "/api/analyze",
        files={},
    )

    assert response.status_code == 422

    payload = response.json()

    assert payload["detail"][0]["type"] == "missing"
    assert payload["detail"][0]["loc"] == [
        "body",
        "inventory_file",
    ]


def test_analyze_rejects_non_xlsx_file() -> None:
    response = client.post(
        "/api/analyze",
        files={
            "inventory_file": (
                "inventory.csv",
                BytesIO(b"a,b\n1,2"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "inventory_file harus berupa file .xlsx."
    )


def test_analyze_rejects_empty_xlsx() -> None:
    response = client.post(
        "/api/analyze",
        files={
            "inventory_file": (
                "inventory.xlsx",
                BytesIO(b""),
                XLSX_MIME_TYPE,
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "inventory_file tidak boleh kosong."
    )


def test_analyze_rejects_corrupt_xlsx() -> None:
    response = client.post(
        "/api/analyze",
        files={
            "inventory_file": (
                "inventory.xlsx",
                BytesIO(b"this is not a real xlsx"),
                XLSX_MIME_TYPE,
            )
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "XLSX tidak valid atau rusak."
    )

def test_analyze_accepts_dynamic_optimizer_request_context() -> None:
    with WORKBOOK_PATH.open("rb") as handle:
        response = client.post(
            "/api/analyze",
            data={
                "optimization_objective": "BALANCED",
                "max_logistics_budget": "30000",
                "minimum_expected_rescue_ratio": "0.50",
            },
            files={
                "inventory_file": (
                    "inventory.xlsx",
                    handle,
                    XLSX_MIME_TYPE,
                )
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["optimization_objective"]
        == "BALANCED"
    )   

def test_analyze_rejects_balanced_without_minimum_rescue_ratio() -> None:
    with WORKBOOK_PATH.open("rb") as handle:
        response = client.post(
            "/api/analyze",
            data={
                "optimization_objective": "BALANCED",
            },
            files={
                "inventory_file": (
                    "inventory.xlsx",
                    handle,
                    XLSX_MIME_TYPE,
                )
            },
        )

    assert response.status_code == 422

    payload = response.json()

    assert any(
        "minimum_expected_rescue_ratio"
        in str(error)
        for error in payload["detail"]
    )