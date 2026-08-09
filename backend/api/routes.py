"""HTTP routes for the Afterlife AI production application."""

from __future__ import annotations

import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile

from fastapi import APIRouter, File, HTTPException, UploadFile
from openpyxl.utils.exceptions import InvalidFileException

from afterlife_ai.pipeline.application import (
    run_production_pipeline,
)
from afterlife_ai.planner.report import RescueDecisionReport

router = APIRouter(
    prefix="/api",
    tags=["analysis"],
)

RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")


@router.post(
    "/analyze",
    response_model=RescueDecisionReport,
)
def analyze_inventory(
    inventory_file: UploadFile = File(...),
) -> RescueDecisionReport:
    """Analyze one uploaded XLSX and return its Rescue Decision Report."""

    filename = inventory_file.filename or ""

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
            shutil.copyfileobj(
                inventory_file.file,
                temp_file,
            )
            temp_path = Path(
                temp_file.name
            )

        if temp_path.stat().st_size == 0:
            raise HTTPException(
                status_code=400,
                detail="inventory_file tidak boleh kosong.",
            )

        try:
            result = run_production_pipeline(
                workbook_path=temp_path,
                runtime_config_path=RUNTIME_CONFIG_PATH,
                analysis_at=datetime.now(UTC),
                request_id=f"REQ-{uuid4().hex}",
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
            temp_path.unlink()