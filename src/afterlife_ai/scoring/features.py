"""Build production model features from runtime planning objects."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import BusinessType
from afterlife_ai.contracts.planning import SurplusPlanningLot


def _derive_ratio(
    *,
    explicit_value: Decimal | None,
    numerator: Decimal | None,
    denominator: Decimal,
) -> Decimal | None:
    """Use explicit ratio or derive it from available runtime quantities."""

    if explicit_value is not None:
        return explicit_value

    if numerator is None or denominator <= 0:
        return None

    return numerator / denominator

def build_model_feature_row(
    *,
    planning_lot: SurplusPlanningLot,
    candidate: CandidateAction,
    business_type: BusinessType,
) -> dict[str, Any]:
    """Build the locked schema-v2 feature row for one candidate."""

    if candidate.planning_lot_id != planning_lot.planning_lot_id:
        raise ValueError(
            "Candidate dan planning lot tidak memiliki "
            "planning_lot_id yang sama."
        )

    return {
        # Categorical features
        "product_category": planning_lot.product_category.value,
        "product_subcategory": planning_lot.product_subcategory,
        "action_type": candidate.action_type.value,
        "business_type": business_type.value,
        "storage_requirement_mode": (
            planning_lot.storage_requirement_mode.value
        ),
        "urgency_level": planning_lot.urgency_level.value,
        "surplus_source": planning_lot.surplus_source.value,
        "destination_type": candidate.destination_type,
        "seasonality_status": (
            planning_lot.seasonality_status.value
            if planning_lot.seasonality_status is not None
            else None
        ),
        "package_format": planning_lot.package_format,

        # Numeric features
        "planning_quantity": planning_lot.planning_quantity,
        "remaining_shelf_life_days": (
            planning_lot.remaining_shelf_life_days
        ),
        "remaining_safe_window_hours": (
            planning_lot.remaining_safe_window_hours
        ),
        "remaining_commercial_window_days": (
            planning_lot.remaining_commercial_window_days
        ),
        "unit_cost": planning_lot.unit_cost,
        "normal_selling_price": planning_lot.normal_selling_price,
        "offered_or_selling_price_per_unit": (
            candidate.offered_or_selling_price_per_unit
        ),
        "direct_action_cost": candidate.direct_action_cost,
        "logistics_cost": candidate.logistics_cost,
        "handling_cost": candidate.handling_cost,
        "estimated_completion_hours": (
            candidate.estimated_completion_hours
        ),
        "active_demand_quantity": candidate.active_demand_quantity,
        "available_capacity": candidate.available_capacity,
        "minimum_order_quantity": candidate.minimum_order_quantity,
        "capability_resource_ratio": _derive_ratio(
            explicit_value=candidate.capability_resource_ratio,
            numerator=candidate.available_capacity,
            denominator=planning_lot.planning_quantity,
        ),
        "demand_coverage_ratio": _derive_ratio(
            explicit_value=candidate.demand_coverage_ratio,
            numerator=candidate.active_demand_quantity,
            denominator=planning_lot.planning_quantity,
        ),
        "demand_freshness_hours": (
            candidate.demand_freshness_hours
        ),
        "distance_km": candidate.distance_km,
        "package_volume_ml": planning_lot.package_volume_ml,
        "package_weight_g": planning_lot.package_weight_g,
    }


__all__ = ["build_model_feature_row"]
