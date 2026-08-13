"""Typed static Partner Demand Registry for the local MVP."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from afterlife_ai.contracts.enums import MatchStatus


class PartnerDemandRecord(BaseModel):
    """One deterministic partner-demand match in a static snapshot."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    source_lot_id: str
    partner_id: str
    destination_type: str

    maximum_quantity: Decimal = Field(
        gt=Decimal("0"),
    )

    offered_or_selling_price_per_unit: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    direct_action_cost: Decimal = Field(
        default=Decimal("0"),
        ge=Decimal("0"),
    )
    logistics_cost: Decimal = Field(
        default=Decimal("0"),
        ge=Decimal("0"),
    )
    handling_cost: Decimal = Field(
        default=Decimal("0"),
        ge=Decimal("0"),
    )

    estimated_completion_hours: Decimal = Field(
        ge=Decimal("0"),
    )

    active_demand_quantity: Decimal = Field(
        gt=Decimal("0"),
    )
    available_capacity: Decimal = Field(
        gt=Decimal("0"),
    )
    minimum_order_quantity: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    distance_km: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    demand_valid_until: datetime

    category_match_status: MatchStatus
    package_size_match_status: MatchStatus
    customer_segment_match_status: MatchStatus
    storage_compatibility_status: MatchStatus

    @model_validator(mode="after")
    def validate_demand_timestamp(
        self,
    ) -> PartnerDemandRecord:
        """Require an explicit timezone for deterministic freshness checks."""

        if self.demand_valid_until.tzinfo is None:
            raise ValueError(
                "demand_valid_until wajib timezone-aware."
            )

        return self


class PartnerDemandRegistry(BaseModel):
    """One immutable static Partner Demand Registry snapshot."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    registry_snapshot_id: str
    snapshot_mode: Literal["STATIC_OFFLINE"]
    source_type: Literal[
        "SYNTHETIC_DEMO_FIXTURE",
        "EVALUATION_FIXTURE",
    ]
    real_world_verified: bool
    runtime_internet_required: bool

    matching_records: list[PartnerDemandRecord]


def load_partner_registry(
    path: str | Path,
) -> PartnerDemandRegistry:
    """Load and validate one static partner registry YAML snapshot."""

    registry_path = Path(path)

    if not registry_path.is_file():
        raise FileNotFoundError(
            "Partner registry tidak ditemukan: "
            f"{registry_path}"
        )

    payload = yaml.safe_load(
        registry_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(payload, dict):
        raise ValueError(
            "Partner registry harus berupa YAML mapping."
        )

    return PartnerDemandRegistry.model_validate(
        payload
    )


__all__ = [
    "PartnerDemandRecord",
    "PartnerDemandRegistry",
    "load_partner_registry",
]
