from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from afterlife_ai.impact.pipeline import run_nextstep_pipeline

FIXTURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integration_001"
)
WORKBOOK_PATH = FIXTURE_DIR / "RAW_INVENTORY_FIXTURE.xlsx"
RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")


def _run_nextstep():
    return run_nextstep_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=datetime(2026, 8, 5, tzinfo=UTC),
        request_id="NEXTSTEP-PIPELINE-001",
    )


def test_nextstep_pipeline_returns_rescue_report_and_sustainability_summary() -> None:
    result = _run_nextstep()
    report = result.rescue_decision_report
    summary = result.sustainability_summary

    assert report.request_id == "NEXTSTEP-PIPELINE-001"
    assert summary.reconciled_quantity == report.batch_metrics.planning_quantity
    assert (
        summary.expected_rescue_quantity
        == report.batch_metrics.expected_physical_rescue_quantity
    )
    assert (
        summary.expected_waste_quantity
        == report.batch_metrics.expected_waste_quantity
    )
    assert summary.expected_rescue_ratio == report.batch_metrics.expected_rescue_ratio


def test_nextstep_pipeline_preserves_advisory_execution_boundary() -> None:
    result = _run_nextstep()

    assert result.rescue_decision_report.execution_performed is False
    assert result.rescue_decision_report.human_final_approval_status.value == "PENDING"


def test_nextstep_pipeline_does_not_overstate_incomplete_mass_evidence() -> None:
    result = _run_nextstep()
    summary = result.sustainability_summary

    assert summary.mass_evidence_coverage in {
        "COMPLETE",
        "PARTIAL",
        "NONE",
    }

    if summary.mass_evidence_coverage != "COMPLETE":
        assert summary.expected_rescue_mass_kg is None
        assert summary.expected_waste_mass_kg is None


def test_nextstep_quantities_still_conserve_planning_scope() -> None:
    result = _run_nextstep()
    summary = result.sustainability_summary

    assert (
        summary.expected_rescue_quantity
        + summary.expected_waste_quantity
        == summary.reconciled_quantity
    )
    assert summary.reconciled_quantity >= Decimal("0")
