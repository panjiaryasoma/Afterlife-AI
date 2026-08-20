"""Deterministic rescue allocation fallback without OR-Tools."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    CoverageStatus,
    FeasibilityStatus,
    ModelScoringStatus,
    SafetyStatus,
    SolverStatus,
    ValidationStatus,
)

ZERO = Decimal("0")


class FallbackAllocation(BaseModel):
    """One allocation produced by deterministic fallback."""

    model_config = ConfigDict(extra="forbid")

    allocation_id: str
    candidate_id: str
    planning_lot_id: str
    action_type: ActionType

    allocated_quantity: Decimal = Field(gt=ZERO)
    expected_value_per_unit: Decimal
    expected_net_recovery: Decimal

    solver_status: SolverStatus
    binding_constraint_codes: list[str]


class FallbackResult(BaseModel):
    """Canonical result of deterministic fallback allocation."""

    model_config = ConfigDict(extra="forbid")

    solver_status: SolverStatus
    objective_value: Decimal

    allocations: list[FallbackAllocation]
    unallocated_quantities: dict[str, Decimal]
    shared_resource_usage: dict[str, Decimal] = Field(
        default_factory=dict
    )

def _is_fallback_eligible(
    candidate: CandidateAction,
) -> bool:
    """Allow only candidates that survived hard gates."""

    return (
        candidate.validation_status
        is ValidationStatus.PASSED
        and candidate.coverage_status
        is CoverageStatus.SUPPORTED
        and candidate.safety_status
        in {
            SafetyStatus.ACCEPTABLE,
            SafetyStatus.ACCEPTABLE_WITH_URGENCY,
        }
        and candidate.feasibility_status
        is FeasibilityStatus.FEASIBLE
        and candidate.model_scoring_status
        is not ModelScoringStatus.BLOCKED
        and not candidate.rejection_reason_codes
        and candidate.maximum_feasible_quantity > ZERO
    )


def _expected_value_per_unit(
    candidate: CandidateAction,
) -> Decimal:
    """Recover expected value per unit from candidate total value."""

    if candidate.maximum_feasible_quantity <= ZERO:
        raise ValueError(
            "maximum_feasible_quantity harus positif."
        )

    return (
        candidate.expected_net_recovery
        / candidate.maximum_feasible_quantity
    )


def _allocation_id(candidate_id: str) -> str:
    """Create deterministic fallback allocation identifier."""

    if candidate_id.startswith("CAND-"):
        return "ALLOC-" + candidate_id[len("CAND-") :]

    return f"ALLOC-{candidate_id}"


def _validate_inputs(
    *,
    candidates: list[CandidateAction],
    planning_quantities: dict[str, Decimal],
    shared_action_capacities: dict[ActionType, Decimal],
    shared_destination_capacities: dict[str, Decimal],
    shared_resource_capacities: dict[str, Decimal],
    candidate_resource_requirements: dict[
        str,
        dict[str, Decimal],
    ],
) -> None:
    """Reject malformed fallback inputs before allocation."""

    candidate_ids = [
        candidate.candidate_id
        for candidate in candidates
    ]

    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError(
            "Duplicate candidate_id ditemukan pada fallback input."
        )

    for planning_lot_id, quantity in (
        planning_quantities.items()
    ):
        if quantity < ZERO:
            raise ValueError(
                "planning quantity tidak boleh negatif: "
                f"{planning_lot_id}={quantity}"
            )

    for action_type, capacity in (
        shared_action_capacities.items()
    ):
        if capacity < ZERO:
            raise ValueError(
                "shared action capacity tidak boleh negatif: "
                f"{action_type.value}={capacity}"
            )

    for destination_id, capacity in (
        shared_destination_capacities.items()
    ):
        if capacity < ZERO:
            raise ValueError(
                "shared destination capacity tidak boleh negatif: "
                f"{destination_id}={capacity}"
            )

    for resource_id, capacity in (
        shared_resource_capacities.items()
    ):
        if capacity < ZERO:
            raise ValueError(
                "shared resource capacity tidak boleh negatif: "
                f"{resource_id}={capacity}"
            )

    candidate_ids_set = set(candidate_ids)

    for candidate_id, requirements in (
        candidate_resource_requirements.items()
    ):
        if candidate_id not in candidate_ids_set:
            raise ValueError(
                "candidate_resource_requirements merujuk "
                f"candidate yang tidak ada: {candidate_id}"
            )

        for resource_id, requirement in requirements.items():
            if resource_id not in shared_resource_capacities:
                raise ValueError(
                    "Resource requirement tidak memiliki "
                    f"shared capacity: {resource_id}"
                )

            if requirement < ZERO:
                raise ValueError(
                    "candidate resource requirement "
                    "tidak boleh negatif."
                )

    for candidate in candidates:
        if (
            _is_fallback_eligible(candidate)
            and candidate.planning_lot_id
            not in planning_quantities
        ):
            raise ValueError(
                "Planning quantity tidak ditemukan untuk "
                f"{candidate.planning_lot_id}."
            )


def allocate_with_deterministic_fallback(
    *,
    candidates: list[CandidateAction],
    planning_quantities: dict[str, Decimal],
    shared_action_capacities: (
        dict[ActionType, Decimal] | None
    ) = None,
    shared_destination_capacities: (
        dict[str, Decimal] | None
    ) = None,
        shared_resource_capacities: (
        dict[str, Decimal] | None
    ) = None,
    candidate_resource_requirements: (
        dict[str, dict[str, Decimal]] | None
    ) = None,
) -> FallbackResult:
    """Allocate greedily with deterministic ordering and hard constraints."""

    shared_action_capacities = (
        shared_action_capacities or {}
    )
    shared_destination_capacities = (
        shared_destination_capacities or {}
    )

    shared_resource_capacities = (
        shared_resource_capacities or {}
    )

    candidate_resource_requirements = (
        candidate_resource_requirements or {}
    )

    _validate_inputs(
        candidates=candidates,
        planning_quantities=planning_quantities,
        shared_action_capacities=shared_action_capacities,
        shared_destination_capacities=(
            shared_destination_capacities
        ),
        shared_resource_capacities=(
            shared_resource_capacities
        ),
        candidate_resource_requirements=(
            candidate_resource_requirements
        ),
    )

    remaining_by_lot = {
        planning_lot_id: quantity
        for planning_lot_id, quantity
        in planning_quantities.items()
    }

    remaining_by_action = {
        action_type: capacity
        for action_type, capacity
        in shared_action_capacities.items()
    }

    remaining_by_destination = {
        destination_id: capacity
        for destination_id, capacity
        in shared_destination_capacities.items()
    }

    remaining_by_resource = {
        resource_id: capacity
        for resource_id, capacity
        in shared_resource_capacities.items()
    }

    eligible_candidates = [
        candidate
        for candidate in candidates
        if _is_fallback_eligible(candidate)
    ]

    ranked_candidates = sorted(
        eligible_candidates,
        key=lambda candidate: (
            -_expected_value_per_unit(candidate),
            candidate.candidate_id,
        ),
    )

    allocations: list[FallbackAllocation] = []
    objective_value = ZERO

    for candidate in ranked_candidates:
        expected_per_unit = _expected_value_per_unit(
            candidate
        )

        # Negative-value actions are never forced.
        if expected_per_unit < ZERO:
            continue

        # Zero-economic-value actions are allowed only for
        # terminal physical-rescue or safety routes.
        if (
            expected_per_unit == ZERO
            and candidate.action_type
            not in {
                ActionType.DONATION,
                ActionType.SAFE_DISPOSAL,
            }
        ):
            continue

        lot_remaining = remaining_by_lot[
            candidate.planning_lot_id
        ]

        if lot_remaining <= ZERO:
            continue

        allocatable = min(
            candidate.maximum_feasible_quantity,
            lot_remaining,
        )

        if (
            candidate.action_type
            in remaining_by_action
        ):
            allocatable = min(
                allocatable,
                remaining_by_action[
                    candidate.action_type
                ],
            )

        if (
            candidate.destination_id is not None
            and candidate.destination_id
            in remaining_by_destination
        ):
            allocatable = min(
                allocatable,
                remaining_by_destination[
                    candidate.destination_id
                ],
            )
        candidate_requirements = (
            candidate_resource_requirements.get(
                candidate.candidate_id,
                {},
            )
        )

        for resource_id, requirement in sorted(
            candidate_requirements.items()
        ):
            if requirement == ZERO:
                continue

            resource_limited_quantity = (
                remaining_by_resource[resource_id]
                / requirement
            )

            allocatable = min(
                allocatable,
                resource_limited_quantity,
            )

        if allocatable <= ZERO:
            continue

        if (
            candidate.minimum_order_quantity is not None
            and allocatable
            < candidate.minimum_order_quantity
        ):
            continue

        expected_net_recovery = (
            allocatable * expected_per_unit
        )

        remaining_by_lot[
            candidate.planning_lot_id
        ] -= allocatable

        if (
            candidate.action_type
            in remaining_by_action
        ):
            remaining_by_action[
                candidate.action_type
            ] -= allocatable

        if (
            candidate.destination_id is not None
            and candidate.destination_id
            in remaining_by_destination
        ):
            remaining_by_destination[
                candidate.destination_id
            ] -= allocatable
        for resource_id, requirement in (
            candidate_requirements.items()
        ):
            remaining_by_resource[resource_id] -= (
                allocatable * requirement
            )

        binding_constraint_codes: list[str] = []

        if (
            allocatable
            == candidate.maximum_feasible_quantity
        ):
            binding_constraint_codes.append(
                "CANDIDATE_CAPACITY"
            )

        if (
            remaining_by_lot[
                candidate.planning_lot_id
            ]
            == ZERO
        ):
            binding_constraint_codes.append(
                "PLANNING_QUANTITY"
            )

        if (
            candidate.action_type
            in remaining_by_action
            and remaining_by_action[
                candidate.action_type
            ]
            == ZERO
        ):
            binding_constraint_codes.append(
                "SHARED_ACTION_CAPACITY"
            )

        if (
            candidate.destination_id is not None
            and candidate.destination_id
            in remaining_by_destination
            and remaining_by_destination[
                candidate.destination_id
            ]
            == ZERO
        ):
            binding_constraint_codes.append(
                "SHARED_DESTINATION_CAPACITY"
            )

        for resource_id, requirement in sorted(
            candidate_requirements.items()
        ):
            if (
                requirement > ZERO
                and remaining_by_resource[
                    resource_id
                ]
                == ZERO
            ):
                binding_constraint_codes.append(
                    "SHARED_RESOURCE_CAPACITY:"
                    f"{resource_id}"
                )

        allocations.append(
            FallbackAllocation(
                allocation_id=_allocation_id(
                    candidate.candidate_id
                ),
                candidate_id=candidate.candidate_id,
                planning_lot_id=(
                    candidate.planning_lot_id
                ),
                action_type=candidate.action_type,
                allocated_quantity=allocatable,
                expected_value_per_unit=(
                    expected_per_unit
                ),
                expected_net_recovery=(
                    expected_net_recovery
                ),
                solver_status=(
                    SolverStatus.FALLBACK_USED
                ),
                binding_constraint_codes=(
                    binding_constraint_codes
                ),
            )
        )

        objective_value += expected_net_recovery

    # Defensive invariants after greedy allocation.
    for planning_lot_id, remaining in (
        remaining_by_lot.items()
    ):
        if remaining < ZERO:
            raise RuntimeError(
                "Fallback melanggar planning quantity "
                f"untuk {planning_lot_id}."
            )

    for action_type, remaining in (
        remaining_by_action.items()
    ):
        if remaining < ZERO:
            raise RuntimeError(
                "Fallback melanggar shared action capacity "
                f"untuk {action_type.value}."
            )

    for destination_id, remaining in (
        remaining_by_destination.items()
    ):
        if remaining < ZERO:
            raise RuntimeError(
                "Fallback melanggar shared destination "
                f"capacity untuk {destination_id}."
            )

    for resource_id, remaining in (
        remaining_by_resource.items()
    ):
        if remaining < ZERO:
            raise RuntimeError(
                "Fallback melanggar shared resource "
                f"capacity untuk {resource_id}."
            )

    unallocated_quantities = {
        planning_lot_id: remaining_by_lot[
            planning_lot_id
        ]
        for planning_lot_id in sorted(
            planning_quantities
        )
    }

    shared_resource_usage = {
        resource_id: (
            shared_resource_capacities[resource_id]
            - remaining_by_resource[resource_id]
        )
        for resource_id in sorted(
            shared_resource_capacities
        )
    }

    return FallbackResult(
        solver_status=SolverStatus.FALLBACK_USED,
        objective_value=objective_value,
        allocations=allocations,
        unallocated_quantities=(
            unallocated_quantities
        ),
        shared_resource_usage=(
            shared_resource_usage
        ),
    )


__all__ = [
    "FallbackAllocation",
    "FallbackResult",
    "allocate_with_deterministic_fallback",
]
