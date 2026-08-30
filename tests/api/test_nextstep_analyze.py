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
XLSX_MIME_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)


def _post(path: str):
    with WORKBOOK_PATH.open("rb") as handle:
        return client.post(
            path,
            files={
                "inventory_file": (
                    "inventory.xlsx",
                    handle,
                    XLSX_MIME_TYPE,
                )
            },
        )


def test_nextstep_analyze_returns_canonical_report_and_sustainability() -> None:
    response = _post("/api/analyze-nextstep")

    assert response.status_code == 200

    payload = response.json()
    report = payload["rescue_decision_report"]
    summary = payload["sustainability_summary"]
    metrics = report["batch_metrics"]

    assert report["execution_performed"] is False
    assert (
        Decimal(summary["reconciled_quantity"])
        == Decimal(metrics["planning_quantity"])
    )
    assert (
        Decimal(summary["expected_rescue_quantity"])
        == Decimal(metrics["expected_physical_rescue_quantity"])
    )
    assert (
        Decimal(summary["expected_waste_quantity"])
        == Decimal(metrics["expected_waste_quantity"])
    )
    assert summary["mass_evidence_coverage"] in {
        "COMPLETE",
        "PARTIAL",
        "NONE",
    }


def test_legacy_analyze_contract_remains_direct_rescue_report() -> None:
    response = _post("/api/analyze")

    assert response.status_code == 200

    payload = response.json()

    assert "batch_metrics" in payload
    assert "rescue_decision_report" not in payload
    assert "sustainability_summary" not in payload


def test_nextstep_analyze_rejects_non_xlsx() -> None:
    response = client.post(
        "/api/analyze-nextstep",
        files={
            "inventory_file": (
                "inventory.txt",
                b"not an xlsx",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "inventory_file harus berupa file .xlsx."
    )


def test_nextstep_analyze_rejects_empty_xlsx() -> None:
    response = client.post(
        "/api/analyze-nextstep",
        files={
            "inventory_file": (
                "inventory.xlsx",
                b"",
                XLSX_MIME_TYPE,
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "inventory_file tidak boleh kosong."
    )
