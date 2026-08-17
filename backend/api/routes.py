"""HTTP routes for the Afterlife AI production application."""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from openpyxl.utils.exceptions import InvalidFileException
from pydantic import ValidationError

from afterlife_ai.contracts.enums import OptimizationObjective
from afterlife_ai.contracts.request import AnalysisRequest
from afterlife_ai.pipeline.application import (
    run_production_pipeline,
)
from afterlife_ai.planner.report import RescueDecisionReport

router = APIRouter(
    prefix="/api",
    tags=["analysis"],
)

RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")
PARTNER_REGISTRY_PATH = Path(
    "configs/partner_registry_demo_v1.yaml"
)
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
UPLOAD_CHUNK_SIZE_BYTES = 1024 * 1024

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
    """Analyze one uploaded XLSX and return its Rescue Decision Report."""

    filename = inventory_file.filename or ""

    analysis_at = datetime.now(UTC)
    request_id = f"REQ-{uuid4().hex}"

    try:
        request_context = AnalysisRequest(
            request_id=request_id,
            analysis_timestamp=analysis_at,
            inventory_file_name=filename,
            optimization_objective=(
                optimization_objective
            ),
            max_logistics_budget=(
                max_logistics_budget
            ),
            rescue_deadline_at=rescue_deadline_at,
            minimum_expected_rescue_ratio=(
                minimum_expected_rescue_ratio
            ),
            objective_policy_version=(
                "runtime-objective-v1.0"
            ),
        )
    except ValidationError as exc:
        validation_detail = [
            {
                "type": error["type"],
                "loc": list(error["loc"]),
                "msg": error["msg"],
            }
            for error in exc.errors(
                include_url=False,
                include_input=False,
            )
        ]

        raise HTTPException(
            status_code=422,
            detail=validation_detail,
        ) from exc

    if Path(filename).suffix.lower() != ".xlsx":
        raise HTTPException(
            status_code=400,
            detail="inventory_file harus berupa file .xlsx.",
        )

    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".xlsx",
            delete=False,
        ) as temp_file:
            temp_path = Path(
                temp_file.name
            )

            total_bytes = 0

            while True:
                chunk = inventory_file.file.read(
                    UPLOAD_CHUNK_SIZE_BYTES
                )

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "inventory_file melebihi batas upload "
                            f"{MAX_UPLOAD_SIZE_BYTES} bytes."
                        ),
                    )

                temp_file.write(chunk)

        if temp_path.stat().st_size == 0:
            raise HTTPException(
                status_code=400,
                detail="inventory_file tidak boleh kosong.",
            )

        try:
            result = run_production_pipeline(
                workbook_path=temp_path,
                runtime_config_path=RUNTIME_CONFIG_PATH,
                partner_registry_path=PARTNER_REGISTRY_PATH,
                analysis_at=analysis_at,
                request_id=request_id,
                optimization_objective=(
                    request_context.optimization_objective
                ),
                max_logistics_budget=(
                    request_context.max_logistics_budget
                ),
                minimum_expected_rescue_ratio=(
                    request_context.minimum_expected_rescue_ratio
                ),
                rescue_deadline_at=(
                    request_context.rescue_deadline_at
                ),
            )
        except (BadZipFile, InvalidFileException) as exc:
            raise HTTPException(
                status_code=422,
                detail="XLSX tidak valid atau rusak.",
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"XLSX tidak valid: {exc}",
            ) from exc

        return result.report

    finally:
        inventory_file.file.close()

        if (
            temp_path is not None
            and temp_path.exists()
        ):
            try:
                temp_path.unlink()
            except PermissionError:
                pass