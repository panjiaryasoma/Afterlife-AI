"""CP-SAT allocation optimizer for deterministic rescue planning."""

from decimal import ROUND_HALF_UP, Decimal

from ortools.sat.python import cp_model
from pydantic import BaseModel, ConfigDict, Field

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    CoverageStatus,
    FeasibilityStatus,
    ModelScoringStatus,
    OptimizationObjective,
    SafetyStatus,
    SolverStatus,
    ValidationStatus,
)

ZERO = Decimal("0")

OPTIMIZER_NUM_SEARCH_WORKERS = 1
OPTIMIZER_RANDOM_SEED = 42
ONE = Decimal("1")

# CP-SAT requires integer coefficients. Bound economic
# objective precision before integer scaling so repeating
# Decimal divisions cannot create unsafe coefficient scales.
OPTIMIZER_VALUE_QUANTUM = Decimal("0.0001")
MONEY_QUANTUM = Decimal("0.01")


class OptimizationAllocation(BaseModel):
    """One optimizer-selected rescue allocation."""

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


class OptimizationResult(BaseModel):
    """Canonical deterministic optimizer result."""

    model_config = ConfigDict(extra="forbid")

    solver_status: SolverStatus
    objective_value: Decimal

    allocations: list[OptimizationAllocation]
    unallocated_quantities: dict[str, Decimal]

    total_logistics_cost: Decimal = Field(
        default=ZERO,
        ge=ZERO,
    )

    shared_resource_usage: dict[str, Decimal] = Field(
        default_factory=dict
    )

    expected_physical_rescue_quantity: Decimal = Field(
        default=ZERO,
        ge=ZERO,
    )


def _decimal_places(value: Decimal) -> int:
    exponent = value.as_tuple().exponent

    if not isinstance(exponent, int):
        raise ValueError(
            "Optimizer hanya menerima finite Decimal values."
        )

    return max(0, -exponent)


def _scale(values: list[Decimal]) -> int:
    if not values:
        return 1

    decimal_places = max(
        _decimal_places(value)
        for value in values
    )

    return int(10**decimal_places)


def _to_scaled_int(
    value: Decimal,
    scale: int,
) -> int:
    scaled = value * Decimal(scale)

    if scaled != scaled.to_integral_value():
        raise ValueError(
            f"Value {value} tidak dapat direpresentasikan "
            f"dengan scale {scale}."
        )

    return int(scaled)


def _exact_int(value: Decimal) -> int:
    if value != value.to_integral_value():
        raise ValueError(
            f"Scaled value {value} tidak integral."
        )

    return int(value)


