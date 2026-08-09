from datetime import UTC, datetime
from pathlib import Path

from afterlife_ai.contracts.enums import InventoryStatus
from afterlife_ai.pipeline.triage_pipeline import (
    run_triage_pipeline,
)

FIXTURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integration_001"
)

WORKBOOK_PATH = FIXTURE_DIR / "RAW_INVENTORY_FIXTURE.xlsx"

RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")


def test_production_pipeline_reads_xlsx_and_runs_triage() -> None:
    result = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=datetime(
            2026,
            8,
            5,
            tzinfo=UTC,
        ),
    )

    assert len(result.raw_inventory_lots) == 6
    assert len(result.canonical_inventory_records) == 6
    assert len(result.triage_results) == 6

    statuses = {
        item.source_lot_id: item.inventory_status
        for item in result.triage_results
    }

    assert statuses == {
        "LOT-001": InventoryStatus.HEALTHY_STOCK,
        "LOT-002": InventoryStatus.MONITOR,
        "LOT-003": InventoryStatus.SURPLUS_CANDIDATE,
        "LOT-004": InventoryStatus.EXPIRED,
        "LOT-005": InventoryStatus.NEEDS_REVIEW,
        "LOT-006": InventoryStatus.SURPLUS_CANDIDATE,
    }