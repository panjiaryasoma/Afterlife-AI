"""Contracts for generated rescue action candidates."""

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from afterlife_ai.contracts.enums import (
    ActionType,
    CoverageStatus,
    FeasibilityStatus,
    MatchStatus,
    ModelScoringStatus,
    SafetyStatus,
    ValidationStatus,
    VerificationStatus,
)


class CandidateAction(BaseModel):
    """One generated rescue action candidate for one planning lot."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    planning_lot_id: str
    action_type: ActionType

    destination_id: str | None = None
    destination_type: str | None = None

    maximum_feasible_quantity: Decimal = Field(
        ge=Decimal("0"),
    )

    offered_or_selling_price_per_unit: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    direct_action_cost: Decimal = Field(
        ge=Decimal("0"),
    )
    logistics_cost: Decimal = Field(
        ge=Decimal("0"),
    )
    handling_cost: Decimal = Field(
        ge=Decimal("0"),
    )

    estimated_completion_hours: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    active_demand_quantity: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    available_capacity: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    minimum_order_quantity: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    capability_resource_ratio: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    demand_coverage_ratio: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    demand_freshness_hours: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    distance_km: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    category_match_status: MatchStatus
    package_size_match_status: MatchStatus
    customer_segment_match_status: MatchStatus
    storage_compatibility_status: MatchStatus

    validation_status: ValidationStatus
    coverage_status: CoverageStatus
    safety_status: SafetyStatus
    verification_status: VerificationStatus
    feasibility_status: FeasibilityStatus
    model_scoring_status: ModelScoringStatus

    rejection_reason_codes: list[str]

    fixture_rescue_success_score: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    estimated_rescue_success_score: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    model_version: str | None = None

    expected_cash_recovery: Decimal = Field(
        ge=Decimal("0"),
    )
    expected_future_branch_recovery: Decimal = Field(
        ge=Decimal("0"),
    )
    expected_avoided_purchase_cost: Decimal = Field(
        ge=Decimal("0"),
    )
    expected_physical_rescue_quantity: Decimal = Field(
        ge=Decimal("0"),
    )
    expected_waste_quantity: Decimal = Field(
        ge=Decimal("0"),
    )
    expected_net_recovery: Decimal

    @model_validator(mode="after")
    def validate_model_score_contract(self) -> Self:
        """Require an estimated model score when model scoring is allowed."""

        if (
            self.model_scoring_status is ModelScoringStatus.ALLOWED
            and self.estimated_rescue_success_score is None
        ):
            raise ValueError(
                "estimated_rescue_success_score wajib tersedia ketika "
                "model_scoring_status adalah ALLOWED."
            )

        return self


__all__ = ["CandidateAction"]
