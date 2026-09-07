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

from afterlife_ai.contracts.enums import (
    MatchStatus,
    ProductCategory,
)


class PartnerDemandRecord(BaseModel):
    """One deterministic partner-demand match in a static snapshot."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    source_lot_id: str | None = None
    product_category: ProductCategory | None = None
    partner_id: str
    destination_type: str

    maximum_quantity: Decimal = Field(
        gt=Decimal("0"),
    )

    offered_or_selling_price_per_unit: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    offered_price_fraction_of_normal: Decimal | None = Field(
        default=None,
        gt=Decimal("0"),
        le=Decimal("1"),
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
    def validate_record_contract(
        self,
    ) -> PartnerDemandRecord:
        """Require deterministic selector, offer source, and timestamp."""

        if (
            self.source_lot_id is None
            and self.product_category is None
        ):
            raise ValueError(
                "Partner demand record membutuhkan source_lot_id "
                "atau product_category."
            )

        price_sources = sum(
            value is not None
            for value in (
                self.offered_or_selling_price_per_unit,
                self.offered_price_fraction_of_normal,
            )
        )

        if price_sources != 1:
            raise ValueError(
                "Partner demand record membutuhkan tepat satu "
                "sumber harga: offered_or_selling_price_per_unit "
                "atau offered_price_fraction_of_normal."
            )

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
    registry_snapshot_timestamp: datetime
    snapshot_mode: Literal["STATIC_OFFLINE"]
    source_type: Literal[
        "SYNTHETIC_DEMO_FIXTURE",
        "EVALUATION_FIXTURE",
    ]
    real_world_verified: bool
    runtime_internet_required: Literal[False]

    matching_records: list[PartnerDemandRecord]

    @model_validator(mode="after")
    def validate_snapshot_timestamp(
        self,
    ) -> PartnerDemandRegistry:
        """Require timezone-aware snapshot timestamp when supplied."""

        if self.registry_snapshot_timestamp.tzinfo is None:
            raise ValueError(
                "registry_snapshot_timestamp wajib timezone-aware."
            )

        return self


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
