"""HTTP routes for the Afterlife AI production application."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, File, Form, UploadFile

from afterlife_ai.contracts.enums import OptimizationObjective
from afterlife_ai.pipeline.application import (
    run_production_pipeline,
)
from afterlife_ai.planner.report import RescueDecisionReport
from backend.api.analysis_service import (
    MAX_UPLOAD_SIZE_BYTES,
    PARTNER_REGISTRY_PATH,
    RUNTIME_CONFIG_PATH,
    UPLOAD_CHUNK_SIZE_BYTES,
    run_uploaded_analysis,
)

router = APIRouter(
    prefix="/api",
    tags=["analysis"],
)


@router.post(
    "/analyze",
    response_model=RescueDecisionReport,
)
def analyze_inventory(
    inventory_file: UploadFile = File(...),
    optimization_objective: OptimizationObjective = Form(
        OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
    ),
    max_logistics_budget: Decimal | None = Form(
        None
    ),
    minimum_expected_rescue_ratio: Decimal | None = Form(
        None
    ),
    rescue_deadline_at: datetime | None = Form(
        None
    ),
) -> RescueDecisionReport:
    """Analyze one uploaded XLSX and return its canonical rescue report."""

    analysis_at = datetime.now(UTC)
    request_id = f"REQ-{uuid4().hex}"

    result = run_uploaded_analysis(
        inventory_file=inventory_file,
        optimization_objective=optimization_objective,
        max_logistics_budget=max_logistics_budget,
        minimum_expected_rescue_ratio=(
            minimum_expected_rescue_ratio
        ),
        rescue_deadline_at=rescue_deadline_at,
        runner=run_production_pipeline,
        analysis_at=analysis_at,
        request_id=request_id,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        partner_registry_path=PARTNER_REGISTRY_PATH,
        max_upload_size_bytes=MAX_UPLOAD_SIZE_BYTES,
        upload_chunk_size_bytes=UPLOAD_CHUNK_SIZE_BYTES,
    )

    return result.report


__all__ = [
    "MAX_UPLOAD_SIZE_BYTES",
    "PARTNER_REGISTRY_PATH",
    "RUNTIME_CONFIG_PATH",
    "UPLOAD_CHUNK_SIZE_BYTES",
    "router",
]
