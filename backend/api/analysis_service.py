"""Shared HTTP upload execution for canonical and NextStep analysis routes."""

from __future__ import annotations

import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Protocol
from zipfile import BadZipFile

from fastapi import HTTPException, UploadFile
from openpyxl.utils.exceptions import InvalidFileException
from pydantic import ValidationError

from afterlife_ai.contracts.enums import OptimizationObjective
from afterlife_ai.contracts.request import AnalysisRequest

RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")
PARTNER_REGISTRY_PATH = Path(
    "configs/partner_registry_demo_v1.yaml"
)
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
UPLOAD_CHUNK_SIZE_BYTES = 1024 * 1024


class AnalysisRunner[ResultT](Protocol):
    """Callable contract shared by production and NextStep pipeline runners."""

    def __call__(
        self,
        *,
        workbook_path: str | Path,
        runtime_config_path: str | Path,
        analysis_at: datetime,
        request_id: str,
        optimization_objective: OptimizationObjective,
        max_logistics_budget: Decimal | None,
        minimum_expected_rescue_ratio: Decimal | None,
        rescue_deadline_at: datetime | None,
        partner_registry_path: str | Path,
    ) -> ResultT: ...


def _validation_detail(exc: ValidationError) -> list[dict[str, object]]:
    return [
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


def run_uploaded_analysis[ResultT](
    *,
    inventory_file: UploadFile,
    optimization_objective: OptimizationObjective,
    max_logistics_budget: Decimal | None,
    minimum_expected_rescue_ratio: Decimal | None,
    rescue_deadline_at: datetime | None,
    runner: AnalysisRunner[ResultT],
    analysis_at: datetime,
    request_id: str,
    runtime_config_path: str | Path,
    partner_registry_path: str | Path,
    max_upload_size_bytes: int,
    upload_chunk_size_bytes: int = UPLOAD_CHUNK_SIZE_BYTES,
) -> ResultT:
    """Validate one uploaded workbook, run the supplied pipeline, then clean up."""

    filename = inventory_file.filename or ""

    try:
        request_context = AnalysisRequest(
            request_id=request_id,
            analysis_timestamp=analysis_at,
            inventory_file_name=filename,
            optimization_objective=optimization_objective,
            max_logistics_budget=max_logistics_budget,
            rescue_deadline_at=rescue_deadline_at,
            minimum_expected_rescue_ratio=(
                minimum_expected_rescue_ratio
            ),
            objective_policy_version="runtime-objective-v1.0",
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=_validation_detail(exc),
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
            temp_path = Path(temp_file.name)
            total_bytes = 0

            while True:
                chunk = inventory_file.file.read(
                    upload_chunk_size_bytes
                )

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > max_upload_size_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "inventory_file melebihi batas upload "
                            f"{max_upload_size_bytes} bytes."
                        ),
                    )

                temp_file.write(chunk)

        if temp_path.stat().st_size == 0:
            raise HTTPException(
                status_code=400,
                detail="inventory_file tidak boleh kosong.",
            )

        try:
            return runner(
                workbook_path=temp_path,
                runtime_config_path=runtime_config_path,
                partner_registry_path=partner_registry_path,
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
    finally:
        inventory_file.file.close()

        if temp_path is not None and temp_path.exists():
            try:
                temp_path.unlink()
            except PermissionError:
                pass


__all__ = [
    "AnalysisRunner",
    "MAX_UPLOAD_SIZE_BYTES",
    "PARTNER_REGISTRY_PATH",
    "RUNTIME_CONFIG_PATH",
    "UPLOAD_CHUNK_SIZE_BYTES",
    "run_uploaded_analysis",
]
