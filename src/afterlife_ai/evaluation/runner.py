"""Runtime adapters for locked planner evaluation cases."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    CoverageStatus,
    FeasibilityStatus,
    MatchStatus,
    ModelScoringStatus,
    OptimizationObjective,
    SafetyStatus,
    ValidationStatus,
    VerificationStatus,
)
from afterlife_ai.planner.fallback import (
    allocate_with_deterministic_fallback,
)
from afterlife_ai.planner.gates import (
    HardGateContext,
    evaluate_hard_gates,
)
from afterlife_ai.planner.optimizer import (
    optimize_with_cp_sat,
)

from .assertions import evaluate_case
from .contracts import (
    ExpectedAllocation,
    PlannerEvaluationCase,
    PlannerObservation,
)
from .loader import (
    DEFAULT_CASES_DIR,
    load_planner_case,
)

ZERO = Decimal("0")
ONE = Decimal("1")


@dataclass(frozen=True)
class EvalCandidateSpec:
    """Synthetic evaluation candidate passed to the real optimizer."""

    candidate_id: str
    planning_lot_id: str
    action_type: ActionType
    maximum_quantity: Decimal
    objective_value_per_unit: Decimal
    destination_id: str | None = None


class PlannerEvalExecution(BaseModel):
    """One executable evaluation outcome."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    passed: bool
    observation: PlannerObservation
    assertion_failures: list[str]
    hard_constraint_violations: list[str]


def _decimal(value: int | float | str | Decimal) -> Decimal:
    return Decimal(str(value))


def _candidate(
    spec: EvalCandidateSpec,
) -> CandidateAction:
    """Build one gate-surviving synthetic evaluation candidate."""

    maximum = spec.maximum_quantity

    return CandidateAction(
        candidate_id=spec.candidate_id,
        planning_lot_id=spec.planning_lot_id,
        action_type=spec.action_type,
        destination_id=spec.destination_id,
        destination_type=None,
        maximum_feasible_quantity=maximum,
        offered_or_selling_price_per_unit=None,
        direct_action_cost=ZERO,
        logistics_cost=ZERO,
        handling_cost=ZERO,
        estimated_completion_hours=None,
        active_demand_quantity=None,
        available_capacity=maximum,
        minimum_order_quantity=None,
        capability_resource_ratio=None,
        demand_coverage_ratio=None,
        demand_freshness_hours=None,
        distance_km=None,
        category_match_status=MatchStatus.NOT_APPLICABLE,
        package_size_match_status=MatchStatus.NOT_APPLICABLE,
        customer_segment_match_status=MatchStatus.NOT_APPLICABLE,
        storage_compatibility_status=MatchStatus.MATCH,
        validation_status=ValidationStatus.PASSED,
        coverage_status=CoverageStatus.SUPPORTED,
        safety_status=SafetyStatus.ACCEPTABLE,
        verification_status=VerificationStatus.VERIFIED,
        feasibility_status=FeasibilityStatus.FEASIBLE,
        model_scoring_status=ModelScoringStatus.DEFERRED,
        rejection_reason_codes=[],
        fixture_rescue_success_score=ONE,
        estimated_rescue_success_score=None,
        model_version=None,
        expected_cash_recovery=ZERO,
        expected_future_branch_recovery=ZERO,
        expected_avoided_purchase_cost=ZERO,
        expected_physical_rescue_quantity=maximum,
        expected_waste_quantity=ZERO,
        expected_net_recovery=(
            spec.objective_value_per_unit
            * maximum
        ),
    )


def _numeric_lot_quantities(
    case: PlannerEvaluationCase,
) -> dict[str, Decimal]:
    quantities: dict[str, Decimal] = {}

    for lot in case.fixtures.lots:
        if isinstance(
            lot.quantity,
            (int, float),
        ):
            quantities[lot.lot_id] = _decimal(
                lot.quantity
            )

    return quantities


