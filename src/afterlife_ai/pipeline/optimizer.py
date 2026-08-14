"""Production adapter for deterministic global rescue optimization."""

from __future__ import annotations

from decimal import Decimal

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    OptimizationObjective,
    SolverStatus,
)
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.pipeline.runtime_config import RuntimeConfig
from afterlife_ai.planner.fallback import (
    FallbackResult,
    allocate_with_deterministic_fallback,
)
from afterlife_ai.planner.optimizer import (
    OptimizationAllocation,
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
def _shared_destination_capacities(
    candidates: list[CandidateAction],
) -> dict[str, Decimal]:
    """Derive global partner capacity bounds from candidate facts."""

    capacities: dict[str, Decimal] = {}

    for candidate in candidates:
        if (
            candidate.action_type
            is not ActionType.EXTERNAL_PARTNER
            or candidate.destination_id is None
        ):
            continue

        available_limits = [
            quantity
            for quantity in (
                candidate.active_demand_quantity,
                candidate.available_capacity,
            )
            if quantity is not None
        ]

        if not available_limits:
            continue

        candidate_limit = min(
            available_limits
        )

        existing_limit = capacities.get(
            candidate.destination_id
        )

        if existing_limit is None:
            capacities[
                candidate.destination_id
            ] = candidate_limit
        else:
            capacities[
                candidate.destination_id
            ] = min(
                existing_limit,
                candidate_limit,
            )

    return capacities

def _fallback_result_to_optimization_result(
    fallback_result: FallbackResult,
) -> OptimizationResult:
    """Adapt deterministic fallback output to production optimizer contract."""

    return OptimizationResult(
        solver_status=fallback_result.solver_status,
        objective_value=fallback_result.objective_value,
        allocations=[
            OptimizationAllocation(
                allocation_id=allocation.allocation_id,
                candidate_id=allocation.candidate_id,
                planning_lot_id=(
                    allocation.planning_lot_id
                ),
                action_type=allocation.action_type,
                allocated_quantity=(
                    allocation.allocated_quantity
                ),
                expected_value_per_unit=(
                    allocation.expected_value_per_unit
                ),
                expected_net_recovery=(
                    allocation.expected_net_recovery
                ),
                solver_status=allocation.solver_status,
                binding_constraint_codes=(
                    allocation.binding_constraint_codes
                ),
            )
            for allocation in fallback_result.allocations
        ],
        unallocated_quantities=(
            fallback_result.unallocated_quantities
        ),
    )


def optimize_production_candidates(
    *,
    candidates: list[CandidateAction],
    planning_lots: list[SurplusPlanningLot],
    config: RuntimeConfig,
    optimization_objective: OptimizationObjective = (
        OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
    ),
    max_logistics_budget: Decimal | None = None,
    minimum_expected_rescue_ratio: Decimal | None = None,
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

    shared_action_capacities = (
        _shared_action_capacities(config)
    )
    
    shared_destination_capacities = (
        _shared_destination_capacities(
            candidates
        )
    )

    cp_sat_result = optimize_with_cp_sat(
        candidates=candidates,
        planning_quantities=planning_quantities,
        shared_action_capacities=(
            shared_action_capacities
        ),
        shared_destination_capacities=(
            shared_destination_capacities
        ),
        max_logistics_budget=max_logistics_budget,
        optimization_objective=optimization_objective,
        minimum_expected_rescue_ratio=(
            minimum_expected_rescue_ratio
        ),
    )

    if cp_sat_result.solver_status in {
        SolverStatus.OPTIMAL,
        SolverStatus.FEASIBLE,
        SolverStatus.INFEASIBLE,
    }:
        return cp_sat_result

    fallback_can_preserve_request_constraints = (
        optimization_objective
        is OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
        and max_logistics_budget is None
        and minimum_expected_rescue_ratio is None
    )

    if not fallback_can_preserve_request_constraints:
        return cp_sat_result

    fallback_result = (
        allocate_with_deterministic_fallback(
            candidates=candidates,
            planning_quantities=planning_quantities,
            shared_action_capacities=(
                shared_action_capacities
            ),
        )
    )

    return _fallback_result_to_optimization_result(
        fallback_result
    )


__all__ = ["optimize_production_candidates"]
