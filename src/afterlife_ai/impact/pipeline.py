"""NextStep-specific production wrapper with first-class sustainability output."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from afterlife_ai.contracts.enums import OptimizationObjective
from afterlife_ai.contracts.impact import BatchSustainabilitySummary
from afterlife_ai.impact.reporting import build_report_sustainability_summary
from afterlife_ai.pipeline.application import run_production_pipeline
from afterlife_ai.planner.report import RescueDecisionReport

ZERO = Decimal("0")
QUANTITY_TOLERANCE = Decimal("1E-18")
DEFAULT_PARTNER_REGISTRY_PATH = Path(
    "configs/partner_registry_empty_v1.yaml"
)


class NextStepDecisionReport(BaseModel):
    """NextStep output that preserves the canonical rescue report contract."""

    model_config = ConfigDict(extra="forbid")

    rescue_decision_report: RescueDecisionReport
    sustainability_summary: BatchSustainabilitySummary

    @model_validator(mode="after")
    def validate_sustainability_reconciliation(self) -> Self:
        """Keep NextStep impact quantities aligned with canonical metrics."""

        metrics = self.rescue_decision_report.batch_metrics
        summary = self.sustainability_summary

        expected_rescue = (
            metrics.expected_physical_rescue_quantity
            if metrics.expected_physical_rescue_quantity is not None
            else ZERO
        )
        expected_waste = (
            metrics.expected_waste_quantity
            if metrics.expected_waste_quantity is not None
            else ZERO
        )

        checks = (
            (
                summary.reconciled_quantity,
                metrics.planning_quantity,
                "reconciled quantity",
            ),
            (
                summary.expected_rescue_quantity,
                expected_rescue,
                "expected rescue quantity",
            ),
            (
                summary.expected_waste_quantity,
                expected_waste,
                "expected waste quantity",
            ),
        )

        for left, right, label in checks:
            if abs(left - right) > QUANTITY_TOLERANCE:
                raise ValueError(
                    "NextStep sustainability summary does not match "
                    f"canonical report {label}."
                )

        if summary.expected_rescue_ratio != metrics.expected_rescue_ratio:
            raise ValueError(
                "NextStep sustainability summary does not match "
                "canonical report expected rescue ratio."
            )

        return self


def run_nextstep_pipeline(
    *,
    workbook_path: str | Path,
    runtime_config_path: str | Path,
    analysis_at: datetime,
    request_id: str,
    optimization_objective: OptimizationObjective = (
        OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
    ),
    max_logistics_budget: Decimal | None = None,
    minimum_expected_rescue_ratio: Decimal | None = None,
    rescue_deadline_at: datetime | None = None,
    partner_registry_path: str | Path = DEFAULT_PARTNER_REGISTRY_PATH,
) -> NextStepDecisionReport:
    """Run the existing production planner and attach measured impact output."""

    production = run_production_pipeline(
        workbook_path=workbook_path,
        runtime_config_path=runtime_config_path,
        analysis_at=analysis_at,
        request_id=request_id,
        optimization_objective=optimization_objective,
        max_logistics_budget=max_logistics_budget,
        minimum_expected_rescue_ratio=minimum_expected_rescue_ratio,
        rescue_deadline_at=rescue_deadline_at,
        partner_registry_path=partner_registry_path,
    )

    sustainability_summary = build_report_sustainability_summary(
        planning_lots=production.planning_lots,
        selected_allocations=(
            production.report.selected_allocations
        ),
        unallocated_quantities=(
            production.optimization_result.unallocated_quantities
        ),
    )

    return NextStepDecisionReport(
        rescue_decision_report=production.report,
        sustainability_summary=sustainability_summary,
    )


__all__ = [
    "NextStepDecisionReport",
    "run_nextstep_pipeline",
]