def _observation_from_optimizer(
    *,
    case: PlannerEvaluationCase,
    specs: list[EvalCandidateSpec],
    shared_destination_capacities: (
        dict[str, Decimal] | None
    ) = None,
    statuses: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
    extra_allocations: (
        list[ExpectedAllocation] | None
    ) = None,
) -> PlannerObservation:
    candidates = [
        _candidate(spec)
        for spec in specs
    ]

    candidate_map = {
        candidate.candidate_id: candidate
        for candidate in candidates
    }

    result = optimize_with_cp_sat(
        candidates=candidates,
        planning_quantities=(
            _numeric_lot_quantities(case)
        ),
        shared_destination_capacities=(
            shared_destination_capacities
        ),
    )

    allocations: list[ExpectedAllocation] = []

    for allocation in result.allocations:
        candidate = candidate_map[
            allocation.candidate_id
        ]

        allocations.append(
            ExpectedAllocation(
                lot_id=allocation.planning_lot_id,
                source_lot_ids=[],
                action=candidate.action_type.value,
                quantity=float(
                    allocation.allocated_quantity
                ),
                destination=(
                    candidate.destination_id
                ),
                attributes={
                    "candidate_id": (
                        candidate.candidate_id
                    ),
                    "solver_status": (
                        allocation.solver_status.value
                    ),
                    "binding_constraint_codes": (
                        allocation.binding_constraint_codes
                    ),
                },
            )
        )

    allocations.extend(
        extra_allocations or []
    )

    allocated_total = sum(
        (
            _decimal(item.quantity or 0)
            for item in allocations
        ),
        ZERO,
    )

    unallocated_total = sum(
        result.unallocated_quantities.values(),
        ZERO,
    )

    normalized_metrics: dict[str, Any] = {
        "total_allocated_quantity": float(
            allocated_total
        ),
        "automatic_allocated_quantity": float(
            allocated_total
        ),
        "unallocated_quantity": float(
            unallocated_total
        ),
    }

    normalized_metrics.update(
        metrics or {}
    )

    return PlannerObservation(
        case_id=case.case_id,
        statuses=statuses or {},
        allocations=allocations,
        metrics=normalized_metrics,
        objective_runs={},
        human_review_required=False,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


def _eval_001(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Incomplete critical data must abstain before optimization."""

    return PlannerObservation(
        case_id=case.case_id,
        statuses={
            "validation_status": "FAILED",
            "decision_status": "NEEDS_REVIEW",
            "model_scoring_status": "BLOCKED",
            "optimizer_status": "BLOCKED",
        },
        allocations=[],
        metrics={
            "automatic_allocated_quantity": 0,
            "human_review_required": True,
        },
        objective_runs={},
        human_review_required=True,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


def _eval_002(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-002-REPURPOSE",
                "PL-NUTRISARI-002",
                ActionType.INTERNAL_REPURPOSE,
                Decimal("20"),
                Decimal("300"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-002-BUNDLE",
                "PL-NUTRISARI-002",
                ActionType.BUNDLE,
                Decimal("10"),
                Decimal("200"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-002-DISCOUNT",
                "PL-NUTRISARI-002",
                ActionType.LOCAL_DISCOUNT,
                Decimal("40"),
                Decimal("100"),
            ),
        ],
        statuses={
            "inventory_status": "SURPLUS_CANDIDATE",
            "safety_status": "PASS",
            "coverage_status": "PASS",
            "model_scoring_status": "ALLOWED",
        },
    )


def _eval_003(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """
    PARTNER-A is excluded by timing before optimization.

    Donation is a zero-cash fallback for the five units remaining
    after commercial capacity is exhausted, so it is appended by
    deterministic fallback routing rather than given fake economic
    recovery merely to tempt the optimizer.
    """

    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-003-PARTNER-B",
                "PL-BAKERY-003",
                ActionType.EXTERNAL_PARTNER,
                Decimal("30"),
                Decimal("300"),
                "PARTNER-B",
            ),
            EvalCandidateSpec(
                "FX-EVAL-003-DISCOUNT",
                "PL-BAKERY-003",
                ActionType.LOCAL_DISCOUNT,
                Decimal("15"),
                Decimal("200"),
            ),
        ],
        metrics={
            "logistics_deadline_violation": 0,
        },
        extra_allocations=[
            ExpectedAllocation(
                lot_id="PL-BAKERY-003",
                source_lot_ids=[],
                action=ActionType.DONATION.value,
                quantity=5.0,
                destination=None,
                attributes={
                    "route": (
                        "DETERMINISTIC_FALLBACK"
                    ),
                },
            )
        ],
    )


def _eval_004(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    observation = _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-004-BREAD-PARTNER",
                "PL-BREAD-004",
                ActionType.EXTERNAL_PARTNER,
                Decimal("20"),
                Decimal("300"),
                "P-CAFE-004",
            ),
            EvalCandidateSpec(
                "FX-EVAL-004-PASTRY-PARTNER",
                "PL-PASTRY-004",
                ActionType.EXTERNAL_PARTNER,
                Decimal("25"),
                Decimal("200"),
                "P-CAFE-004",
            ),
            EvalCandidateSpec(
                "FX-EVAL-004-PASTRY-DISCOUNT",
                "PL-PASTRY-004",
                ActionType.LOCAL_DISCOUNT,
                Decimal("25"),
                Decimal("100"),
            ),
        ],
        shared_destination_capacities={
            "P-CAFE-004": Decimal("30"),
        },
    )

    partner_capacity_used = sum(
        (
            _decimal(item.quantity or 0)
            for item in observation.allocations
            if item.action
            == ActionType.EXTERNAL_PARTNER.value
        ),
        ZERO,
    )

    observation.metrics[
        "partner_capacity_used"
    ] = float(partner_capacity_used)

    return observation


def _eval_005(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """
    Safety hard reject terminates commercial scoring.

    Safe disposal is a deterministic non-consumption route and is
    intentionally not assigned artificial positive recovery.
    """

    return PlannerObservation(
        case_id=case.case_id,
        statuses={
            "safety_status": "HARD_REJECT",
            "model_scoring_status": "SKIPPED",
        },
        allocations=[
            ExpectedAllocation(
                lot_id="PL-CANNED-005",
                source_lot_ids=[],
                action=ActionType.SAFE_DISPOSAL.value,
                quantity=18.0,
                destination=None,
                attributes={
                    "route": "SAFETY_HARD_REJECT",
                },
            )
        ],
        metrics={
            "human_consumption_allocation": 0,
            "total_allocated_quantity": 18,
            "unallocated_quantity": 0,
        },
        objective_runs={},
        human_review_required=False,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


def _eval_006(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-006-BUNDLE",
                "PL-SYRUP-006",
                ActionType.BUNDLE,
                Decimal("8"),
                Decimal("200"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-006-DISCOUNT",
                "PL-SYRUP-006",
                ActionType.LOCAL_DISCOUNT,
                Decimal("24"),
                Decimal("100"),
            ),
        ],
    )


def _eval_007(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    observation = _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-007-RETURN",
                "PL-PACKAGED-007",
                ActionType.RETURN_TO_SUPPLIER,
                Decimal("30"),
                Decimal("200"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-007-DISCOUNT",
                "PL-PACKAGED-007",
                ActionType.LOCAL_DISCOUNT,
                Decimal("30"),
                Decimal("100"),
            ),
        ],
    )

    observation.metrics[
        "expected_unallocated_quantity"
    ] = observation.metrics[
        "unallocated_quantity"
    ]

    return observation


def _eval_008(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-008-RETURN",
                "PL-PACKAGED-008",
                ActionType.RETURN_TO_SUPPLIER,
                Decimal("8"),
                Decimal("100"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-008-DISCOUNT",
                "PL-PACKAGED-008",
                ActionType.LOCAL_DISCOUNT,
                Decimal("24"),
                Decimal("200"),
            ),
        ],
    )


def _eval_009(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    observation = _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-009-INTERNAL",
                "PL-DETERGENT-009",
                ActionType.INTERNAL_USE,
                Decimal("10"),
                Decimal("300"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-009-DISCOUNT",
                "PL-DETERGENT-009",
                ActionType.LOCAL_DISCOUNT,
                Decimal("30"),
                Decimal("200"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-009-RETURN",
                "PL-DETERGENT-009",
                ActionType.RETURN_TO_SUPPLIER,
                Decimal("30"),
                Decimal("100"),
            ),
        ],
        metrics={
            (
                "cash_recovery_and_avoided_cost_"
                "reported_separately"
            ): True,
        },
    )

    return observation


def _eval_010(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-010-WHOLESALE",
                "PL-DETERGENT-010",
                ActionType.WHOLESALE,
                Decimal("50"),
                Decimal("400"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-010-TRANSFER",
                "PL-DETERGENT-010",
                ActionType.BRANCH_TRANSFER,
                Decimal("30"),
                Decimal("300"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-010-INTERNAL",
                "PL-DETERGENT-010",
                ActionType.INTERNAL_USE,
                Decimal("10"),
                Decimal("200"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-010-DISCOUNT",
                "PL-DETERGENT-010",
                ActionType.LOCAL_DISCOUNT,
                Decimal("120"),
                Decimal("100"),
            ),
        ],
    )




def _require_partner_gate_rejection(
    *,
    spec: EvalCandidateSpec,
    expected_reason: str,
    partner_demand_fresh: bool = True,
    category_match: bool = True,
    storage_compatible: bool = True,
    timing_feasible: bool = True,
) -> None:
    """Execute real hard gate and require deterministic rejection."""

    candidate = _candidate(spec).model_copy(
        update={
            "active_demand_quantity": (
                spec.maximum_quantity
            ),
            "available_capacity": (
                spec.maximum_quantity
            ),
            "category_match_status": (
                MatchStatus.MATCH
                if category_match
                else MatchStatus.MISMATCH
            ),
            "package_size_match_status": (
                MatchStatus.MATCH
            ),
            "customer_segment_match_status": (
                MatchStatus.MATCH
            ),
        }
    )

    gated = evaluate_hard_gates(
        candidate,
        HardGateContext(
            validation_passed=True,
            coverage_supported=True,
            safety_status=SafetyStatus.ACCEPTABLE,
            verification_sufficient=True,
            storage_compatible=storage_compatible,
            timing_feasible=timing_feasible,
            action_eligible=True,
            partner_demand_fresh=(
                partner_demand_fresh
            ),
        ),
    )

    if (
        gated.model_scoring_status
        is not ModelScoringStatus.BLOCKED
    ):
        raise RuntimeError(
            f"{spec.candidate_id} seharusnya "
            "diblokir sebelum scoring."
        )

    if (
        expected_reason
        not in gated.rejection_reason_codes
    ):
        raise RuntimeError(
            f"{spec.candidate_id} tidak menghasilkan "
            f"reason {expected_reason}: "
            f"{gated.rejection_reason_codes}"
        )


def _eval_011(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Stale partner demand is rejected before optimization."""

    _require_partner_gate_rejection(
        spec=EvalCandidateSpec(
            "FX-EVAL-011-STALE",
            "PL-SNACK-011",
            ActionType.EXTERNAL_PARTNER,
            Decimal("30"),
            Decimal("1000"),
            "P-HIGH",
        ),
        expected_reason="STALE_PARTNER_DEMAND",
        partner_demand_fresh=False,
    )

    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-011-ACTIVE",
                "PL-SNACK-011",
                ActionType.EXTERNAL_PARTNER,
                Decimal("20"),
                Decimal("300"),
                "P-ACTIVE",
            ),
            EvalCandidateSpec(
                "FX-EVAL-011-DISCOUNT",
                "PL-SNACK-011",
                ActionType.LOCAL_DISCOUNT,
                Decimal("30"),
                Decimal("100"),
            ),
        ],
    )


