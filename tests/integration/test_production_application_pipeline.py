from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from afterlife_ai.contracts.enums import (
    ApprovalStatus,
    OptimizationObjective,
    SolverStatus,
)
from afterlife_ai.pipeline.application import (
    run_production_pipeline,
)

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
