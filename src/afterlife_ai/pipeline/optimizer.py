"""Production adapter for deterministic global rescue optimization."""

from __future__ import annotations

from decimal import Decimal

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import ActionType
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.pipeline.runtime_config import RuntimeConfig
from afterlife_ai.planner.optimizer import (
    OptimizationResult,
    optimize_with_cp_sat,
)

ZERO = Decimal("0")


def _planning_quantities(
    planning_lots: list[SurplusPlanningLot],
) -> dict[str, Decimal]:
    """Build deterministic planning quantity map."""

    quantities: dict[str, Decimal] = {}

    for planning_lot in planning_lots:
        if planning_lot.planning_lot_id in quantities:
            raise ValueError(
                "Duplicate planning_lot_id ditemukan: "
                f"{planning_lot.planning_lot_id}."
            )

        quantities[
            planning_lot.planning_lot_id
        ] = planning_lot.planning_quantity

    return quantities


def _shared_action_capacities(
    config: RuntimeConfig,
) -> dict[ActionType, Decimal]:
    """Translate runtime shared capabilities into optimizer constraints."""

    capacities: dict[
        ActionType,
        Decimal,
    ] = {}

    repurpose = (
        config.capabilities.internal_repurpose
    )

    repurpose_enabled = (
        config.capabilities.supported_actions.get(
            ActionType.INTERNAL_REPURPOSE,
            False,
        )
    )

    if (
        repurpose_enabled
        and repurpose.capacity_scope
        == "SHARED_ACROSS_ALL_PLANNING_LOTS"
    ):
        capacities[
            ActionType.INTERNAL_REPURPOSE
        ] = repurpose.maximum_quantity

    return capacities


def optimize_production_candidates(
    *,
    candidates: list[CandidateAction],
    planning_lots: list[SurplusPlanningLot],
    config: RuntimeConfig,
) -> OptimizationResult:
    """Run CP-SAT with runtime-derived global hard constraints."""

    planning_quantities = _planning_quantities(
        planning_lots
    )

    if any(
        quantity < ZERO
        for quantity in planning_quantities.values()
    ):
        raise ValueError(
            "Production planning quantity tidak boleh negatif."
        )

    return optimize_with_cp_sat(
        candidates=candidates,
        planning_quantities=planning_quantities,
        shared_action_capacities=(
            _shared_action_capacities(config)
        ),
    )


__all__ = ["optimize_production_candidates"]