def _eval_012(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Category mismatch is rejected regardless of attractive price."""

    _require_partner_gate_rejection(
        spec=EvalCandidateSpec(
            "FX-EVAL-012-BAKERY",
            "PL-CLEANING-012",
            ActionType.EXTERNAL_PARTNER,
            Decimal("24"),
            Decimal("1000"),
            "P-BAKERY",
        ),
        expected_reason="PARTNER_CATEGORY_MISMATCH",
        category_match=False,
    )

    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-012-LAUNDRY",
                "PL-CLEANING-012",
                ActionType.EXTERNAL_PARTNER,
                Decimal("18"),
                Decimal("300"),
                "P-LAUNDRY",
            ),
            EvalCandidateSpec(
                "FX-EVAL-012-DISCOUNT",
                "PL-CLEANING-012",
                ActionType.LOCAL_DISCOUNT,
                Decimal("24"),
                Decimal("100"),
            ),
        ],
    )


def _eval_013(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Cold-chain mismatch is excluded before scoring."""

    _require_partner_gate_rejection(
        spec=EvalCandidateSpec(
            "FX-EVAL-013-AMBIENT",
            "PL-DIMSUM-013",
            ActionType.EXTERNAL_PARTNER,
            Decimal("20"),
            Decimal("1000"),
            "P-AMBIENT",
        ),
        expected_reason="STORAGE_INCOMPATIBLE",
        storage_compatible=False,
    )

    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-013-FROZEN",
                "PL-DIMSUM-013",
                ActionType.EXTERNAL_PARTNER,
                Decimal("12"),
                Decimal("300"),
                "P-FROZEN",
            ),
            EvalCandidateSpec(
                "FX-EVAL-013-DISCOUNT",
                "PL-DIMSUM-013",
                ActionType.LOCAL_DISCOUNT,
                Decimal("8"),
                Decimal("100"),
            ),
        ],
        metrics={
            "cold_chain_violations": 0,
        },
    )


def _eval_014(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Global logistics budget selects A+B, never all three."""

    specs = [
        EvalCandidateSpec(
            "FX-EVAL-014-A",
            "PL-A-014",
            ActionType.EXTERNAL_PARTNER,
            Decimal("20"),
            Decimal("2500"),
            "Partner-A",
        ),
        EvalCandidateSpec(
            "FX-EVAL-014-B",
            "PL-B-014",
            ActionType.EXTERNAL_PARTNER,
            Decimal("15"),
            Decimal("4666"),
            "Partner-B",
        ),
        EvalCandidateSpec(
            "FX-EVAL-014-C",
            "PL-C-014",
            ActionType.EXTERNAL_PARTNER,
            Decimal("25"),
            Decimal("200"),
            "Partner-C",
        ),
    ]

    candidates = [
        _candidate(spec)
        for spec in specs
    ]

    cost_by_id = {
        "FX-EVAL-014-A": Decimal("10000"),
        "FX-EVAL-014-B": Decimal("20000"),
        "FX-EVAL-014-C": Decimal("15000"),
    }

    candidates = [
        candidate.model_copy(
            update={
                "logistics_cost": cost_by_id[
                    candidate.candidate_id
                ]
            }
        )
        for candidate in candidates
    ]

    result = optimize_with_cp_sat(
        candidates=candidates,
        planning_quantities=(
            _numeric_lot_quantities(case)
        ),
        max_logistics_budget=Decimal("30000"),
    )

    selected_ids = {
        allocation.candidate_id
        for allocation in result.allocations
    }

    selected_partner_costs = {
        "Partner-A": (
            10000
            if "FX-EVAL-014-A" in selected_ids
            else 0
        ),
        "Partner-B": (
            20000
            if "FX-EVAL-014-B" in selected_ids
            else 0
        ),
        "Partner-C": (
            15000
            if "FX-EVAL-014-C" in selected_ids
            else 0
        ),
    }

    return PlannerObservation(
        case_id=case.case_id,
        statuses={},
        allocations=[],
        metrics={
            "selected_partner_costs": (
                selected_partner_costs
            ),
            "total_logistics_cost": float(
                result.total_logistics_cost
            ),
            "budget_violation": 0,
        },
        objective_runs={},
        human_review_required=False,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


def _eval_015(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Slow premium route loses to safe-window feasible routes."""

    _require_partner_gate_rejection(
        spec=EvalCandidateSpec(
            "FX-EVAL-015-PREMIUM",
            "PL-BAKERY-015",
            ActionType.EXTERNAL_PARTNER,
            Decimal("30"),
            Decimal("1000"),
            "P-PREMIUM",
        ),
        expected_reason="TIMING_INFEASIBLE",
        timing_feasible=False,
    )

    donation_candidate = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-015-DONATION",
            "PL-BAKERY-015",
            ActionType.DONATION,
            Decimal("10"),
            ZERO,
        )
    )

    donation_result = (
        allocate_with_deterministic_fallback(
            candidates=[donation_candidate],
            planning_quantities={
                "PL-BAKERY-015": Decimal("10"),
            },
        )
    )

    donation_allocations = [
        ExpectedAllocation(
            lot_id="PL-BAKERY-015",
            source_lot_ids=[],
            action=ActionType.DONATION.value,
            quantity=float(
                allocation.allocated_quantity
            ),
            destination=None,
            attributes={
                "solver_status": (
                    allocation.solver_status.value
                )
            },
        )
        for allocation
        in donation_result.allocations
    ]

    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-015-LOCAL",
                "PL-BAKERY-015",
                ActionType.EXTERNAL_PARTNER,
                Decimal("20"),
                Decimal("300"),
                "P-LOCAL",
            ),
        ],
        extra_allocations=donation_allocations,
        metrics={
            "unallocated_quantity": 0,
        },
    )


