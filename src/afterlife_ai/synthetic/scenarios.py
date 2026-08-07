"""Deterministic synthetic scenario feature generation."""

from dataclasses import dataclass

import numpy as np

from afterlife_ai.contracts.enums import (
    ActionType,
    BusinessType,
    SeasonalityStatus,
    SurplusSource,
    UrgencyLevel,
)
from afterlife_ai.synthetic.catalog import (
    ACTION_DESTINATION_TYPES,
    MODEL_SCORED_ACTIONS,
    PRODUCT_PROFILES,
)
from afterlife_ai.synthetic.schema_contract import ModelFeatureContract


@dataclass(frozen=True)
class SyntheticScenarioCandidate:
    """One model-eligible synthetic candidate before outcome generation."""

    scenario_group_id: str
    business_profile_id: str
    request_id: str
    lot_id: str
    candidate_id: str
    feature_values: dict[str, str | int | float | None]


_BUSINESS_TYPES: tuple[BusinessType, ...] = (
    BusinessType.SMALL_RETAIL,
    BusinessType.MEDIUM_RETAIL,
    BusinessType.SMALL_FNB,
    BusinessType.MEDIUM_FNB,
    BusinessType.MEDIUM_WHOLESALER,
)

_URGENCY_LEVELS: tuple[UrgencyLevel, ...] = (
    UrgencyLevel.LOW,
    UrgencyLevel.MEDIUM,
    UrgencyLevel.HIGH,
    UrgencyLevel.CRITICAL,
)

_SURPLUS_SOURCES: tuple[SurplusSource, ...] = (
    SurplusSource.CALCULATED,
    SurplusSource.USER_DECLARED,
    SurplusSource.RULE_TRIGGERED,
)

_SEASONALITY_STATUSES: tuple[SeasonalityStatus, ...] = (
    SeasonalityStatus.IN_SEASON,
    SeasonalityStatus.POST_SEASON,
    SeasonalityStatus.PRE_SEASON,
    SeasonalityStatus.NOT_APPLICABLE,
)


def _choice[T](
    rng: np.random.Generator,
    values: tuple[T, ...],
) -> T:
    """Select one tuple item deterministically through the supplied RNG."""

    index = int(rng.integers(0, len(values)))
    return values[index]


def _rounded_uniform(
    rng: np.random.Generator,
    low: float,
    high: float,
    digits: int = 2,
) -> float:
    """Sample one bounded synthetic numeric value."""

    return round(float(rng.uniform(low, high)), digits)


def _price_features(
    rng: np.random.Generator,
    action: ActionType,
) -> tuple[float, float, float]:
    """Generate internally consistent synthetic price values."""

    unit_cost = _rounded_uniform(rng, 2_000.0, 80_000.0)
    markup_ratio = _rounded_uniform(rng, 1.10, 1.80, 4)
    normal_price = round(unit_cost * markup_ratio, 2)

    if action is ActionType.DONATION:
        offered_price = 0.0
    elif action is ActionType.INTERNAL_USE:
        offered_price = 0.0
    else:
        recovery_ratio = _rounded_uniform(rng, 0.35, 1.00, 4)
        offered_price = round(normal_price * recovery_ratio, 2)

    return unit_cost, normal_price, offered_price


