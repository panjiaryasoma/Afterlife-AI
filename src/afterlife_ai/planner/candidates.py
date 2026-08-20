"""Deterministic candidate generation for rescue planning."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    CoverageStatus,
    FeasibilityStatus,
    MatchStatus,
    ModelScoringStatus,
    SafetyStatus,
    ValidationStatus,
)
from afterlife_ai.contracts.planning import SurplusPlanningLot


class CandidateActionSpec(BaseModel):
    """Deterministic action specification supplied by capability logic."""

    model_config = ConfigDict(extra="forbid")

    action_type: ActionType
    maximum_quantity: Decimal = Field(ge=Decimal("0"))

    destination_id: str | None = None
    destination_type: str | None = None

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

    category_match_status: MatchStatus = (
        MatchStatus.NOT_APPLICABLE
    )
    package_size_match_status: MatchStatus = (
        MatchStatus.NOT_APPLICABLE
    )
    customer_segment_match_status: MatchStatus = (
        MatchStatus.NOT_APPLICABLE
    )
    storage_compatibility_status: MatchStatus = (
        MatchStatus.NOT_APPLICABLE
    )


_ACTION_ORDER = {
    ActionType.INTERNAL_REPURPOSE: 10,
    ActionType.BUNDLE: 20,
    ActionType.LOCAL_DISCOUNT: 30,
    ActionType.PROMOTIONAL_BONUS: 40,
    ActionType.INTERNAL_USE: 50,
    ActionType.RETURN_TO_SUPPLIER: 60,
    ActionType.BRANCH_TRANSFER: 70,
    ActionType.WHOLESALE: 80,
    ActionType.EXTERNAL_PARTNER: 90,
    ActionType.DONATION: 100,
    ActionType.SAFE_DISPOSAL: 110,
}

_ACTION_ID_SUFFIX = {
    ActionType.INTERNAL_REPURPOSE: "REPURPOSE",
    ActionType.BUNDLE: "BUNDLE",
    ActionType.LOCAL_DISCOUNT: "DISCOUNT",
    ActionType.PROMOTIONAL_BONUS: "BONUS",
    ActionType.INTERNAL_USE: "INTERNAL-USE",
    ActionType.RETURN_TO_SUPPLIER: "RETURN",
    ActionType.BRANCH_TRANSFER: "TRANSFER",
    ActionType.WHOLESALE: "WHOLESALE",
    ActionType.EXTERNAL_PARTNER: "PARTNER",
    ActionType.DONATION: "DONATION",
    ActionType.SAFE_DISPOSAL: "DISPOSAL",
}


def _planning_lot_token(planning_lot_id: str) -> str:
    """Extract stable token used by deterministic candidate IDs."""

    prefix = "PLAN-LOT-"

    if planning_lot_id.startswith(prefix):
        return planning_lot_id[len(prefix) :]

    return planning_lot_id


def _candidate_id(
    planning_lot: SurplusPlanningLot,
    action_type: ActionType,
    destination_id: str | None = None,
) -> str:
    """Build deterministic candidate identifier."""

    token = _planning_lot_token(planning_lot.planning_lot_id)
    suffix = _ACTION_ID_SUFFIX[action_type]

    candidate_id = f"CAND-{token}-{suffix}"

    if (
        action_type is ActionType.EXTERNAL_PARTNER
        and destination_id is not None
    ):
        return f"{candidate_id}-{destination_id}"

    return candidate_id


def generate_candidates(
    planning_lot: SurplusPlanningLot,
    action_specs: list[CandidateActionSpec],
) -> list[CandidateAction]:
    """Generate deterministic candidates from supplied action capability specs."""

    candidates: list[CandidateAction] = []

    ordered_specs = sorted(
        action_specs,
        key=lambda spec: (
            _ACTION_ORDER.get(spec.action_type, 999),
            spec.action_type.value,
        ),
    )

    for spec in ordered_specs:
        maximum_feasible_quantity = min(
            planning_lot.planning_quantity,
            spec.maximum_quantity,
        )

        if maximum_feasible_quantity <= 0:
            continue

        available_capacity = spec.available_capacity

        if available_capacity is None:
            available_capacity = maximum_feasible_quantity

        candidate = CandidateAction(
            candidate_id=_candidate_id(
                planning_lot,
                spec.action_type,
                spec.destination_id,
            ),
            planning_lot_id=planning_lot.planning_lot_id,
            action_type=spec.action_type,
            destination_id=spec.destination_id,
            destination_type=spec.destination_type,
            maximum_feasible_quantity=maximum_feasible_quantity,
            offered_or_selling_price_per_unit=(
                spec.offered_or_selling_price_per_unit
            ),
            direct_action_cost=spec.direct_action_cost,
            logistics_cost=spec.logistics_cost,
            handling_cost=spec.handling_cost,
            estimated_completion_hours=(
                spec.estimated_completion_hours
            ),
            active_demand_quantity=spec.active_demand_quantity,
            available_capacity=available_capacity,
            minimum_order_quantity=spec.minimum_order_quantity,
            capability_resource_ratio=(
                spec.capability_resource_ratio
            ),
            demand_coverage_ratio=spec.demand_coverage_ratio,
            demand_freshness_hours=spec.demand_freshness_hours,
            distance_km=spec.distance_km,
            category_match_status=(
                spec.category_match_status
            ),
            package_size_match_status=(
                spec.package_size_match_status
            ),
            customer_segment_match_status=(
                spec.customer_segment_match_status
            ),
            storage_compatibility_status=(
                spec.storage_compatibility_status
            ),
            validation_status=ValidationStatus.PARTIAL,
            coverage_status=CoverageStatus.INSUFFICIENT_FEATURE_COVERAGE,
            safety_status=SafetyStatus.UNVERIFIED,
            verification_status=planning_lot.verification_status,
            feasibility_status=FeasibilityStatus.NEEDS_REVIEW,
            model_scoring_status=ModelScoringStatus.DEFERRED,
            rejection_reason_codes=[],
            fixture_rescue_success_score=None,
            estimated_rescue_success_score=None,
            model_version=None,
            expected_cash_recovery=Decimal("0"),
            expected_future_branch_recovery=Decimal("0"),
            expected_avoided_purchase_cost=Decimal("0"),
            expected_physical_rescue_quantity=Decimal("0"),
            expected_waste_quantity=Decimal("0"),
            expected_net_recovery=Decimal("0"),
        )

        candidates.append(candidate)

    return candidates


__all__ = [
    "CandidateActionSpec",
    "generate_candidates",
]