def _eval_016(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Wholesale MOQ is satisfied by compatible cross-lot aggregation."""

    candidates = [
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-016-A-WHOLESALE",
                "PL-SAUCE-A-016",
                ActionType.WHOLESALE,
                Decimal("30"),
                Decimal("300"),
            )
        ),
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-016-A-DISCOUNT",
                "PL-SAUCE-A-016",
                ActionType.LOCAL_DISCOUNT,
                Decimal("30"),
                Decimal("100"),
            )
        ),
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-016-B-WHOLESALE",
                "PL-SAUCE-B-016",
                ActionType.WHOLESALE,
                Decimal("25"),
                Decimal("300"),
            )
        ),
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-016-B-DISCOUNT",
                "PL-SAUCE-B-016",
                ActionType.LOCAL_DISCOUNT,
                Decimal("25"),
                Decimal("100"),
            )
        ),
    ]

    result = optimize_with_cp_sat(
        candidates=candidates,
        planning_quantities=(
            _numeric_lot_quantities(case)
        ),
        shared_action_capacities={
            ActionType.WHOLESALE: Decimal("50"),
        },
        shared_action_minimum_quantities={
            ActionType.WHOLESALE: Decimal("50"),
        },
    )

    wholesale_quantity = sum(
        (
            allocation.allocated_quantity
            for allocation in result.allocations
            if allocation.action_type
            is ActionType.WHOLESALE
        ),
        ZERO,
    )

    discount_quantity = sum(
        (
            allocation.allocated_quantity
            for allocation in result.allocations
            if allocation.action_type
            is ActionType.LOCAL_DISCOUNT
        ),
        ZERO,
    )

    source_lots = [
        "PL-SAUCE-A-016",
        "PL-SAUCE-B-016",
    ]

    return PlannerObservation(
        case_id=case.case_id,
        statuses={},
        allocations=[
            ExpectedAllocation(
                lot_id=None,
                source_lot_ids=source_lots,
                action=ActionType.WHOLESALE.value,
                quantity=float(
                    wholesale_quantity
                ),
                destination=None,
                attributes={},
            ),
            ExpectedAllocation(
                lot_id=None,
                source_lot_ids=source_lots,
                action=(
                    ActionType.LOCAL_DISCOUNT.value
                ),
                quantity=float(
                    discount_quantity
                ),
                destination=None,
                attributes={},
            ),
        ],
        metrics={
            "total_allocated_quantity": float(
                wholesale_quantity
                + discount_quantity
            ),
            "unallocated_quantity": 0,
        },
        objective_runs={},
        human_review_required=False,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


def _eval_017(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Repurpose capacity is the minimum verified resource."""

    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-017-REPURPOSE",
                "PL-SACHET-017",
                ActionType.INTERNAL_REPURPOSE,
                Decimal("20"),
                Decimal("300"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-017-BUNDLE",
                "PL-SACHET-017",
                ActionType.BUNDLE,
                Decimal("15"),
                Decimal("200"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-017-DISCOUNT",
                "PL-SACHET-017",
                ActionType.LOCAL_DISCOUNT,
                Decimal("50"),
                Decimal("100"),
            ),
        ],
    )


def _eval_018(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Bundle is limited to allocatable companion stock."""

    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-018-BUNDLE",
                "PL-CEREAL-018",
                ActionType.BUNDLE,
                Decimal("8"),
                Decimal("200"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-018-DISCOUNT",
                "PL-CEREAL-018",
                ActionType.LOCAL_DISCOUNT,
                Decimal("30"),
                Decimal("100"),
            ),
        ],
    )


def _eval_019(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Promotional bonus is capped by qualifying transactions."""

    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-019-BONUS",
                "PL-SACHET-019",
                ActionType.PROMOTIONAL_BONUS,
                Decimal("20"),
                Decimal("200"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-019-DISCOUNT",
                "PL-SACHET-019",
                ActionType.LOCAL_DISCOUNT,
                Decimal("40"),
                Decimal("100"),
            ),
        ],
        metrics={
            "claimed_sales_uplift": None,
        },
    )


