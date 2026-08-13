from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from pytest import MonkeyPatch

import afterlife_ai.pipeline.application as application_module
from afterlife_ai.contracts.enums import (
    ActionType,
    ApprovalStatus,
    FeasibilityStatus,
    ModelScoringStatus,
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
        **_: object,
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


def test_production_pipeline_forwards_dynamic_optimizer_request_context(
    monkeypatch: MonkeyPatch,
) -> None:
    captured_kwargs: dict[str, Any] = {}

    real_optimizer = (
        application_module.optimize_production_candidates
    )

    def spy_optimizer(
        **kwargs: Any,
    ) -> OptimizationResult:
        captured_kwargs.update(kwargs)
        return real_optimizer(**kwargs)

    monkeypatch.setattr(
        application_module,
        "optimize_production_candidates",
        spy_optimizer,
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
        request_id="PRODUCTION-CONTEXT-001",
        optimization_objective=(
            OptimizationObjective.BALANCED
        ),
        max_logistics_budget=Decimal("30000"),
        minimum_expected_rescue_ratio=(
            Decimal("0.50")
        ),
    )

    assert (
        captured_kwargs["optimization_objective"]
        is OptimizationObjective.BALANCED
    )

    assert (
        captured_kwargs["max_logistics_budget"]
        == Decimal("30000")
    )

    assert (
        captured_kwargs[
            "minimum_expected_rescue_ratio"
        ]
        == Decimal("0.50")
    )

    assert (
        result.report.optimization_objective
        is OptimizationObjective.BALANCED
    )

def test_production_pipeline_forwards_rescue_deadline_to_hard_gates(
    monkeypatch: MonkeyPatch,
) -> None:
    captured_kwargs: dict[str, Any] = {}

    real_hard_gates = (
        application_module.apply_production_hard_gates
    )

    def spy_hard_gates(
        **kwargs: Any,
    ) -> Any:
        captured_kwargs.update(kwargs)
        return real_hard_gates(**kwargs)

    monkeypatch.setattr(
        application_module,
        "apply_production_hard_gates",
        spy_hard_gates,
    )

    rescue_deadline_at = datetime(
        2026,
        8,
        6,
        tzinfo=UTC,
    )

    run_production_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=datetime(
            2026,
            8,
            5,
            tzinfo=UTC,
        ),
        request_id="PRODUCTION-DEADLINE-001",
        rescue_deadline_at=rescue_deadline_at,
    )

    assert (
        captured_kwargs["rescue_deadline_at"]
        == rescue_deadline_at
    )


def test_production_pipeline_adds_safe_disposal_second_pass_when_rescue_is_blocked(
    monkeypatch: MonkeyPatch,
) -> None:
    gate_calls: list[list[Any]] = []

    real_hard_gates = (
        application_module.apply_production_hard_gates
    )

    def controlled_hard_gates(
        **kwargs: Any,
    ) -> Any:
        candidates = kwargs["candidates"]

        gate_calls.append(list(candidates))

        if len(gate_calls) == 1:
            return [
                candidate.model_copy(
                    update={
                        "feasibility_status": (
                            FeasibilityStatus.INFEASIBLE
                        ),
                        "model_scoring_status": (
                            ModelScoringStatus.BLOCKED
                        ),
                        "rejection_reason_codes": [
                            "TEST_FORCED_BLOCK"
                        ],
                    }
                )
                for candidate in candidates
            ]

        return real_hard_gates(**kwargs)

    monkeypatch.setattr(
        application_module,
        "apply_production_hard_gates",
        controlled_hard_gates,
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
        request_id="PRODUCTION-DISPOSAL-SECOND-PASS",
    )

    disposal_candidates = [
        candidate
        for candidate in result.valued_candidates
        if candidate.action_type
        is ActionType.SAFE_DISPOSAL
    ]

    assert disposal_candidates

    assert len(gate_calls) == 2

    assert all(
        candidate.action_type
        is ActionType.SAFE_DISPOSAL
        for candidate in gate_calls[1]
    )

def test_production_pipeline_does_not_add_disposal_when_rescue_is_feasible() -> None:
    result = run_production_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=datetime(
            2026,
            8,
            5,
            tzinfo=UTC,
        ),
        request_id="PRODUCTION-NO-DISPOSAL-WHEN-FEASIBLE",
    )

    assert not any(
        candidate.action_type
        is ActionType.SAFE_DISPOSAL
        for candidate in result.valued_candidates
    )


def test_rescue_report_exposes_enriched_allocation_explainability() -> None:
    result = run_production_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=datetime(
            2026,
            8,
            5,
            tzinfo=UTC,
        ),
        request_id=(
            "PRODUCTION-REPORT-EXPLAINABILITY"
        ),
    )

    candidate_by_id = {
        candidate.candidate_id: candidate
        for candidate in result.valued_candidates
    }

    partial_allocation = next(
        allocation
        for allocation in result.report.selected_allocations
        if (
            allocation.allocated_quantity
            < candidate_by_id[
                allocation.candidate_id
            ].maximum_feasible_quantity
        )
    )

    candidate = candidate_by_id[
        partial_allocation.candidate_id
    ]

    ratio = (
        partial_allocation.allocated_quantity
        / candidate.maximum_feasible_quantity
    )

    assert (
        partial_allocation.destination_id
        == candidate.destination_id
    )
    assert (
        partial_allocation.destination_type
        == candidate.destination_type
    )

    assert (
        partial_allocation.offered_or_selling_price_per_unit
        == candidate.offered_or_selling_price_per_unit
    )

    assert (
        partial_allocation.estimated_rescue_success_score
        == candidate.estimated_rescue_success_score
    )

    assert (
        partial_allocation.direct_action_cost
        == candidate.direct_action_cost * ratio
    )
    assert (
        partial_allocation.logistics_cost
        == candidate.logistics_cost * ratio
    )
    assert (
        partial_allocation.handling_cost
        == candidate.handling_cost * ratio
    )

    assert (
        partial_allocation.estimated_completion_hours
        == candidate.estimated_completion_hours
    )
    assert (
        partial_allocation.distance_km
        == candidate.distance_km
    )

    assert (
        partial_allocation.expected_cash_recovery
        == candidate.expected_cash_recovery * ratio
    )
    assert (
        partial_allocation.expected_future_branch_recovery
        == (
            candidate.expected_future_branch_recovery
            * ratio
        )
    )
    assert (
        partial_allocation.expected_avoided_purchase_cost
        == (
            candidate.expected_avoided_purchase_cost
            * ratio
        )
    )
    assert (
        partial_allocation.expected_physical_rescue_quantity
        == (
            candidate.expected_physical_rescue_quantity
            * ratio
        )
    )
    assert (
        partial_allocation.expected_waste_quantity
        == candidate.expected_waste_quantity * ratio
    )

    optimizer_allocation = next(
        allocation
        for allocation
        in result.optimization_result.allocations
        if (
            allocation.candidate_id
            == partial_allocation.candidate_id
        )
    )

    assert (
        partial_allocation.expected_value_per_unit
        == optimizer_allocation.expected_value_per_unit
    )
    assert (
        partial_allocation.expected_net_recovery
        == optimizer_allocation.expected_net_recovery
    )
    assert (
        partial_allocation.binding_constraint_codes
        == optimizer_allocation.binding_constraint_codes
    )
