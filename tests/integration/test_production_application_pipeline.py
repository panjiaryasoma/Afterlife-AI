from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from pytest import MonkeyPatch

from afterlife_ai.contracts.enums import (
    ApprovalStatus,
    OptimizationObjective,
    SolverStatus,
)
from afterlife_ai.pipeline.application import (
    run_production_pipeline,
)
from afterlife_ai.planner.optimizer import OptimizationResult

FIXTURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integration_001"
)

WORKBOOK_PATH = FIXTURE_DIR / "RAW_INVENTORY_FIXTURE.xlsx"
RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")


def test_one_xlsx_runs_to_rescue_decision_report() -> None:
    result = run_production_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=datetime(
            2026,
            8,
            5,
            tzinfo=UTC,
        ),
        request_id="PRODUCTION-TEST-001",
    )

    report = result.report

    assert len(result.raw_inventory_lots) == 6
    assert len(result.planning_lots) == 2
    assert len(result.valued_candidates) == 5

    assert result.optimization_result.solver_status in {
        SolverStatus.OPTIMAL,
        SolverStatus.FEASIBLE,
    }

    assert (
        report.optimization_solver_status
        is result.optimization_result.solver_status
    )

    assert report.request_id == "PRODUCTION-TEST-001"
    assert report.feature_schema_version == "2.0.0"

    assert (
        report.optimization_objective
        is OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
    )

    assert (
        report.human_final_approval_status
        is ApprovalStatus.PENDING
    )

    assert report.execution_performed is False

    metrics = report.batch_metrics

    assert (
        metrics.allocated_planning_quantity
        + metrics.unallocated_planning_quantity
        == metrics.planning_quantity
    )

    routed = (
        metrics.protected_quantity
        + metrics.monitor_quantity
        + metrics.planning_quantity
        + metrics.expired_quantity
        + metrics.review_quantity
    )

    assert routed == metrics.input_quantity

    selected_total = sum(
        (
            item.allocated_quantity
            for item in report.selected_allocations
        ),
        Decimal("0"),
    )

    assert (
        selected_total
        == metrics.allocated_planning_quantity
    )

    selected_candidate_ids = {
        item.candidate_id
        for item in report.selected_allocations
    }

    reported_alternative_ids = {
        item.candidate_id
        for item in report.rejected_candidates
    }

    valued_candidate_ids = {
        candidate.candidate_id
        for candidate in result.valued_candidates
    }

    assert (
        selected_candidate_ids
        | reported_alternative_ids
        == valued_candidate_ids
    )

    assert (
        selected_candidate_ids
        & reported_alternative_ids
        == set()
    )

    candidate_by_id = {
        candidate.candidate_id: candidate
        for candidate in result.valued_candidates
    }

    for item in report.rejected_candidates:
        candidate = candidate_by_id[item.candidate_id]

        if candidate.rejection_reason_codes:
            assert (
                item.rejection_reason_codes
                == candidate.rejection_reason_codes
            )
        else:
            assert item.rejection_reason_codes == [
                "OPTIMIZER_NOT_SELECTED"
            ]

    assert report.score_provenance.provider_name in {
        "M1_HIST_GRADIENT_BOOSTING",
        "DETERMINISTIC_FALLBACK_V1",
    }

    if (
        report.score_provenance.provider_name
        == "M1_HIST_GRADIENT_BOOSTING"
    ):
        assert report.model_execution_performed is True
    else:
        assert report.model_execution_performed is False


def test_infeasible_optimizer_is_explicit_in_rescue_report(
    monkeypatch: MonkeyPatch,
) -> None:
    def fake_optimizer(
        *,
        candidates: object,
        planning_lots: object,
        config: object,
    ) -> OptimizationResult:
        del candidates, config

        planning_quantities = {
            lot.planning_lot_id: lot.planning_quantity
            for lot in planning_lots
        }

        return OptimizationResult(
            solver_status=SolverStatus.INFEASIBLE,
            objective_value=Decimal("0"),
            allocations=[],
            unallocated_quantities=planning_quantities,
        )

    monkeypatch.setattr(
        (
            "afterlife_ai.pipeline.application."
            "optimize_production_candidates"
        ),
        fake_optimizer,
    )

    result = run_production_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=datetime(
            2026,
            8,
            5,
            tzinfo=UTC,
        ),
        request_id="PRODUCTION-INFEASIBLE-TEST",
    )

    report = result.report

    assert (
        result.optimization_result.solver_status
        is SolverStatus.INFEASIBLE
    )

    assert (
        report.optimization_solver_status
        is SolverStatus.INFEASIBLE
    )

    assert report.selected_allocations == []

    assert (
        report.batch_metrics.allocated_planning_quantity
        == Decimal("0")
    )

    assert (
        report.batch_metrics.unallocated_planning_quantity
        == report.batch_metrics.planning_quantity
    )

    assert report.rejected_candidates

    assert all(
        item.rejection_reason_codes
        == ["OPTIMIZER_INFEASIBLE"]
        for item in report.rejected_candidates
    )

    assert any(
        "no feasible allocation" in limitation.lower()
        for limitation in report.limitations
    )

    assert (
        report.human_exception_review_required
        is True
    )