"""Analysis request contract aligned with FEATURE_SCHEMA_FINAL_v2.0.yaml."""

from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import OptimizationObjective


class AnalysisRequest(BaseModel):
    """Dynamic request context submitted with one inventory workbook."""

    model_config = ConfigDict(extra="forbid")

    request_id: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z0-9_-]+$",
    )
    analysis_timestamp: datetime | None = None

    inventory_file_name: str
    optimization_objective: OptimizationObjective

    max_logistics_budget: Decimal | None = Field(
        default=None,
        ge=0,
    )
    rescue_deadline_at: datetime | None = None

    minimum_expected_rescue_ratio: Decimal | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    objective_policy_version: str
    random_seed: int = 42

    @model_validator(mode="after")
    def validate_objective_requirements(self) -> Self:
        """Validate fields required by particular optimization objectives."""

        if (
            self.optimization_objective == OptimizationObjective.BALANCED
            and self.minimum_expected_rescue_ratio is None
        ):
            raise ValueError(
                "minimum_expected_rescue_ratio wajib diisi "
                "untuk objective BALANCED"
            )

        return self


__all__ = ["AnalysisRequest"]