def _is_optimizer_eligible(
    candidate: CandidateAction,
) -> bool:
    """Only candidates surviving hard gates may enter optimization."""

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
    if candidate.maximum_feasible_quantity <= ZERO:
        raise ValueError(
            "maximum_feasible_quantity harus positif."
        )

    value_per_unit = (
        candidate.expected_net_recovery
        / candidate.maximum_feasible_quantity
    )

    return value_per_unit.quantize(
        OPTIMIZER_VALUE_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def _expected_rescue_per_unit(
    candidate: CandidateAction,
) -> Decimal:
    if candidate.maximum_feasible_quantity <= ZERO:
        raise ValueError(
            "maximum_feasible_quantity harus positif."
        )

    return (
        candidate.expected_physical_rescue_quantity
        / candidate.maximum_feasible_quantity
    )


def _solver_status(status: int) -> SolverStatus:
    if status == cp_model.OPTIMAL:
        return SolverStatus.OPTIMAL

    if status == cp_model.FEASIBLE:
        return SolverStatus.FEASIBLE

    if status == cp_model.INFEASIBLE:
        return SolverStatus.INFEASIBLE

    if status == cp_model.MODEL_INVALID:
        return SolverStatus.MODEL_INVALID

    return SolverStatus.UNKNOWN


def _allocation_id(candidate_id: str) -> str:
    if candidate_id.startswith("CAND-"):
        return "ALLOC-" + candidate_id[len("CAND-") :]

    return f"ALLOC-{candidate_id}"


def _validate_unique_candidate_ids(
    candidates: list[CandidateAction],
) -> None:
    candidate_ids = [
        candidate.candidate_id
        for candidate in candidates
    ]

    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError(
            "Duplicate candidate_id ditemukan pada optimizer input."
        )


def _validate_inputs(
    *,
    candidates: list[CandidateAction],
    planning_quantities: dict[str, Decimal],
    shared_action_capacities: dict[
        ActionType,
        Decimal,
    ],
    shared_action_minimum_quantities: dict[
        ActionType,
        Decimal,
    ],
    shared_destination_capacities: dict[
        str,
        Decimal,
    ],
    shared_resource_capacities: dict[
        str,
        Decimal,
    ],
    candidate_resource_requirements: dict[
        str,
        dict[str, Decimal],
    ],
    max_logistics_budget: Decimal | None,
    optimization_objective: OptimizationObjective,
    minimum_expected_rescue_ratio: Decimal | None,
) -> None:
    if any(
        quantity < ZERO
        for quantity in planning_quantities.values()
    ):
        raise ValueError(
            "planning_quantities tidak boleh negatif."
        )

    for action_type, capacity in (
        shared_action_capacities.items()
    ):
        if capacity < ZERO:
            raise ValueError(
                "shared action capacity tidak boleh negatif: "
                f"{action_type.value}={capacity}"
            )

    for action_type, minimum_quantity in (
        shared_action_minimum_quantities.items()
    ):
        if minimum_quantity < ZERO:
            raise ValueError(
                "shared action minimum quantity tidak boleh negatif: "
                f"{action_type.value}={minimum_quantity}"
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

    candidate_ids = {
        candidate.candidate_id
        for candidate in candidates
    }

    for candidate_id, requirements in (
        candidate_resource_requirements.items()
    ):
        if candidate_id not in candidate_ids:
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

    if (
        max_logistics_budget is not None
        and max_logistics_budget < ZERO
    ):
        raise ValueError(
            "max_logistics_budget tidak boleh negatif."
        )

    if minimum_expected_rescue_ratio is not None:
        if not (
            ZERO
            <= minimum_expected_rescue_ratio
            <= ONE
        ):
            raise ValueError(
                "minimum_expected_rescue_ratio harus "
                "berada pada rentang 0..1."
            )

    if (
        optimization_objective
        is OptimizationObjective.BALANCED
        and minimum_expected_rescue_ratio is None
    ):
        raise ValueError(
            "minimum_expected_rescue_ratio wajib "
            "untuk objective BALANCED."
        )


def optimize_with_cp_sat(
    *,
    candidates: list[CandidateAction],
    planning_quantities: dict[str, Decimal],
    shared_action_capacities: (
        dict[ActionType, Decimal] | None
    ) = None,
    shared_action_minimum_quantities: (
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
    max_logistics_budget: Decimal | None = None,
    optimization_objective: OptimizationObjective = (
        OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
    ),
    minimum_expected_rescue_ratio: Decimal | None = None,
) -> OptimizationResult:
    """Optimize rescue allocation under deterministic hard constraints."""

    shared_action_capacities = (
        shared_action_capacities or {}
    )
    shared_action_minimum_quantities = (
        shared_action_minimum_quantities or {}
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

    _validate_unique_candidate_ids(candidates)

    _validate_inputs(
        candidates=candidates,
        planning_quantities=planning_quantities,
        shared_action_capacities=(
            shared_action_capacities
        ),
        shared_action_minimum_quantities=(
            shared_action_minimum_quantities
        ),
        shared_destination_capacities=(
            shared_destination_capacities
        ),
        shared_resource_capacities=(
            shared_resource_capacities
        ),
        candidate_resource_requirements=(
            candidate_resource_requirements
        ),
        max_logistics_budget=max_logistics_budget,
        optimization_objective=optimization_objective,
        minimum_expected_rescue_ratio=(
            minimum_expected_rescue_ratio
        ),
    )

    eligible_candidates = sorted(
        (
            candidate
            for candidate in candidates
            if _is_optimizer_eligible(candidate)
        ),
        key=lambda candidate: candidate.candidate_id,
    )

    for candidate in eligible_candidates:
        if (
            candidate.planning_lot_id
            not in planning_quantities
        ):
            raise ValueError(
                "Planning quantity tidak ditemukan untuk "
                f"{candidate.planning_lot_id}."
            )

    quantity_values = list(
        planning_quantities.values()
    )

    quantity_values.extend(
        candidate.maximum_feasible_quantity
        for candidate in eligible_candidates
    )

    quantity_values.extend(
        shared_action_capacities.values()
    )

    quantity_values.extend(
        shared_action_minimum_quantities.values()
    )

    quantity_values.extend(
        shared_destination_capacities.values()
    )

    quantity_scale = _scale(quantity_values)

    value_per_unit = {
        candidate.candidate_id:
        _expected_value_per_unit(candidate)
        for candidate in eligible_candidates
    }

    rescue_per_unit = {
        candidate.candidate_id:
        _expected_rescue_per_unit(candidate)
        for candidate in eligible_candidates
    }

    value_scale = _scale(
        list(value_per_unit.values())
    )

    rescue_scale_values = list(
        rescue_per_unit.values()
    )

    if minimum_expected_rescue_ratio is not None:
        rescue_scale_values.append(
            minimum_expected_rescue_ratio
        )

    rescue_scale = _scale(
        rescue_scale_values
    )

    model = cp_model.CpModel()

    quantity_variables: dict[
        str,
        cp_model.IntVar,
    ] = {}

    selected_variables: dict[
        str,
        cp_model.IntVar,
    ] = {}

    for candidate in eligible_candidates:
        maximum_scaled = _to_scaled_int(
            candidate.maximum_feasible_quantity,
            quantity_scale,
        )

        quantity_variable = model.new_int_var(
            0,
            maximum_scaled,
            f"qty_{candidate.candidate_id}",
        )

        selected_variable = model.new_bool_var(
            f"selected_{candidate.candidate_id}"
        )

        quantity_variables[
            candidate.candidate_id
        ] = quantity_variable

        selected_variables[
            candidate.candidate_id
        ] = selected_variable

        model.add(
            quantity_variable
            <= maximum_scaled * selected_variable
        )

        model.add(
            quantity_variable
            >= selected_variable
        )

    # --------------------------------------------------------
    # Planning-lot quantity constraint
    # --------------------------------------------------------

    for planning_lot_id, planning_quantity in sorted(
        planning_quantities.items()
    ):
        lot_variables = [
            quantity_variables[
                candidate.candidate_id
            ]
            for candidate in eligible_candidates
            if candidate.planning_lot_id
            == planning_lot_id
        ]

        if lot_variables:
            model.add(
                sum(lot_variables)
                <= _to_scaled_int(
                    planning_quantity,
                    quantity_scale,
                )
            )

    # --------------------------------------------------------
    # Shared action capacity
    # --------------------------------------------------------

    for action_type, capacity in sorted(
        shared_action_capacities.items(),
        key=lambda item: item[0].value,
    ):
        action_variables = [
            quantity_variables[
                candidate.candidate_id
            ]
            for candidate in eligible_candidates
            if candidate.action_type is action_type
        ]

        if action_variables:
            model.add(
                sum(action_variables)
                <= _to_scaled_int(
                    capacity,
                    quantity_scale,
                )
            )

    # --------------------------------------------------------
    # Aggregate action MOQ
    # --------------------------------------------------------

    for action_type, minimum_quantity in sorted(
        shared_action_minimum_quantities.items(),
        key=lambda item: item[0].value,
    ):
        if minimum_quantity == ZERO:
            continue

        matching_candidates = [
            candidate
            for candidate in eligible_candidates
            if candidate.action_type is action_type
        ]

        if not matching_candidates:
            continue

        action_variables = [
            quantity_variables[
                candidate.candidate_id
            ]
            for candidate in matching_candidates
        ]

        total_available = sum(
            (
                candidate.maximum_feasible_quantity
                for candidate in matching_candidates
            ),
            ZERO,
        )

        if action_type in shared_action_capacities:
            total_available = min(
                total_available,
                shared_action_capacities[
                    action_type
                ],
            )

        action_used = model.new_bool_var(
            f"aggregate_action_used_{action_type.value}"
        )

        total_action_quantity = sum(
            action_variables
        )

        model.add(
            total_action_quantity
            <= (
                _to_scaled_int(
                    total_available,
                    quantity_scale,
                )
                * action_used
            )
        )

        model.add(
            total_action_quantity
            >= (
                _to_scaled_int(
                    minimum_quantity,
                    quantity_scale,
                )
                * action_used
            )
        )

    # --------------------------------------------------------
    # Shared destination capacity
    # --------------------------------------------------------

    for destination_id, capacity in sorted(
        shared_destination_capacities.items()
    ):
        destination_variables = [
            quantity_variables[
                candidate.candidate_id
            ]
            for candidate in eligible_candidates
            if candidate.destination_id
            == destination_id
        ]

        if destination_variables:
            model.add(
                sum(destination_variables)
                <= _to_scaled_int(
                    capacity,
                    quantity_scale,
                )
            )

    # --------------------------------------------------------
    # Generic shared resource capacity
    #
    # requirement = resource units consumed per allocated unit.
    # Example:
    # COLD_STORAGE = 1 per product unit.
    # --------------------------------------------------------

    for resource_id, capacity in sorted(
        shared_resource_capacities.items()
    ):
        requirements = [
            candidate_resource_requirements.get(
                candidate.candidate_id,
                {},
            ).get(
                resource_id,
                ZERO,
            )
            for candidate in eligible_candidates
        ]

        resource_scale = _scale(
            requirements + [capacity]
        )

        resource_terms = []

        for candidate, requirement in zip(
            eligible_candidates,
            requirements,
            strict=True,
        ):
            if requirement == ZERO:
                continue

            coefficient = _to_scaled_int(
                requirement,
                resource_scale,
            )

            resource_terms.append(
                coefficient
                * quantity_variables[
                    candidate.candidate_id
                ]
            )

        if resource_terms:
            capacity_rhs = _exact_int(
                capacity
                * Decimal(resource_scale)
                * Decimal(quantity_scale)
            )

            model.add(
                sum(resource_terms)
                <= capacity_rhs
            )

    # --------------------------------------------------------
    # Global fixed logistics budget
    # --------------------------------------------------------

    if max_logistics_budget is not None:
        logistics_values = [
            candidate.logistics_cost
            for candidate in eligible_candidates
        ]

        logistics_values.append(
            max_logistics_budget
        )

        logistics_scale = _scale(
            logistics_values
        )

        logistics_terms = [
            _to_scaled_int(
                candidate.logistics_cost,
                logistics_scale,
            )
            * selected_variables[
                candidate.candidate_id
            ]
            for candidate in eligible_candidates
        ]

        model.add(
            sum(logistics_terms)
            <= _to_scaled_int(
                max_logistics_budget,
                logistics_scale,
            )
        )

    # --------------------------------------------------------
    # BALANCED rescue-ratio constraint
    # --------------------------------------------------------

    rescue_terms = []

    for candidate in eligible_candidates:
        rescue_coefficient = _to_scaled_int(
            rescue_per_unit[
                candidate.candidate_id
            ],
            rescue_scale,
        )

        rescue_terms.append(
            rescue_coefficient
            * quantity_variables[
                candidate.candidate_id
            ]
        )

    if (
        optimization_objective
        is OptimizationObjective.BALANCED
    ):
        assert (
            minimum_expected_rescue_ratio
            is not None
        )

        total_planning_quantity = sum(
            planning_quantities.values(),
            ZERO,
        )

        minimum_expected_rescue = (
            minimum_expected_rescue_ratio
            * total_planning_quantity
        )

        rescue_rhs = _exact_int(
            minimum_expected_rescue
            * Decimal(quantity_scale)
            * Decimal(rescue_scale)
        )

        model.add(
            sum(rescue_terms)
            >= rescue_rhs
        )

    # --------------------------------------------------------
    # Objective
    # --------------------------------------------------------

    recovery_terms = []

    for candidate in eligible_candidates:
        coefficient = _to_scaled_int(
            value_per_unit[
                candidate.candidate_id
            ],
            value_scale,
        )

        recovery_terms.append(
            coefficient
            * quantity_variables[
                candidate.candidate_id
            ]
        )

    if (
        optimization_objective
        is OptimizationObjective.MINIMIZE_WASTE
    ):
        if rescue_terms:
            model.maximize(
                sum(rescue_terms)
            )

    else:
        if recovery_terms:
            model.maximize(
                sum(recovery_terms)
            )

    # --------------------------------------------------------
    # Solve deterministically
    # --------------------------------------------------------

    solver = cp_model.CpSolver()

    solver.parameters.num_search_workers = (
        OPTIMIZER_NUM_SEARCH_WORKERS
    )
    solver.parameters.random_seed = (
        OPTIMIZER_RANDOM_SEED
    )

    status = solver.solve(model)
    project_status = _solver_status(int(status))
    primary_project_status = project_status

    if (
        optimization_objective
        is OptimizationObjective.MINIMIZE_WASTE
        and project_status
        in {
            SolverStatus.OPTIMAL,
            SolverStatus.FEASIBLE,
        }
        and rescue_terms
        and recovery_terms
    ):
        best_rescue_objective = int(
            solver.value(
                sum(rescue_terms)
            )
        )

        model.add(
            sum(rescue_terms)
            == best_rescue_objective
        )

        model.maximize(
            sum(recovery_terms)
        )

        tie_break_status = solver.solve(model)
        tie_break_project_status = _solver_status(
            int(tie_break_status)
        )

        if tie_break_project_status in {
            SolverStatus.OPTIMAL,
            SolverStatus.FEASIBLE,
        }:
            if (
                primary_project_status
                is SolverStatus.OPTIMAL
                and tie_break_project_status
                is SolverStatus.OPTIMAL
            ):
                project_status = SolverStatus.OPTIMAL
            else:
                project_status = SolverStatus.FEASIBLE
        else:
            project_status = tie_break_project_status

    if project_status not in {
        SolverStatus.OPTIMAL,
        SolverStatus.FEASIBLE,
    }:
        return OptimizationResult(
            solver_status=project_status,
            objective_value=ZERO,
            allocations=[],
            unallocated_quantities=dict(
                planning_quantities
            ),
            total_logistics_cost=ZERO,
            shared_resource_usage={
                resource_id: ZERO
                for resource_id
                in shared_resource_capacities
            },
            expected_physical_rescue_quantity=ZERO,
        )

    # --------------------------------------------------------
    # Materialize result
    # --------------------------------------------------------

    allocations: list[
        OptimizationAllocation
    ] = []

    allocated_by_lot = {
        planning_lot_id: ZERO
        for planning_lot_id
        in planning_quantities
    }

    allocated_by_action = {
        action_type: ZERO
        for action_type
        in shared_action_capacities
    }

    allocated_by_destination = {
        destination_id: ZERO
        for destination_id
        in shared_destination_capacities
    }

    resource_usage = {
        resource_id: ZERO
        for resource_id
        in shared_resource_capacities
    }

    total_recovery = ZERO
    total_expected_rescue = ZERO
    total_logistics_cost = ZERO

    raw_allocations: list[
        tuple[
            CandidateAction,
            Decimal,
            Decimal,
            Decimal,
        ]
    ] = []

    for candidate in eligible_candidates:
        scaled_quantity = solver.value(
            quantity_variables[
                candidate.candidate_id
            ]
        )

        if scaled_quantity <= 0:
            continue

        allocated_quantity = (
            Decimal(scaled_quantity)
            / Decimal(quantity_scale)
        )

        expected_per_unit = value_per_unit[
            candidate.candidate_id
        ]

        allocation_expected_value = (
            allocated_quantity
            * expected_per_unit
        ).quantize(
            MONEY_QUANTUM,
            rounding=ROUND_HALF_UP,
        )

        allocation_expected_rescue = (
            allocated_quantity
            * rescue_per_unit[
                candidate.candidate_id
            ]
        )

        allocated_by_lot[
            candidate.planning_lot_id
        ] += allocated_quantity

        if (
            candidate.action_type
            in allocated_by_action
        ):
            allocated_by_action[
                candidate.action_type
            ] += allocated_quantity

        if (
            candidate.destination_id is not None
            and candidate.destination_id
            in allocated_by_destination
        ):
            allocated_by_destination[
                candidate.destination_id
            ] += allocated_quantity

        for resource_id in shared_resource_capacities:
            requirement = (
                candidate_resource_requirements.get(
                    candidate.candidate_id,
                    {},
                ).get(
                    resource_id,
                    ZERO,
                )
            )

            resource_usage[
                resource_id
            ] += (
                allocated_quantity
                * requirement
            )

        total_logistics_cost += (
            candidate.logistics_cost
        )

        total_recovery += (
            allocation_expected_value
        )

        total_expected_rescue += (
            allocation_expected_rescue
        )

        raw_allocations.append(
            (
                candidate,
                allocated_quantity,
                expected_per_unit,
                allocation_expected_value,
            )
        )

    # --------------------------------------------------------
    # Defensive post-solve assertions
    # --------------------------------------------------------

    for planning_lot_id, allocated in (
        allocated_by_lot.items()
    ):
        if (
            allocated
            > planning_quantities[
                planning_lot_id
            ]
        ):
            raise RuntimeError(
                "Optimizer melanggar planning quantity."
            )

    for action_type, allocated in (
        allocated_by_action.items()
    ):
        if (
            allocated
            > shared_action_capacities[
                action_type
            ]
        ):
            raise RuntimeError(
                "Optimizer melanggar shared action capacity."
            )

    for destination_id, allocated in (
        allocated_by_destination.items()
    ):
        if (
            allocated
            > shared_destination_capacities[
                destination_id
            ]
        ):
            raise RuntimeError(
                "Optimizer melanggar shared destination capacity."
            )

    for resource_id, usage in resource_usage.items():
        if (
            usage
            > shared_resource_capacities[
                resource_id
            ]
        ):
            raise RuntimeError(
                "Optimizer melanggar shared resource capacity: "
                f"{resource_id}."
            )

    if (
        max_logistics_budget is not None
        and total_logistics_cost
        > max_logistics_budget
    ):
        raise RuntimeError(
            "Optimizer melanggar global logistics budget."
        )

    if (
        optimization_objective
        is OptimizationObjective.BALANCED
    ):
        assert (
            minimum_expected_rescue_ratio
            is not None
        )

        minimum_rescue = (
            minimum_expected_rescue_ratio
            * sum(
                planning_quantities.values(),
                ZERO,
            )
        )

        if total_expected_rescue < minimum_rescue:
            raise RuntimeError(
                "Optimizer melanggar minimum expected rescue ratio."
            )

    # --------------------------------------------------------
    # Allocation contracts + binding constraints
    # --------------------------------------------------------

    for (
        candidate,
        allocated_quantity,
        expected_per_unit,
        allocation_expected_value,
    ) in raw_allocations:
        binding_constraint_codes: list[str] = []

        if (
            allocated_quantity
            == candidate.maximum_feasible_quantity
        ):
            binding_constraint_codes.append(
                "CANDIDATE_CAPACITY"
            )

        if (
            candidate.action_type
            in shared_action_capacities
            and allocated_by_action[
                candidate.action_type
            ]
            == shared_action_capacities[
                candidate.action_type
            ]
        ):
            binding_constraint_codes.append(
                "SHARED_ACTION_CAPACITY"
            )

        if (
            candidate.destination_id is not None
            and candidate.destination_id
            in shared_destination_capacities
            and allocated_by_destination[
                candidate.destination_id
            ]
            == shared_destination_capacities[
                candidate.destination_id
            ]
        ):
            binding_constraint_codes.append(
                "SHARED_DESTINATION_CAPACITY"
            )

        for resource_id, capacity in (
            shared_resource_capacities.items()
        ):
            requirement = (
                candidate_resource_requirements.get(
                    candidate.candidate_id,
                    {},
                ).get(
                    resource_id,
                    ZERO,
                )
            )

            if (
                requirement > ZERO
                and resource_usage[
                    resource_id
                ] == capacity
            ):
                binding_constraint_codes.append(
                    f"SHARED_RESOURCE_CAPACITY:{resource_id}"
                )

        if (
            max_logistics_budget is not None
            and total_logistics_cost
            == max_logistics_budget
        ):
            binding_constraint_codes.append(
                "GLOBAL_LOGISTICS_BUDGET"
            )

        allocations.append(
            OptimizationAllocation(
                allocation_id=_allocation_id(
                    candidate.candidate_id
                ),
                candidate_id=(
                    candidate.candidate_id
                ),
                planning_lot_id=(
                    candidate.planning_lot_id
                ),
                action_type=(
                    candidate.action_type
                ),
                allocated_quantity=(
                    allocated_quantity
                ),
                expected_value_per_unit=(
                    expected_per_unit
                ),
                expected_net_recovery=(
                    allocation_expected_value
                ),
                solver_status=project_status,
                binding_constraint_codes=(
                    binding_constraint_codes
                ),
            )
        )

    unallocated_quantities = {
        planning_lot_id: (
            planning_quantity
            - allocated_by_lot[
                planning_lot_id
            ]
        )
        for planning_lot_id, planning_quantity
        in sorted(planning_quantities.items())
    }

    if (
        optimization_objective
        is OptimizationObjective.MINIMIZE_WASTE
    ):
        objective_value = total_expected_rescue
    else:
        objective_value = total_recovery

    return OptimizationResult(
        solver_status=project_status,
        objective_value=objective_value,
        allocations=allocations,
        unallocated_quantities=(
            unallocated_quantities
        ),
        total_logistics_cost=(
            total_logistics_cost
        ),
        shared_resource_usage=(
            resource_usage
        ),
        expected_physical_rescue_quantity=(
            total_expected_rescue
        ),
    )


__all__ = [
    "OptimizationAllocation",
    "OptimizationResult",
    "optimize_with_cp_sat",
]
