"""Production candidate generation from typed runtime capabilities."""

from __future__ import annotations

from decimal import Decimal

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import ActionType
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.pipeline.runtime_config import RuntimeConfig
from afterlife_ai.planner.candidates import (
    CandidateActionSpec,
    generate_candidates,
)

ZERO = Decimal("0")


def _action_enabled(
    config: RuntimeConfig,
    action_type: ActionType,
) -> bool:
    """Return whether one action is enabled by runtime capability config."""

    return config.capabilities.supported_actions.get(
        action_type,
        False,
    )


def _local_discount_price(
    planning_lot: SurplusPlanningLot,
    config: RuntimeConfig,
) -> Decimal:
    """Calculate static MVP discount price without crossing price floor."""

    calculated = (
        planning_lot.normal_selling_price
        * config.capabilities.local_discount.price_fraction_of_normal
    )

    minimum = planning_lot.minimum_recovery_price

    if minimum is not None:
        return max(calculated, minimum)

    return calculated

def _build_safe_disposal_spec(
    *,
    planning_lot: SurplusPlanningLot,
    config: RuntimeConfig,
) -> CandidateActionSpec | None:
    """Build the deterministic safe-disposal candidate when enabled."""

    if not _action_enabled(
        config,
        ActionType.SAFE_DISPOSAL,
    ):
        return None

    safe_disposal_capability = (
        config.capabilities.safe_disposal
    )

    return CandidateActionSpec(
        action_type=ActionType.SAFE_DISPOSAL,
        maximum_quantity=(
            planning_lot.planning_quantity
        ),
        offered_or_selling_price_per_unit=ZERO,
        estimated_completion_hours=(
            safe_disposal_capability.estimated_completion_hours
        ),
        available_capacity=(
            planning_lot.planning_quantity
        ),
    )

def _build_action_specs(
    *,
    planning_lot: SurplusPlanningLot,
    config: RuntimeConfig,
) -> list[CandidateActionSpec]:
    """Build deterministic candidate specs from runtime capabilities."""

    specs: list[CandidateActionSpec] = []

    if _action_enabled(
        config,
        ActionType.INTERNAL_REPURPOSE,
    ):
        internal_repurpose_capability = (
            config.capabilities.internal_repurpose
        )

        specs.append(
            CandidateActionSpec(
                action_type=ActionType.INTERNAL_REPURPOSE,
                maximum_quantity=(
                    internal_repurpose_capability.maximum_quantity
                ),
                destination_id=(
                    internal_repurpose_capability.destination_id
                ),
                destination_type=(
                    internal_repurpose_capability.destination_type
                ),
                offered_or_selling_price_per_unit=(
                    internal_repurpose_capability.selling_price_per_unit
                ),
                direct_action_cost=(
                    internal_repurpose_capability.direct_action_cost
                ),
                estimated_completion_hours=(
                    internal_repurpose_capability.estimated_completion_hours
                ),
                available_capacity=(
                    internal_repurpose_capability.maximum_quantity
                ),
            )
        )

    if (
        _action_enabled(
            config,
            ActionType.BUNDLE,
        )
        and planning_lot.product_category
        in config.capabilities.bundle.supported_categories
        and planning_lot.sku
        in config.capabilities.bundle.supported_source_skus
    ):
        bundle_capability = config.capabilities.bundle

        specs.append(
            CandidateActionSpec(
                action_type=ActionType.BUNDLE,
                maximum_quantity=(
                    bundle_capability.maximum_quantity
                ),
                destination_id=(
                    bundle_capability.destination_id
                ),
                destination_type=(
                    bundle_capability.destination_type
                ),
                offered_or_selling_price_per_unit=(
                    bundle_capability.selling_price_per_unit
                ),
                direct_action_cost=(
                    bundle_capability.direct_action_cost
                ),
                estimated_completion_hours=(
                    bundle_capability.estimated_completion_hours
                ),
                available_capacity=(
                    bundle_capability.maximum_quantity
                ),
            )
        )

    if _action_enabled(
        config,
        ActionType.LOCAL_DISCOUNT,
    ):
        local_discount_capability = (
            config.capabilities.local_discount
        )

        specs.append(
            CandidateActionSpec(
                action_type=ActionType.LOCAL_DISCOUNT,
                maximum_quantity=(
                    planning_lot.planning_quantity
                ),
                destination_id=(
                    local_discount_capability.destination_id
                ),
                destination_type=(
                    local_discount_capability.destination_type
                ),
                offered_or_selling_price_per_unit=(
                    _local_discount_price(
                        planning_lot,
                        config,
                    )
                ),
                direct_action_cost=(
                    local_discount_capability.direct_action_cost
                ),
                estimated_completion_hours=(
                    local_discount_capability.estimated_completion_hours
                ),
                available_capacity=(
                    planning_lot.planning_quantity
                ),
            )
        )

    if not specs:
        disposal_spec = _build_safe_disposal_spec(
            planning_lot=planning_lot,
            config=config,
        )

        if disposal_spec is not None:
            specs.append(disposal_spec)

    return specs


def generate_production_candidates(
    *,
    planning_lots: list[SurplusPlanningLot],
    config: RuntimeConfig,
) -> list[CandidateAction]:
    """Generate deterministic production candidates for all planning lots."""

    candidates: list[CandidateAction] = []

    for planning_lot in planning_lots:
        specs = _build_action_specs(
            planning_lot=planning_lot,
            config=config,
        )

        candidates.extend(
            generate_candidates(
                planning_lot,
                specs,
            )
        )

    return candidates

def generate_safe_disposal_candidates(
    *,
    planning_lots: list[SurplusPlanningLot],
    config: RuntimeConfig,
) -> list[CandidateAction]:
    """Generate only safe-disposal candidates for second-pass fallback."""

    candidates: list[CandidateAction] = []

    for planning_lot in planning_lots:
        spec = _build_safe_disposal_spec(
            planning_lot=planning_lot,
            config=config,
        )

        if spec is None:
            continue

        candidates.extend(
            generate_candidates(
                planning_lot,
                [spec],
            )
        )

    return candidates


__all__ = [
    "generate_production_candidates",
    "generate_safe_disposal_candidates",
]
