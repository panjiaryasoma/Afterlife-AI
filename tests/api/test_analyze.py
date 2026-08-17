from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO
from pathlib import Path

import pytest
from backend.api import routes
from backend.main import app
from fastapi.testclient import TestClient
from openpyxl import load_workbook

from afterlife_ai.contracts.enums import OptimizationObjective
from afterlife_ai.pipeline.application import run_production_pipeline

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
def test_analyze_matches_canonical_pipeline_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixed_analysis_at = datetime(
        2026,
        8,
        17,
        2,
        30,
        tzinfo=UTC,
    )
    fixed_request_id = "REQ-API-PARITY-001"

    class FixedDateTime:
        @staticmethod
        def now(_tz: object = None) -> datetime:
            return fixed_analysis_at

    class FixedUUID:
        hex = "API-PARITY-001"

    monkeypatch.setattr(
        routes,
        "datetime",
        FixedDateTime,
    )
    monkeypatch.setattr(
        routes,
        "uuid4",
        lambda: FixedUUID(),
    )

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

    canonical_result = run_production_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=routes.RUNTIME_CONFIG_PATH,
        partner_registry_path=routes.PARTNER_REGISTRY_PATH,
        analysis_at=fixed_analysis_at,
        request_id=fixed_request_id,
        optimization_objective=(
            OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
        ),
        max_logistics_budget=None,
        minimum_expected_rescue_ratio=None,
        rescue_deadline_at=None,
    )

    assert (
        response.json()
        == canonical_result.report.model_dump(mode="json")
    )

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

def test_analyze_applies_rescue_deadline_before_scoring() -> None:
    with WORKBOOK_PATH.open("rb") as handle:
        response = client.post(
            "/api/analyze",
            data={
                "rescue_deadline_at": (
                    "2020-01-01T00:00:00+00:00"
                ),
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

    assert payload["selected_allocations"] == []

    assert payload["rejected_candidates"]

    assert all(
        "TIMING_INFEASIBLE"
        in item["rejection_reason_codes"]
        for item in payload["rejected_candidates"]
    )

def test_analyze_rejects_naive_rescue_deadline() -> None:
    with WORKBOOK_PATH.open("rb") as handle:
        response = client.post(
            "/api/analyze",
            data={
                "rescue_deadline_at": (
                    "2026-08-20T12:00:00"
                ),
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

    assert "timezone-aware" in str(
        response.json()["detail"]
    )

def test_analyze_rejects_upload_above_size_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        routes,
        "MAX_UPLOAD_SIZE_BYTES",
        8,
    )

    response = client.post(
        "/api/analyze",
        files={
            "inventory_file": (
                "inventory.xlsx",
                BytesIO(b"123456789"),
                XLSX_MIME_TYPE,
            )
        },
    )

    assert response.status_code == 413
    assert "melebihi batas upload" in (
        response.json()["detail"]
    )

def test_analyze_returns_canonical_error_for_invalid_schema(
    tmp_path: Path,
) -> None:
    invalid_workbook_path = (
        tmp_path / "invalid_schema.xlsx"
    )

    workbook = load_workbook(
        WORKBOOK_PATH
    )

    try:
        worksheet = workbook[
            "inventory_lots"
        ]

        headers = [
            cell.value
            for cell in worksheet[1]
        ]

        lot_id_column = (
            headers.index("lot_id") + 1
        )

        worksheet.delete_cols(
            lot_id_column
        )

        workbook.save(
            invalid_workbook_path
        )

    finally:
        workbook.close()

    with invalid_workbook_path.open(
        "rb"
    ) as handle:
        response = client.post(
            "/api/analyze",
            files={
                "inventory_file": (
                    "invalid_schema.xlsx",
                    handle,
                    XLSX_MIME_TYPE,
                )
            },
        )

    assert response.status_code == 422

    assert response.headers[
        "content-type"
    ].startswith(
        "application/json"
    )

    detail = response.json()["detail"]

    assert "lot_id" in detail

def test_analyze_cleanup_does_not_mask_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_unlink = Path.unlink

    def locked_unlink(
        path: Path,
        missing_ok: bool = False,
    ) -> None:
        if path.suffix == ".xlsx":
            raise PermissionError(
                32,
                "file is being used by another process",
            )

        original_unlink(
            path,
            missing_ok=missing_ok,
        )

    monkeypatch.setattr(
        Path,
        "unlink",
        locked_unlink,
    )

    monkeypatch.setattr(
        routes,
        "run_production_pipeline",
        lambda **_: (_ for _ in ()).throw(
            ValueError(
                "Kolom wajib tidak ditemukan: lot_id"
            )
        ),
    )

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

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "XLSX tidak valid: "
        "Kolom wajib tidak ditemukan: lot_id"
    )