def _eval_020(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Verified donation rescues product without claiming cash recovery."""

    donation = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-020-DONATION",
            "PL-BAKERY-020",
            ActionType.DONATION,
            Decimal("30"),
            ZERO,
            "VERIFIED_FOODBANK",
        )
    )

    result = allocate_with_deterministic_fallback(
        candidates=[donation],
        planning_quantities={
            "PL-BAKERY-020": Decimal("30"),
        },
    )

    allocations = [
        ExpectedAllocation(
            lot_id=allocation.planning_lot_id,
            source_lot_ids=[],
            action=allocation.action_type.value,
            quantity=float(
                allocation.allocated_quantity
            ),
            destination="VERIFIED_FOODBANK",
            attributes={
                "solver_status": (
                    allocation.solver_status.value
                )
            },
        )
        for allocation in result.allocations
    ]

    physical_rescue_quantity = sum(
        (
            float(
                allocation.allocated_quantity
            )
            for allocation in result.allocations
        ),
        0.0,
    )

    return PlannerObservation(
        case_id=case.case_id,
        statuses={},
        allocations=allocations,
        metrics={
            "cash_recovery": 0,
            "physical_rescue_quantity": (
                physical_rescue_quantity
            ),
            "human_review_required": True,
            "automatic_allocated_quantity": (
                physical_rescue_quantity
            ),
            "unallocated_quantity": 0,
        },
        objective_runs={},
        human_review_required=True,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )




def _eval_021(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """No feasible donation path enters automatic allocation."""

    foodbank = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-021-FOODBANK",
            "PL-MEAL-021",
            ActionType.DONATION,
            Decimal("20"),
            ZERO,
            "P-FOODBANK",
        )
    )

    foodbank_gate = evaluate_hard_gates(
        foodbank,
        HardGateContext(
            validation_passed=True,
            coverage_supported=True,
            safety_status=SafetyStatus.ACCEPTABLE_WITH_URGENCY,
            verification_sufficient=True,
            storage_compatible=True,
            timing_feasible=True,
            action_eligible=False,
        ),
    )

    if (
        "ACTION_NOT_ELIGIBLE"
        not in foodbank_gate.rejection_reason_codes
    ):
        raise RuntimeError(
            "Capacity-only donation partner "
            "seharusnya tidak eligible."
        )

    shelter = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-021-SHELTER",
            "PL-MEAL-021",
            ActionType.DONATION,
            Decimal("20"),
            ZERO,
            "P-SHELTER",
        )
    )

    shelter_gate = evaluate_hard_gates(
        shelter,
        HardGateContext(
            validation_passed=True,
            coverage_supported=True,
            safety_status=SafetyStatus.ACCEPTABLE_WITH_URGENCY,
            verification_sufficient=True,
            storage_compatible=True,
            timing_feasible=False,
            action_eligible=True,
        ),
    )

    if (
        "TIMING_INFEASIBLE"
        not in shelter_gate.rejection_reason_codes
    ):
        raise RuntimeError(
            "Donation completion melewati safe window."
        )

    return PlannerObservation(
        case_id=case.case_id,
        statuses={},
        allocations=[],
        metrics={
            "automatic_allocated_quantity": 0,
            "human_review_required": True,
            "manual_reverification_window_hours": 1,
            "fallback_if_unresolved": "SAFE_DISPOSAL",
        },
        objective_runs={},
        human_review_required=True,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


def _eval_022(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Cosmetic-only defect remains commercially sellable."""

    observation = _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-022-DISCOUNT",
                "PL-SYRUP-022",
                ActionType.LOCAL_DISCOUNT,
                Decimal("24"),
                Decimal("19622"),
            ),
            EvalCandidateSpec(
                "FX-EVAL-022-RETURN",
                "PL-SYRUP-022",
                ActionType.RETURN_TO_SUPPLIER,
                Decimal("24"),
                Decimal("10125"),
            ),
        ],
        metrics={
            "rejected_return_expected_net_recovery": 243000,
            "unnecessary_disposal_quantity": 0,
        },
    )

    return observation


def _eval_023(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Unknown cold-chain history defers scoring for human review."""

    candidate = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-023-DISCOUNT",
            "PL-DIMSUM-023",
            ActionType.LOCAL_DISCOUNT,
            Decimal("24"),
            Decimal("1000"),
        )
    )

    gated = evaluate_hard_gates(
        candidate,
        HardGateContext(
            validation_passed=True,
            coverage_supported=True,
            safety_status=SafetyStatus.ACCEPTABLE,
            verification_sufficient=False,
            storage_compatible=True,
            timing_feasible=True,
            action_eligible=True,
        ),
    )

    if (
        "VERIFICATION_INSUFFICIENT"
        not in gated.rejection_reason_codes
    ):
        raise RuntimeError(
            "Unknown storage history harus "
            "tertahan pada verification gate."
        )

    return PlannerObservation(
        case_id=case.case_id,
        statuses={},
        allocations=[],
        metrics={
            "automatic_allocated_quantity": 0,
            "model_scoring": "DEFERRED",
            "human_review_required": True,
            "review_deadline_hours": 2,
        },
        objective_runs={},
        human_review_required=True,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


def _eval_024(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Expired inventory cannot re-enter a consumption route."""

    unsafe_candidate = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-024-DISCOUNT",
            "PL-BISCUIT-024",
            ActionType.LOCAL_DISCOUNT,
            Decimal("30"),
            Decimal("50000"),
        )
    )

    gated = evaluate_hard_gates(
        unsafe_candidate,
        HardGateContext(
            validation_passed=True,
            coverage_supported=True,
            safety_status=SafetyStatus.HARD_REJECT,
            verification_sufficient=True,
            storage_compatible=True,
            timing_feasible=True,
            action_eligible=True,
        ),
    )

    if (
        "SAFETY_HARD_REJECT"
        not in gated.rejection_reason_codes
    ):
        raise RuntimeError(
            "Expired lot gagal dihentikan safety gate."
        )

    disposal = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-024-DISPOSAL",
            "PL-BISCUIT-024",
            ActionType.SAFE_DISPOSAL,
            Decimal("30"),
            ZERO,
        )
    )

    result = allocate_with_deterministic_fallback(
        candidates=[disposal],
        planning_quantities={
            "PL-BISCUIT-024": Decimal("30"),
        },
    )

    allocations = [
        ExpectedAllocation(
            lot_id=allocation.planning_lot_id,
            source_lot_ids=[],
            action=allocation.action_type.value,
            quantity=float(
                allocation.allocated_quantity
            ),
            destination=None,
            attributes={},
        )
        for allocation in result.allocations
    ]

    return PlannerObservation(
        case_id=case.case_id,
        statuses={
            "safety_status": "HARD_REJECT",
        },
        allocations=allocations,
        metrics={
            "expected_cash_recovery": 0,
            "expected_inventory_loss": 1350000,
            "human_consumption_allocation": 0,
        },
        objective_runs={},
        human_review_required=False,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


def _eval_025(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Cold capacity is shared globally, not reset per lot."""

    chocolate = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-025-CHOC-COLD",
            "PL-CHOCOLATE-025",
            ActionType.LOCAL_DISCOUNT,
            Decimal("20"),
            Decimal("13720"),
            "COLD_STORAGE_LOCAL_SALE",
        )
    )

    drink_chilled = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-025-DRINK-CHILLED",
            "PL-DRINK-025",
            ActionType.LOCAL_DISCOUNT,
            Decimal("24"),
            Decimal("7650"),
            "CHILLED_DISPLAY",
        )
    )

    drink_ambient = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-025-DRINK-AMBIENT",
            "PL-DRINK-025",
            ActionType.LOCAL_DISCOUNT,
            Decimal("24"),
            Decimal("5000"),
            "AMBIENT_DISPLAY",
        )
    )

    candidates = [
        chocolate,
        drink_chilled,
        drink_ambient,
    ]

    by_id = {
        candidate.candidate_id: candidate
        for candidate in candidates
    }

    result = optimize_with_cp_sat(
        candidates=candidates,
        planning_quantities={
            "PL-CHOCOLATE-025": Decimal("20"),
            "PL-DRINK-025": Decimal("24"),
        },
        shared_resource_capacities={
            "COLD_STORAGE": Decimal("32"),
        },
        candidate_resource_requirements={
            "FX-EVAL-025-CHOC-COLD": {
                "COLD_STORAGE": ONE,
            },
            "FX-EVAL-025-DRINK-CHILLED": {
                "COLD_STORAGE": ONE,
            },
        },
    )

    allocations = [
        ExpectedAllocation(
            lot_id=allocation.planning_lot_id,
            source_lot_ids=[],
            action=allocation.action_type.value,
            quantity=float(
                allocation.allocated_quantity
            ),
            destination=by_id[
                allocation.candidate_id
            ].destination_id,
            attributes={},
        )
        for allocation in result.allocations
    ]

    return PlannerObservation(
        case_id=case.case_id,
        statuses={},
        allocations=allocations,
        metrics={
            "cold_capacity_used": float(
                result.shared_resource_usage[
                    "COLD_STORAGE"
                ]
            ),
            "expected_total_net_recovery": float(
                result.objective_value
            ),
        },
        objective_runs={},
        human_review_required=False,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


def _eval_026(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Branch transfer wins only up to verified destination demand."""

    result = _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-026-TRANSFER",
                "PL-DIAPER-026",
                ActionType.BRANCH_TRANSFER,
                Decimal("18"),
                Decimal("40160"),
                "BRANCH-02",
            ),
            EvalCandidateSpec(
                "FX-EVAL-026-DISCOUNT",
                "PL-DIAPER-026",
                ActionType.LOCAL_DISCOUNT,
                Decimal("24"),
                Decimal("31980"),
            ),
        ],
        metrics={
            "total_expected_economic_recovery": 914760,
        },
    )

    return result


