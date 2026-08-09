from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from afterlife_ai.contracts.enums import (
    ActionType,
    SolverStatus,
)
from afterlife_ai.pipeline.candidates import (
    generate_production_candidates,
)
from afterlife_ai.pipeline.gates import (
    apply_production_hard_gates,
)
from afterlife_ai.pipeline.optimizer import (
    optimize_production_candidates,
)
from afterlife_ai.pipeline.planning import (
    build_production_planning_lots,
)
from afterlife_ai.pipeline.runtime_config import (
    load_runtime_config,
)
from afterlife_ai.pipeline.scoring import (
    score_production_candidates,
)
from afterlife_ai.pipeline.triage_pipeline import (
    run_triage_pipeline,
)
from afterlife_ai.pipeline.value import (
    apply_production_expected_values,
)

FIXTURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integration_001"
)

WORKBOOK_PATH = FIXTURE_DIR / "RAW_INVENTORY_FIXTURE.xlsx"
RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")


def test_production_optimizer_enforces_shared_capacity_and_quantity() -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    triage = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=analysis_at,
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

    gated = apply_production_hard_gates(
        candidates=candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=triage.raw_inventory_lots,
        config=config,
        analysis_at=analysis_at,
    )

    scored = score_production_candidates(
        candidates=gated,
        planning_lots=planning_lots,
        config=config,
    )

    valued = apply_production_expected_values(
        candidates=scored,
    )

    result = optimize_production_candidates(
        candidates=valued,
        planning_lots=planning_lots,
        config=config,
    )

    assert result.solver_status in {
        SolverStatus.OPTIMAL,
        SolverStatus.FEASIBLE,
    }

    planning_quantities = {
        lot.planning_lot_id: lot.planning_quantity
        for lot in planning_lots
    }

    allocated_by_lot = defaultdict(
        lambda: Decimal("0")
    )

    repurpose_quantity = Decimal("0")

    for allocation in result.allocations:
        allocated_by_lot[
            allocation.planning_lot_id
        ] += allocation.allocated_quantity

        if (
            allocation.action_type
            is ActionType.INTERNAL_REPURPOSE
        ):
            repurpose_quantity += (
                allocation.allocated_quantity
            )

    assert repurpose_quantity <= Decimal("6")

    for planning_lot_id, quantity in (
        planning_quantities.items()
    ):
        assert (
            allocated_by_lot[planning_lot_id]
            + result.unallocated_quantities[
                planning_lot_id
            ]
            == quantity
        )
