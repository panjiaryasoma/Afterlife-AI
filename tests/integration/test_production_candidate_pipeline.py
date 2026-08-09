from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from afterlife_ai.contracts.enums import ActionType
from afterlife_ai.pipeline.candidates import (
    generate_production_candidates,
)
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


def test_production_candidate_generation_uses_runtime_capabilities() -> None:
    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    triage = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=datetime(
            2026,
            8,
            5,
            tzinfo=UTC,
        ),
    )

    planning_lots = build_production_planning_lots(
        lots=triage.raw_inventory_lots,
        triage_results=triage.triage_results,
        config=config,
    )

    candidates = generate_production_candidates(
        planning_lots=planning_lots,
        config=config,
    )

    assert [
        candidate.candidate_id
        for candidate in candidates
    ] == [
        "CAND-003-REPURPOSE",
        "CAND-003-BUNDLE",
        "CAND-003-DISCOUNT",
        "CAND-006-REPURPOSE",
        "CAND-006-DISCOUNT",
    ]

    by_id = {
        candidate.candidate_id: candidate
        for candidate in candidates
    }

    assert (
        by_id["CAND-003-REPURPOSE"].action_type
        is ActionType.INTERNAL_REPURPOSE
    )
    assert (
        by_id["CAND-003-REPURPOSE"].maximum_feasible_quantity
        == Decimal("6")
    )
    assert (
        by_id["CAND-003-REPURPOSE"]
        .offered_or_selling_price_per_unit
        == Decimal("3500")
    )

    assert (
        by_id["CAND-003-BUNDLE"].maximum_feasible_quantity
        == Decimal("4")
    )
    assert (
        by_id["CAND-003-BUNDLE"]
        .offered_or_selling_price_per_unit
        == Decimal("1600")
    )

    assert (
        by_id["CAND-003-DISCOUNT"]
        .offered_or_selling_price_per_unit
        == Decimal("1500")
    )

    assert (
        by_id["CAND-006-DISCOUNT"]
        .offered_or_selling_price_per_unit
        == Decimal("1500")
    )

    assert all(
        candidate.action_type
        is not ActionType.SAFE_DISPOSAL
        for candidate in candidates
    )