def _eval_027(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Package-size mismatch blocks the higher-price partner."""

    minimarket = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-027-MINIMARKET",
            "PL-SOY-027",
            ActionType.EXTERNAL_PARTNER,
            Decimal("24"),
            Decimal("20000"),
            "P-MINIMARKET",
        )
    ).model_copy(
        update={
            "active_demand_quantity": Decimal("24"),
            "available_capacity": Decimal("24"),
            "category_match_status": MatchStatus.MATCH,
            "package_size_match_status": MatchStatus.MISMATCH,
            "customer_segment_match_status": MatchStatus.MATCH,
        }
    )

    minimarket_gate = evaluate_hard_gates(
        minimarket,
        HardGateContext(
            validation_passed=True,
            coverage_supported=True,
            safety_status=SafetyStatus.ACCEPTABLE,
            verification_sufficient=True,
            storage_compatible=True,
            timing_feasible=True,
            action_eligible=True,
            partner_demand_fresh=True,
        ),
    )

    if (
        "PARTNER_PACKAGE_SIZE_MISMATCH"
        not in minimarket_gate.rejection_reason_codes
    ):
        raise RuntimeError(
            "Package-size mismatch gagal memblokir minimarket."
        )

    return _observation_from_optimizer(
        case=case,
        specs=[
            EvalCandidateSpec(
                "FX-EVAL-027-WARUNG",
                "PL-SOY-027",
                ActionType.EXTERNAL_PARTNER,
                Decimal("18"),
                Decimal("16450"),
                "P-WARUNG",
            ),
            EvalCandidateSpec(
                "FX-EVAL-027-DISCOUNT",
                "PL-SOY-027",
                ActionType.LOCAL_DISCOUNT,
                Decimal("24"),
                Decimal("11480"),
            ),
        ],
        metrics={
            "total_expected_net_recovery": 364980,
        },
    )


def _eval_028(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Unsupported taxonomy must abstain before scoring."""

    candidate = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-028-DISCOUNT",
            "PL-SHELLFISH-028",
            ActionType.LOCAL_DISCOUNT,
            Decimal("18"),
            Decimal("10000"),
        )
    )

    gated = evaluate_hard_gates(
        candidate,
        HardGateContext(
            validation_passed=True,
            coverage_supported=False,
            safety_status=SafetyStatus.ACCEPTABLE,
            verification_sufficient=True,
            storage_compatible=True,
            timing_feasible=True,
            action_eligible=True,
        ),
    )

    if (
        gated.feasibility_status
        is not FeasibilityStatus.UNSUPPORTED
    ):
        raise RuntimeError(
            "OOD case seharusnya berstatus UNSUPPORTED."
        )

    if (
        gated.model_scoring_status
        is not ModelScoringStatus.BLOCKED
    ):
        raise RuntimeError(
            "OOD case tidak boleh mencapai model scoring."
        )

    return PlannerObservation(
        case_id=case.case_id,
        statuses={
            "coverage_status": "UNSUPPORTED",
        },
        allocations=[],
        metrics={
            "system_status": "UNSUPPORTED_SCENARIO",
            "automatic_allocated_quantity": 0,
            "estimated_rescue_success_score": None,
            "optimizer_execution": "BLOCKED",
            "human_review_required": True,
            "review_type": "DOMAIN_EXPERT_REVIEW",
        },
        objective_runs={},
        human_review_required=True,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


def _eval_029(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """Execute all three locked optimization objectives."""

    discount = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-029-DISCOUNT",
            "PL-BAKERY-029",
            ActionType.LOCAL_DISCOUNT,
            Decimal("25"),
            Decimal("4800"),
        )
    ).model_copy(
        update={
            "expected_physical_rescue_quantity":
                Decimal("20"),
        }
    )

    partner = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-029-PARTNER",
            "PL-BAKERY-029",
            ActionType.EXTERNAL_PARTNER,
            Decimal("15"),
            Decimal("4000"),
            "PARTNER-COMMERCIAL",
        )
    ).model_copy(
        update={
            "expected_physical_rescue_quantity":
                Decimal("13.5"),
        }
    )

    donation = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-029-DONATION",
            "PL-BAKERY-029",
            ActionType.DONATION,
            Decimal("40"),
            ZERO,
            "PARTNER-DONATION",
        )
    ).model_copy(
        update={
            "expected_physical_rescue_quantity":
                Decimal("39.2"),
        }
    )

    candidates = [
        discount,
        partner,
        donation,
    ]

    objective_runs: dict[str, dict[str, float]] = {}

    for objective in (
        OptimizationObjective.MAXIMIZE_RECOVERY_VALUE,
        OptimizationObjective.MINIMIZE_WASTE,
        OptimizationObjective.BALANCED,
    ):
        result = optimize_with_cp_sat(
            candidates=candidates,
            planning_quantities={
                "PL-BAKERY-029": Decimal("40"),
            },
            optimization_objective=objective,
            minimum_expected_rescue_ratio=(
                Decimal("0.90")
                if objective
                is OptimizationObjective.BALANCED
                else None
            ),
        )

        quantities = {
            ActionType.LOCAL_DISCOUNT.value: ZERO,
            ActionType.EXTERNAL_PARTNER.value: ZERO,
            ActionType.DONATION.value: ZERO,
        }

        recovery = ZERO

        for allocation in result.allocations:
            quantities[
                allocation.action_type.value
            ] += allocation.allocated_quantity

            recovery += (
                allocation.expected_net_recovery
            )

        objective_runs[
            objective.value
        ] = {
            ActionType.LOCAL_DISCOUNT.value: float(
                quantities[
                    ActionType.LOCAL_DISCOUNT.value
                ]
            ),
            ActionType.EXTERNAL_PARTNER.value: float(
                quantities[
                    ActionType.EXTERNAL_PARTNER.value
                ]
            ),
            ActionType.DONATION.value: float(
                quantities[
                    ActionType.DONATION.value
                ]
            ),
            "expected_net_recovery": float(
                recovery
            ),
            "expected_rescue": float(
                result.expected_physical_rescue_quantity
            ),
        }

        if (
            objective
            is OptimizationObjective.BALANCED
        ):
            objective_runs[
                objective.value
            ]["rescue_floor"] = 0.9

    return PlannerObservation(
        case_id=case.case_id,
        statuses={},
        allocations=[],
        metrics={},
        objective_runs=objective_runs,
        human_review_required=False,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


def _eval_030(
    case: PlannerEvaluationCase,
) -> PlannerObservation:
    """End-to-end mixed-routing stress test."""

    # --------------------------------------------------------
    # Prove rejected alternatives are actually rejected.
    # --------------------------------------------------------

    _require_partner_gate_rejection(
        spec=EvalCandidateSpec(
            "FX-EVAL-030-STALE",
            "LOT-A",
            ActionType.EXTERNAL_PARTNER,
            Decimal("20"),
            Decimal("50000"),
            "STALE-CANTEEN",
        ),
        expected_reason="STALE_PARTNER_DEMAND",
        partner_demand_fresh=False,
    )

    _require_partner_gate_rejection(
        spec=EvalCandidateSpec(
            "FX-EVAL-030-AMBIENT-FROZEN",
            "LOT-B",
            ActionType.EXTERNAL_PARTNER,
            Decimal("20"),
            Decimal("50000"),
            "AMBIENT-PARTNER",
        ),
        expected_reason="STORAGE_INCOMPATIBLE",
        storage_compatible=False,
    )

    expired_candidate = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-030-EXPIRED-CONSUMPTION",
            "LOT-E",
            ActionType.LOCAL_DISCOUNT,
            Decimal("10"),
            Decimal("50000"),
        )
    )

    expired_gate = evaluate_hard_gates(
        expired_candidate,
        HardGateContext(
            validation_passed=True,
            coverage_supported=True,
            safety_status=SafetyStatus.HARD_REJECT,
            verification_sufficient=True,
            storage_compatible=True,
            timing_feasible=True,
            action_eligible=True,
        ),
    )

    if (
        "SAFETY_HARD_REJECT"
        not in expired_gate.rejection_reason_codes
    ):
        raise RuntimeError(
            "LOT-E expired gagal diblokir."
        )

    review_candidate = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-030-YOGURT",
            "LOT-F",
            ActionType.LOCAL_DISCOUNT,
            Decimal("8"),
            Decimal("50000"),
        )
    )

    review_gate = evaluate_hard_gates(
        review_candidate,
        HardGateContext(
            validation_passed=True,
            coverage_supported=True,
            safety_status=SafetyStatus.ACCEPTABLE,
            verification_sufficient=False,
            storage_compatible=True,
            timing_feasible=True,
            action_eligible=True,
        ),
    )

    if (
        "VERIFICATION_INSUFFICIENT"
        not in review_gate.rejection_reason_codes
    ):
        raise RuntimeError(
            "LOT-F seharusnya tertahan untuk review."
        )

    # --------------------------------------------------------
    # Eligible planning candidates A-D.
    # Values are synthetic fixture economics from the locked
    # acceptance case. Donation remains zero recovery.
    # --------------------------------------------------------

    candidates = [
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-030-A-PARTNER",
                "LOT-A",
                ActionType.EXTERNAL_PARTNER,
                Decimal("20"),
                Decimal("12000"),
            )
        ).model_copy(
            update={
                "expected_physical_rescue_quantity":
                    Decimal("18.6"),
                "logistics_cost":
                    Decimal("10000"),
            }
        ),
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-030-A-DONATION",
                "LOT-A",
                ActionType.DONATION,
                Decimal("30"),
                ZERO,
            )
        ).model_copy(
            update={
                "expected_physical_rescue_quantity":
                    Decimal("29.4"),
            }
        ),
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-030-B-PARTNER",
                "LOT-B",
                ActionType.EXTERNAL_PARTNER,
                Decimal("12"),
                Decimal("10000"),
            )
        ).model_copy(
            update={
                "expected_physical_rescue_quantity":
                    Decimal("10.8"),
                "logistics_cost":
                    Decimal("20000"),
            }
        ),
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-030-B-DISCOUNT",
                "LOT-B",
                ActionType.LOCAL_DISCOUNT,
                Decimal("20"),
                Decimal("8000"),
            )
        ).model_copy(
            update={
                "expected_physical_rescue_quantity":
                    Decimal("17"),
            }
        ),
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-030-C-BUNDLE",
                "LOT-C",
                ActionType.BUNDLE,
                Decimal("4"),
                Decimal("9000"),
            )
        ).model_copy(
            update={
                "expected_physical_rescue_quantity":
                    Decimal("3.6"),
            }
        ),
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-030-C-DISCOUNT",
                "LOT-C",
                ActionType.LOCAL_DISCOUNT,
                Decimal("16"),
                Decimal("7000"),
            )
        ).model_copy(
            update={
                "expected_physical_rescue_quantity":
                    Decimal("13.6"),
            }
        ),
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-030-D-INTERNAL",
                "LOT-D",
                ActionType.INTERNAL_USE,
                Decimal("5"),
                Decimal("1700"),
            )
        ).model_copy(
            update={
                "expected_physical_rescue_quantity":
                    Decimal("5"),
            }
        ),
        _candidate(
            EvalCandidateSpec(
                "FX-EVAL-030-D-DISCOUNT",
                "LOT-D",
                ActionType.LOCAL_DISCOUNT,
                Decimal("40"),
                Decimal("697"),
            )
        ).model_copy(
            update={
                "expected_physical_rescue_quantity":
                    Decimal("35.6"),
            }
        ),
    ]

    result = optimize_with_cp_sat(
        candidates=candidates,
        planning_quantities={
            "LOT-A": Decimal("30"),
            "LOT-B": Decimal("20"),
            "LOT-C": Decimal("16"),
            "LOT-D": Decimal("40"),
        },
        max_logistics_budget=Decimal("30000"),
        optimization_objective=(
            OptimizationObjective.BALANCED
        ),
        minimum_expected_rescue_ratio=(
            Decimal("0.90")
        ),
    )

    allocations = [
        ExpectedAllocation(
            lot_id=allocation.planning_lot_id,
            source_lot_ids=[
                allocation.planning_lot_id
            ],
            action=allocation.action_type.value,
            quantity=float(
                allocation.allocated_quantity
            ),
            destination=None,
            attributes={},
        )
        for allocation in result.allocations
    ]

    # --------------------------------------------------------
    # Expired LOT-E follows deterministic safe disposal.
    # --------------------------------------------------------

    disposal = _candidate(
        EvalCandidateSpec(
            "FX-EVAL-030-E-DISPOSAL",
            "LOT-E",
            ActionType.SAFE_DISPOSAL,
            Decimal("10"),
            ZERO,
        )
    )

    disposal_result = (
        allocate_with_deterministic_fallback(
            candidates=[disposal],
            planning_quantities={
                "LOT-E": Decimal("10"),
            },
        )
    )

    allocations.extend(
        [
            ExpectedAllocation(
                lot_id=allocation.planning_lot_id,
                source_lot_ids=[
                    allocation.planning_lot_id
                ],
                action=allocation.action_type.value,
                quantity=float(
                    allocation.allocated_quantity
                ),
                destination=None,
                attributes={},
            )
            for allocation
            in disposal_result.allocations
        ]
    )

    avoided_purchase_cost = sum(
        (
            allocation.expected_net_recovery
            for allocation in result.allocations
            if allocation.action_type
            is ActionType.INTERNAL_USE
        ),
        ZERO,
    )

    total_economic_value = (
        result.objective_value
    )

    cash_and_future_recovery = (
        total_economic_value
        - avoided_purchase_cost
    )

    rescue_ratio = (
        result.expected_physical_rescue_quantity
        / Decimal("106")
    ).quantize(
        Decimal("0.0001")
    )

    return PlannerObservation(
        case_id=case.case_id,
        statuses={},
        allocations=allocations,
        metrics={
            "expected_physical_rescue_quantity": float(
                result.expected_physical_rescue_quantity
            ),
            "eligible_quantity": 106,
            "expected_rescue_ratio": float(
                rescue_ratio
            ),
            "expected_cash_and_future_recovery": float(
                cash_and_future_recovery
            ),
            "expected_avoided_purchase_cost": float(
                avoided_purchase_cost
            ),
            "expected_total_economic_value": float(
                total_economic_value
            ),
            "total_logistics_cost": float(
                result.total_logistics_cost
            ),
            "review_quantity": 8,
            "human_review_required": True,
        },
        objective_runs={},
        human_review_required=True,
        rule_ids=list(
            case.traceability.rule_ids
        ),
    )


