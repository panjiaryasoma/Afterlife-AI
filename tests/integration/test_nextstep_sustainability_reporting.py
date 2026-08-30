from datetime import UTC, datetime
from pathlib import Path

from afterlife_ai.impact.reporting import (
    build_report_sustainability_summary,
)
from afterlife_ai.pipeline.application import (
    ProductionPipelineResult,
    run_production_pipeline,
)

FIXTURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integration_001"
)
WORKBOOK_PATH = FIXTURE_DIR / "RAW_INVENTORY_FIXTURE.xlsx"
RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")


def _run_pipeline() -> ProductionPipelineResult:
    return run_production_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=datetime(2026, 8, 5, tzinfo=UTC),
        request_id="NEXTSTEP-SUSTAINABILITY-001",
    )


def test_sustainability_summary_preserves_existing_quantity_metrics() -> None:
    result = _run_pipeline()
    metrics = result.report.batch_metrics

    summary = build_report_sustainability_summary(
        planning_lots=result.planning_lots,
        selected_allocations=result.report.selected_allocations,
        unallocated_quantities=(
            result.optimization_result.unallocated_quantities
        ),
        batch_metrics=metrics,
    )

    assert summary.reconciled_quantity == metrics.planning_quantity
    assert (
        summary.expected_rescue_quantity
        == metrics.expected_physical_rescue_quantity
    )
    assert (
        summary.expected_waste_quantity
        == metrics.expected_waste_quantity
    )
    assert summary.expected_rescue_ratio == metrics.expected_rescue_ratio


def test_sustainability_reporting_does_not_mutate_rescue_allocations() -> None:
    result = _run_pipeline()
    before = [
        allocation.model_dump()
        for allocation in result.report.selected_allocations
    ]

    build_report_sustainability_summary(
        planning_lots=result.planning_lots,
        selected_allocations=result.report.selected_allocations,
        unallocated_quantities=(
            result.optimization_result.unallocated_quantities
        ),
        batch_metrics=result.report.batch_metrics,
    )

    after = [
        allocation.model_dump()
        for allocation in result.report.selected_allocations
    ]

    assert after == before


def test_incomplete_mass_evidence_never_claims_full_batch_mass() -> None:
    result = _run_pipeline()

    summary = build_report_sustainability_summary(
        planning_lots=result.planning_lots,
        selected_allocations=result.report.selected_allocations,
        unallocated_quantities=(
            result.optimization_result.unallocated_quantities
        ),
        batch_metrics=result.report.batch_metrics,
    )

    if summary.mass_evidence_coverage != "COMPLETE":
        assert summary.expected_rescue_mass_kg is None
        assert summary.expected_waste_mass_kg is None
