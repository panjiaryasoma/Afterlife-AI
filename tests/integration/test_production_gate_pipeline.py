from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from afterlife_ai.contracts.enums import (
    FeasibilityStatus,
    ModelScoringStatus,
    ValidationStatus,
)
from afterlife_ai.pipeline.candidates import (
    generate_production_candidates,
)
from afterlife_ai.pipeline.gates import (
    apply_production_hard_gates,
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


def test_production_hard_gates_allow_only_feasible_candidates() -> None:
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

    assert len(gated) == 5

    assert all(
        candidate.validation_status
        is ValidationStatus.PASSED
        for candidate in gated
    )

    assert all(
        candidate.feasibility_status
        is FeasibilityStatus.FEASIBLE
        for candidate in gated
    )

    assert all(
        candidate.model_scoring_status
        is ModelScoringStatus.DEFERRED
        for candidate in gated
    )

    assert all(
        candidate.rejection_reason_codes == []
        for candidate in gated
    )

def test_production_hard_gates_reject_candidates_that_miss_request_deadline() -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    rescue_deadline_at = (
        analysis_at
        + timedelta(hours=1)
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
        rescue_deadline_at=rescue_deadline_at,
    )

    assert gated

    assert any(
        candidate.feasibility_status
        is FeasibilityStatus.FEASIBLE
        for candidate in gated
    )

    assert any(
        candidate.feasibility_status
        is FeasibilityStatus.INFEASIBLE
        for candidate in gated
    )

    for candidate in gated:
        completion = (
            candidate.estimated_completion_hours
        )

        assert completion is not None

        if completion <= Decimal("1"):
            assert (
                candidate.feasibility_status
                is FeasibilityStatus.FEASIBLE
            )

            assert (
                "TIMING_INFEASIBLE"
                not in candidate.rejection_reason_codes
            )
        else:
            assert (
                candidate.feasibility_status
                is FeasibilityStatus.INFEASIBLE
            )

            assert (
                candidate.model_scoring_status
                is ModelScoringStatus.BLOCKED
            )

            assert (
                "TIMING_INFEASIBLE"
                in candidate.rejection_reason_codes
            )

def test_production_hard_gates_reject_all_candidates_when_request_deadline_is_expired() -> None:
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
        rescue_deadline_at=analysis_at,
    )

    assert gated

    assert all(
        candidate.feasibility_status
        is FeasibilityStatus.INFEASIBLE
        for candidate in gated
    )

    assert all(
        candidate.model_scoring_status
        is ModelScoringStatus.BLOCKED
        for candidate in gated
    )

    assert all(
        "TIMING_INFEASIBLE"
        in candidate.rejection_reason_codes
        for candidate in gated
    )