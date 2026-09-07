from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from afterlife_ai.contracts.enums import (
    OptimizationObjective,
    SolverStatus,
)
from afterlife_ai.pipeline.application import run_production_pipeline

WORKBOOK_PATH = Path(
    "tests/fixtures/Test Afterlife/Valid/realistic simulation/"
    "REALISTIC_05_SUPERMARKET_500.xlsx"
)
RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")
PARTNER_REGISTRY_PATH = Path("configs/partner_registry_web_v2.yaml")
ANALYSIS_AT = datetime(2026, 9, 7, 15, 0, tzinfo=UTC)


def _run_with_budget(budget: Decimal):
    return run_production_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        partner_registry_path=PARTNER_REGISTRY_PATH,
        analysis_at=ANALYSIS_AT,
        request_id=f"REQ-BUDGET-MONOTONICITY-{budget}",
        optimization_objective=(
            OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
        ),
        max_logistics_budget=budget,
        minimum_expected_rescue_ratio=None,
        rescue_deadline_at=None,
    )


def test_maximize_recovery_value_is_monotonic_as_budget_relaxes() -> None:
    budgets = [
        Decimal("0"),
        Decimal("5000"),
        Decimal("50000"),
    ]

    results = [
        _run_with_budget(budget)
        for budget in budgets
    ]

    for budget, result in zip(
        budgets,
        results,
        strict=True,
    ):
        assert (
            result.optimization_result.solver_status
            is SolverStatus.OPTIMAL
        )
        assert (
            result.optimization_result.total_logistics_cost
            <= budget
        )

    planning_quantities = [
        result.report.batch_metrics.planning_quantity
        for result in results
    ]
    assert len(set(planning_quantities)) == 1

    economic_values = [
        result.report.batch_metrics.expected_total_economic_value
        for result in results
    ]

    assert economic_values[0] <= economic_values[1]
    assert economic_values[1] <= economic_values[2]
