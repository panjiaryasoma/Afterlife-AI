from datetime import UTC, datetime
from pathlib import Path

from afterlife_ai.pipeline.planning import (
    build_production_planning_lots,
)
from afterlife_ai.pipeline.runtime_config import (
    load_runtime_config,
)
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


def test_production_pipeline_builds_only_planner_eligible_lots() -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    triage = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=analysis_at,
    )

    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    planning_lots = build_production_planning_lots(
        lots=triage.raw_inventory_lots,
        triage_results=triage.triage_results,
        config=config,
    )

    assert [
        item.planning_lot_id
        for item in planning_lots
    ] == [
        "PLAN-LOT-003",
        "PLAN-LOT-006",
    ]

    assert all(
        item.planning_quantity > 0
        for item in planning_lots
    )

    assert {
        item.source_lot_id
        for item in planning_lots
    } == {
        "LOT-003",
        "LOT-006",
    }
