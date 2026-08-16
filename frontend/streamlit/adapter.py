"""Thin Streamlit adapter for the canonical Afterlife AI pipeline."""

from __future__ import annotations

import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from afterlife_ai.contracts.enums import (
    OptimizationObjective,
)
from afterlife_ai.contracts.request import (
    AnalysisRequest,
)
from afterlife_ai.pipeline.application import (
    ProductionPipelineResult,
    run_production_pipeline,
)

RUNTIME_CONFIG_PATH = Path(
    "configs/runtime_v1.yaml"
)

PARTNER_REGISTRY_PATH = Path(
    "configs/partner_registry_demo_v1.yaml"
)

OBJECTIVE_POLICY_VERSION = (
    "runtime-objective-v1.0"
)


def run_streamlit_analysis(
    *,
    workbook_bytes: bytes,
    inventory_file_name: str,
    analysis_at: datetime,
    request_id: str,
    optimization_objective: OptimizationObjective,
    max_logistics_budget: Decimal | None,
    minimum_expected_rescue_ratio: Decimal | None,
    rescue_deadline_at: datetime | None,
) -> ProductionPipelineResult:
    """Adapt one Streamlit upload into the canonical production pipeline."""
    if Path(inventory_file_name).suffix.lower() != ".xlsx":
        raise ValueError(
            "inventory_file harus berupa file .xlsx."
        )

    if not workbook_bytes:
        raise ValueError(
            "inventory_file tidak boleh kosong."
        )
    request = AnalysisRequest(
        request_id=request_id,
        analysis_timestamp=analysis_at,
        inventory_file_name=inventory_file_name,
        optimization_objective=(
            optimization_objective
        ),
        max_logistics_budget=(
            max_logistics_budget
        ),
        rescue_deadline_at=(
            rescue_deadline_at
        ),
        minimum_expected_rescue_ratio=(
            minimum_expected_rescue_ratio
        ),
        objective_policy_version=(
            OBJECTIVE_POLICY_VERSION
        ),
    )

    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".xlsx",
            delete=False,
        ) as temp_file:
            temp_file.write(
                workbook_bytes
            )

            temp_path = Path(
                temp_file.name
            )

        return run_production_pipeline(
            workbook_path=temp_path,
            runtime_config_path=(
                RUNTIME_CONFIG_PATH
            ),
            partner_registry_path=(
                PARTNER_REGISTRY_PATH
            ),
            analysis_at=analysis_at,
            request_id=(
                request.request_id or ""
            ),
            optimization_objective=(
                request.optimization_objective
            ),
            max_logistics_budget=(
                request.max_logistics_budget
            ),
            minimum_expected_rescue_ratio=(
                request.minimum_expected_rescue_ratio
            ),
            rescue_deadline_at=(
                request.rescue_deadline_at
            ),
        )

    finally:
        if (
            temp_path is not None
            and temp_path.exists()
        ):
            try:
                temp_path.unlink()
            except PermissionError:
                pass