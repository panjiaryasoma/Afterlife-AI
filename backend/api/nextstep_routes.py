"""HTTP route for NextStep impact-aware inventory analysis."""

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, File, Form, UploadFile

from afterlife_ai.contracts.enums import OptimizationObjective
from afterlife_ai.impact.pipeline import (
    NextStepDecisionReport,
    run_nextstep_pipeline,
)
from backend.api.analysis_service import run_uploaded_analysis

router = APIRouter(
    prefix="/api",
    tags=["analysis", "impact"],
)


@router.post(
    "/analyze-nextstep",
    response_model=NextStepDecisionReport,
)
def analyze_inventory_nextstep(
    inventory_file: UploadFile = File(...),
    optimization_objective: OptimizationObjective = Form(
        OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
    ),
    max_logistics_budget: Decimal | None = Form(None),
    minimum_expected_rescue_ratio: Decimal | None = Form(None),
    rescue_deadline_at: datetime | None = Form(None),
) -> NextStepDecisionReport:
    """Return the canonical rescue report plus NextStep sustainability output."""

    return run_uploaded_analysis(
        inventory_file=inventory_file,
        optimization_objective=optimization_objective,
        max_logistics_budget=max_logistics_budget,
        minimum_expected_rescue_ratio=(
            minimum_expected_rescue_ratio
        ),
        rescue_deadline_at=rescue_deadline_at,
        runner=run_nextstep_pipeline,
    )


__all__ = ["router"]