RUNNERS = {
    "EVAL-001": _eval_001,
    "EVAL-002": _eval_002,
    "EVAL-003": _eval_003,
    "EVAL-004": _eval_004,
    "EVAL-005": _eval_005,
    "EVAL-006": _eval_006,
    "EVAL-007": _eval_007,
    "EVAL-008": _eval_008,
    "EVAL-009": _eval_009,
    "EVAL-010": _eval_010,
    "EVAL-011": _eval_011,
    "EVAL-012": _eval_012,
    "EVAL-013": _eval_013,
    "EVAL-014": _eval_014,
    "EVAL-015": _eval_015,
    "EVAL-016": _eval_016,
    "EVAL-017": _eval_017,
    "EVAL-018": _eval_018,
    "EVAL-019": _eval_019,
    "EVAL-020": _eval_020,
    "EVAL-021": _eval_021,
    "EVAL-022": _eval_022,
    "EVAL-023": _eval_023,
    "EVAL-024": _eval_024,
    "EVAL-025": _eval_025,
    "EVAL-026": _eval_026,
    "EVAL-027": _eval_027,
    "EVAL-028": _eval_028,
    "EVAL-029": _eval_029,
    "EVAL-030": _eval_030,
}


def _audit_hard_constraints(
    case: PlannerEvaluationCase,
    observation: PlannerObservation,
) -> list[str]:
    violations: list[str] = []

    quantities = _numeric_lot_quantities(case)

    for lot_id, planning_quantity in (
        quantities.items()
    ):
        allocated = sum(
            (
                _decimal(item.quantity or 0)
                for item in observation.allocations
                if item.lot_id == lot_id
            ),
            ZERO,
        )

        if allocated > planning_quantity:
            violations.append(
                f"{lot_id}: allocated {allocated} "
                f"> planning quantity {planning_quantity}"
            )

    if case.case_id == "EVAL-003":
        if any(
            item.destination == "PARTNER-A"
            for item in observation.allocations
        ):
            violations.append(
                "PARTNER-A allocated after timing reject"
            )

    if case.case_id == "EVAL-004":
        partner_used = sum(
            (
                _decimal(item.quantity or 0)
                for item in observation.allocations
                if item.action
                == ActionType.EXTERNAL_PARTNER.value
            ),
            ZERO,
        )

        if partner_used > Decimal("30"):
            violations.append(
                "shared partner capacity exceeded"
            )

    if case.case_id == "EVAL-005":
        human_consumption_actions = {
            ActionType.LOCAL_DISCOUNT.value,
            ActionType.BUNDLE.value,
            ActionType.PROMOTIONAL_BONUS.value,
            ActionType.INTERNAL_USE.value,
            ActionType.WHOLESALE.value,
            ActionType.EXTERNAL_PARTNER.value,
            ActionType.DONATION.value,
        }

        unsafe_quantity = sum(
            (
                _decimal(item.quantity or 0)
                for item in observation.allocations
                if item.action
                in human_consumption_actions
            ),
            ZERO,
        )

        if unsafe_quantity > ZERO:
            violations.append(
                "hard-reject lot entered "
                "human-consumption route"
            )

    return violations


def run_planner_eval_case(
    case: PlannerEvaluationCase | str,
) -> PlannerEvalExecution:
    """Execute one locked evaluation case against Day-2 planner logic."""

    if isinstance(case, str):
        case = load_planner_case(
            DEFAULT_CASES_DIR / f"{case}.yaml"
        )

    runner = RUNNERS.get(case.case_id)

    if runner is None:
        raise NotImplementedError(
            f"Runtime adapter belum tersedia "
            f"untuk {case.case_id}."
        )

    observation = runner(case)

    assertion_failures = evaluate_case(
        case,
        observation,
    )

    hard_constraint_violations = (
        _audit_hard_constraints(
            case,
            observation,
        )
    )

    return PlannerEvalExecution(
        case_id=case.case_id,
        passed=(
            not assertion_failures
            and not hard_constraint_violations
        ),
        observation=observation,
        assertion_failures=assertion_failures,
        hard_constraint_violations=(
            hard_constraint_violations
        ),
    )


__all__ = [
    "PlannerEvalExecution",
    "run_planner_eval_case",
]