def _numeric_features(
    rng: np.random.Generator,
    action: ActionType,
    planning_quantity: int,
) -> dict[str, float | int]:
    """Generate bounded synthetic numeric model features."""

    unit_cost, normal_price, offered_price = _price_features(
        rng,
        action,
    )

    active_demand = int(
        rng.integers(
            max(1, planning_quantity // 2),
            planning_quantity * 3 + 1,
        )
    )
    available_capacity = int(
        rng.integers(
            max(1, planning_quantity // 2),
            planning_quantity * 3 + 1,
        )
    )

    minimum_order_quantity = int(
        rng.integers(
            1,
            max(2, planning_quantity + 1),
        )
    )

    if action in {
        ActionType.LOCAL_DISCOUNT,
        ActionType.BUNDLE,
        ActionType.PROMOTIONAL_BONUS,
        ActionType.INTERNAL_REPURPOSE,
        ActionType.INTERNAL_USE,
    }:
        distance_km = 0.0
        logistics_cost = 0.0
    else:
        distance_km = _rounded_uniform(rng, 0.5, 40.0)
        logistics_cost = _rounded_uniform(rng, 1_000.0, 75_000.0)

    return {
        "planning_quantity": planning_quantity,
        "remaining_shelf_life_days": int(rng.integers(1, 366)),
        "remaining_safe_window_hours": _rounded_uniform(
            rng,
            4.0,
            720.0,
        ),
        "remaining_commercial_window_days": _rounded_uniform(
            rng,
            1.0,
            120.0,
        ),
        "unit_cost": unit_cost,
        "normal_selling_price": normal_price,
        "offered_or_selling_price_per_unit": offered_price,
        "direct_action_cost": _rounded_uniform(
            rng,
            0.0,
            50_000.0,
        ),
        "logistics_cost": logistics_cost,
        "handling_cost": _rounded_uniform(
            rng,
            0.0,
            25_000.0,
        ),
        "estimated_completion_hours": _rounded_uniform(
            rng,
            0.5,
            168.0,
        ),
        "active_demand_quantity": active_demand,
        "available_capacity": available_capacity,
        "minimum_order_quantity": minimum_order_quantity,
        "capability_resource_ratio": _rounded_uniform(
            rng,
            0.25,
            1.50,
            4,
        ),
        "demand_coverage_ratio": _rounded_uniform(
            rng,
            0.10,
            2.00,
            4,
        ),
        "demand_freshness_hours": _rounded_uniform(
            rng,
            0.0,
            168.0,
        ),
        "distance_km": distance_km,
        "package_volume_ml": _rounded_uniform(
            rng,
            50.0,
            5_000.0,
        ),
        "package_weight_g": _rounded_uniform(
            rng,
            10.0,
            10_000.0,
        ),
    }


def generate_scenario_candidates(
    *,
    seed: int,
    scenario_groups: int,
    candidates_per_group_min: int,
    candidates_per_group_max: int,
    contract: ModelFeatureContract,
) -> list[SyntheticScenarioCandidate]:
    """Generate deterministic model-feature candidates.

    These values are synthetic coverage parameters, not empirical
    frequency or market-distribution claims.
    """

    if scenario_groups <= 0:
        raise ValueError("scenario_groups harus lebih besar dari 0.")

    if candidates_per_group_min < 2:
        raise ValueError(
            "candidates_per_group_min tidak boleh kurang dari 2."
        )

    if candidates_per_group_max > 8:
        raise ValueError(
            "candidates_per_group_max tidak boleh lebih besar dari 8."
        )

    if candidates_per_group_max < candidates_per_group_min:
        raise ValueError(
            "Maximum candidates tidak boleh lebih kecil dari minimum."
        )

    rng = np.random.default_rng(seed)
    generated: list[SyntheticScenarioCandidate] = []

    for group_number in range(1, scenario_groups + 1):
        scenario_group_id = f"SG-{group_number:05d}"
        business_profile_id = (
            f"BP-{((group_number - 1) % 100) + 1:03d}"
        )
        request_id = f"SYN-REQ-{group_number:05d}"
        lot_id = f"SYN-LOT-{group_number:05d}"

        profile = PRODUCT_PROFILES[
            int(rng.integers(0, len(PRODUCT_PROFILES)))
        ]

        business_type = _choice(rng, _BUSINESS_TYPES)
        urgency = _choice(rng, _URGENCY_LEVELS)
        surplus_source = _choice(rng, _SURPLUS_SOURCES)
        seasonality = _choice(rng, _SEASONALITY_STATUSES)

        subcategory = _choice(rng, profile.subcategories)
        storage_requirement = _choice(
            rng,
            profile.storage_requirement_modes,
        )
        package_format = _choice(rng, profile.package_formats)

        planning_quantity = int(rng.integers(2, 251))

        candidate_count = int(
            rng.integers(
                candidates_per_group_min,
                candidates_per_group_max + 1,
            )
        )

        action_indices = rng.choice(
            len(MODEL_SCORED_ACTIONS),
            size=candidate_count,
            replace=False,
        )

        actions = [
            MODEL_SCORED_ACTIONS[int(index)]
            for index in action_indices
        ]

        for candidate_number, action in enumerate(actions, start=1):
            categorical_features = {
                "product_category": profile.category.value,
                "product_subcategory": subcategory,
                "action_type": action.value,
                "business_type": business_type.value,
                "storage_requirement_mode": (
                    storage_requirement.value
                ),
                "urgency_level": urgency.value,
                "surplus_source": surplus_source.value,
                "destination_type": ACTION_DESTINATION_TYPES[action],
                "seasonality_status": seasonality.value,
                "package_format": package_format,
            }

            numeric_features = _numeric_features(
                rng,
                action,
                planning_quantity,
            )

            feature_values: dict[
                str,
                str | int | float | None,
            ] = {
                **categorical_features,
                **numeric_features,
            }

            actual_features = set(feature_values)
            expected_features = set(contract.model_features)

            if actual_features != expected_features:
                missing = expected_features - actual_features
                unexpected = actual_features - expected_features

                raise RuntimeError(
                    "Generated feature set tidak sesuai schema. "
                    f"missing={sorted(missing)}, "
                    f"unexpected={sorted(unexpected)}"
                )

            candidate_id = (
                f"SYN-CAND-{group_number:05d}-"
                f"{candidate_number:02d}"
            )

            generated.append(
                SyntheticScenarioCandidate(
                    scenario_group_id=scenario_group_id,
                    business_profile_id=business_profile_id,
                    request_id=request_id,
                    lot_id=lot_id,
                    candidate_id=candidate_id,
                    feature_values=feature_values,
                )
            )

    return generated


__all__ = [
    "SyntheticScenarioCandidate",
    "generate_scenario_candidates",
]
