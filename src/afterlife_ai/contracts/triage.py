"""Contracts for deterministic inventory triage output."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from afterlife_ai.contracts.enums import (
    InventoryStatus,
    SurplusSource,
    TriageConfidenceStatus,
    UrgencyLevel,
)


class InventoryTriageResult(BaseModel):
    """Deterministic routing result before rescue planning."""

    model_config = ConfigDict(extra="forbid")

    source_lot_id: str
    analysis_date: date

    remaining_shelf_life_days: int | None = None
    remaining_safe_window_hours: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    remaining_commercial_window_days: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    average_daily_sales: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    effective_sales_window_days: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    expected_normal_sales: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    protected_normal_stock_quantity: Decimal = Field(
        ge=Decimal("0"),
    )
    monitor_quantity: Decimal = Field(
        ge=Decimal("0"),
    )
    surplus_candidate_quantity: Decimal = Field(
        ge=Decimal("0"),
    )
    planning_quantity: Decimal = Field(
        ge=Decimal("0"),
    )
    expired_quantity: Decimal = Field(
        ge=Decimal("0"),
    )
    review_quantity: Decimal = Field(
        ge=Decimal("0"),
    )

    inventory_status: InventoryStatus
    surplus_source: SurplusSource | None = None
    triage_reason_codes: list[str]
    triage_confidence_status: TriageConfidenceStatus
    urgency_level: UrgencyLevel

    estimated_current_value: Decimal = Field(
        ge=Decimal("0"),
    )
    triage_policy_version: str

    @model_validator(mode="after")
    def validate_status_quantity_routing(self) -> Self:
        """Ensure routed quantities agree with inventory status."""

        if (
            self.planning_quantity > 0
            and self.inventory_status
            is not InventoryStatus.SURPLUS_CANDIDATE
        ):
            raise ValueError(
                "planning_quantity hanya boleh lebih dari nol "
                "ketika inventory_status adalah SURPLUS_CANDIDATE."
            )

        if (
            self.expired_quantity > 0
            and self.inventory_status is not InventoryStatus.EXPIRED
        ):
            raise ValueError(
                "expired_quantity hanya boleh lebih dari nol "
                "ketika inventory_status adalah EXPIRED."
            )

        review_statuses = {
            InventoryStatus.NEEDS_REVIEW,
            InventoryStatus.SURPLUS_CANDIDATE,
        }

        if (
            self.review_quantity > 0
            and self.inventory_status not in review_statuses
        ):
            raise ValueError(
                "review_quantity hanya boleh lebih dari nol ketika "
                "inventory_status adalah NEEDS_REVIEW atau "
                "SURPLUS_CANDIDATE."
            )

        return self


__all__ = ["InventoryTriageResult"]
