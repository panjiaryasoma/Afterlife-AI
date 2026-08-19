from decimal import Decimal

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    CoverageStatus,
    FeasibilityStatus,
    MatchStatus,
    ModelScoringStatus,
    SafetyStatus,
    SolverStatus,
    ValidationStatus,
    VerificationStatus,
)
from afterlife_ai.planner.fallback import (
    allocate_with_deterministic_fallback,
)


def build_candidate(
    *,
    candidate_id: str,
    planning_lot_id: str,
    action_type: ActionType,
    maximum_quantity: str,
    expected_value_per_unit: str,
    destination_id: str | None = None,
    feasible: bool = True,
) -> CandidateAction:
    maximum = Decimal(maximum_quantity)
    value_per_unit = Decimal(expected_value_per_unit)

    return CandidateAction(
        candidate_id=candidate_id,
        planning_lot_id=planning_lot_id,
        action_type=action_type,
        destination_id=destination_id,
        destination_type=None,
        maximum_feasible_quantity=maximum,
        offered_or_selling_price_per_unit=None,
        direct_action_cost=Decimal("0"),
        logistics_cost=Decimal("0"),
        handling_cost=Decimal("0"),
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
        feasibility_status=(
            FeasibilityStatus.FEASIBLE
            if feasible
            else FeasibilityStatus.INFEASIBLE
        ),
        model_scoring_status=(
            ModelScoringStatus.DEFERRED
            if feasible
            else ModelScoringStatus.BLOCKED
        ),
        rejection_reason_codes=(
            []
            if feasible
            else ["HARD_GATE_REJECT"]
        ),
        fixture_rescue_success_score=(
            Decimal("0.5")
            if feasible
            else None
        ),
        estimated_rescue_success_score=None,
        model_version=None,
        expected_cash_recovery=Decimal("0"),
        expected_future_branch_recovery=Decimal("0"),
        expected_avoided_purchase_cost=Decimal("0"),
        expected_physical_rescue_quantity=Decimal("0"),
        expected_waste_quantity=Decimal("0"),
        expected_net_recovery=(
            value_per_unit * maximum
        ),
    )


def build_fixture_candidates() -> list[CandidateAction]:
    return [
        build_candidate(
            candidate_id="CAND-003-REPURPOSE",
            planning_lot_id="PLAN-LOT-003",
            action_type=ActionType.INTERNAL_REPURPOSE,
            maximum_quantity="6",
            expected_value_per_unit="2064",
        ),
        build_candidate(
            candidate_id="CAND-003-BUNDLE",
            planning_lot_id="PLAN-LOT-003",
            action_type=ActionType.BUNDLE,
            maximum_quantity="4",
            expected_value_per_unit="1280",
        ),
        build_candidate(
            candidate_id="CAND-003-DISCOUNT",
            planning_lot_id="PLAN-LOT-003",
            action_type=ActionType.LOCAL_DISCOUNT,
            maximum_quantity="10",
            expected_value_per_unit="1110",
        ),
        build_candidate(
            candidate_id="CAND-006-REPURPOSE",
            planning_lot_id="PLAN-LOT-006",
            action_type=ActionType.INTERNAL_REPURPOSE,
            maximum_quantity="6",
            expected_value_per_unit="1896",
        ),
        build_candidate(
            candidate_id="CAND-006-DISCOUNT",
            planning_lot_id="PLAN-LOT-006",
            action_type=ActionType.LOCAL_DISCOUNT,
            maximum_quantity="8",
            expected_value_per_unit="1140",
        ),
        build_candidate(
            candidate_id="CAND-006-BONUS",
            planning_lot_id="PLAN-LOT-006",
            action_type=ActionType.PROMOTIONAL_BONUS,
            maximum_quantity="8",
            expected_value_per_unit="9999",
            feasible=False,
        ),
    ]


def run_fixture():
    return allocate_with_deterministic_fallback(
        candidates=build_fixture_candidates(),
        planning_quantities={
            "PLAN-LOT-003": Decimal("10"),
            "PLAN-LOT-006": Decimal("8"),
        },
        shared_action_capacities={
            ActionType.INTERNAL_REPURPOSE: Decimal("6"),
        },
    )


def test_fallback_matches_integration_fixture() -> None:
    result = run_fixture()

    allocations = {
        allocation.candidate_id: allocation.allocated_quantity
        for allocation in result.allocations
    }

    assert allocations == {
        "CAND-003-REPURPOSE": Decimal("6"),
        "CAND-003-BUNDLE": Decimal("4"),
        "CAND-006-DISCOUNT": Decimal("8"),
    }

    assert result.objective_value == Decimal("26624")


def test_fallback_reports_fallback_used_status() -> None:
    result = run_fixture()

    assert result.solver_status is SolverStatus.FALLBACK_USED

    assert all(
        allocation.solver_status is SolverStatus.FALLBACK_USED
        for allocation in result.allocations
    )


def test_fallback_preserves_quantity_conservation() -> None:
    result = run_fixture()

    assert result.unallocated_quantities == {
        "PLAN-LOT-003": Decimal("0"),
        "PLAN-LOT-006": Decimal("0"),
    }

    assert (
        sum(
            allocation.allocated_quantity
            for allocation in result.allocations
        )
        == Decimal("18")
    )


def test_fallback_never_allocates_blocked_candidate() -> None:
    result = run_fixture()

    assert "CAND-006-BONUS" not in {
        allocation.candidate_id
        for allocation in result.allocations
    }


def test_fallback_respects_shared_destination_capacity() -> None:
    candidates = [
        build_candidate(
            candidate_id="CAND-A",
            planning_lot_id="PLAN-A",
            action_type=ActionType.EXTERNAL_PARTNER,
            maximum_quantity="5",
            expected_value_per_unit="2000",
            destination_id="PARTNER-001",
        ),
        build_candidate(
            candidate_id="CAND-B",
            planning_lot_id="PLAN-B",
            action_type=ActionType.EXTERNAL_PARTNER,
            maximum_quantity="5",
            expected_value_per_unit="1000",
            destination_id="PARTNER-001",
        ),
    ]

    result = allocate_with_deterministic_fallback(
        candidates=candidates,
        planning_quantities={
            "PLAN-A": Decimal("5"),
            "PLAN-B": Decimal("5"),
        },
        shared_destination_capacities={
            "PARTNER-001": Decimal("5"),
        },
    )

    assert {
        allocation.candidate_id: allocation.allocated_quantity
        for allocation in result.allocations
    } == {
        "CAND-A": Decimal("5"),
    }


def test_fallback_uses_candidate_id_as_deterministic_tie_break() -> None:
    candidates = [
        build_candidate(
            candidate_id="CAND-B",
            planning_lot_id="PLAN-001",
            action_type=ActionType.LOCAL_DISCOUNT,
            maximum_quantity="5",
            expected_value_per_unit="1000",
        ),
        build_candidate(
            candidate_id="CAND-A",
            planning_lot_id="PLAN-001",
            action_type=ActionType.BUNDLE,
            maximum_quantity="5",
            expected_value_per_unit="1000",
        ),
    ]

    result = allocate_with_deterministic_fallback(
        candidates=candidates,
        planning_quantities={
            "PLAN-001": Decimal("5"),
        },
    )

    assert len(result.allocations) == 1
    assert result.allocations[0].candidate_id == "CAND-A"
    assert result.allocations[0].allocated_quantity == Decimal("5")


def test_fallback_is_deterministic_across_input_order() -> None:
    candidates = build_fixture_candidates()

    first = allocate_with_deterministic_fallback(
        candidates=candidates,
        planning_quantities={
            "PLAN-LOT-003": Decimal("10"),
            "PLAN-LOT-006": Decimal("8"),
        },
        shared_action_capacities={
            ActionType.INTERNAL_REPURPOSE: Decimal("6"),
        },
    )

    second = allocate_with_deterministic_fallback(
        candidates=list(reversed(candidates)),
        planning_quantities={
            "PLAN-LOT-003": Decimal("10"),
            "PLAN-LOT-006": Decimal("8"),
        },
        shared_action_capacities={
            ActionType.INTERNAL_REPURPOSE: Decimal("6"),
        },
    )

    assert first == second


def test_fallback_leaves_negative_value_candidate_unallocated() -> None:
    candidate = build_candidate(
        candidate_id="CAND-NEGATIVE",
        planning_lot_id="PLAN-001",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity="5",
        expected_value_per_unit="-100",
    )

    result = allocate_with_deterministic_fallback(
        candidates=[candidate],
        planning_quantities={
            "PLAN-001": Decimal("5"),
        },
    )

    assert result.allocations == []
    assert result.objective_value == Decimal("0")
    assert result.unallocated_quantities == {
        "PLAN-001": Decimal("5"),
    }



def test_fallback_allows_zero_value_donation_as_terminal_rescue_route() -> None:
    candidate = build_candidate(
        candidate_id="CAND-DONATION-ZERO-CASH",
        planning_lot_id="PLAN-DONATION",
        action_type=ActionType.DONATION,
        maximum_quantity="30",
        expected_value_per_unit="0",
    )

    result = allocate_with_deterministic_fallback(
        candidates=[candidate],
        planning_quantities={
            "PLAN-DONATION": Decimal("30"),
        },
    )

    assert result.allocations[0].candidate_id == (
        "CAND-DONATION-ZERO-CASH"
    )
    assert (
        result.allocations[0].allocated_quantity
        == Decimal("30")
    )
    assert result.objective_value == Decimal("0")
    assert result.unallocated_quantities == {
        "PLAN-DONATION": Decimal("0"),
    }

def test_fallback_respects_shared_resource_capacity() -> None:
    candidates = [
        build_candidate(
            candidate_id="CAND-A",
            planning_lot_id="PLAN-A",
            action_type=ActionType.INTERNAL_REPURPOSE,
            maximum_quantity="5",
            expected_value_per_unit="2000",
        ),
        build_candidate(
            candidate_id="CAND-B",
            planning_lot_id="PLAN-B",
            action_type=ActionType.INTERNAL_REPURPOSE,
            maximum_quantity="5",
            expected_value_per_unit="1000",
        ),
    ]

    result = allocate_with_deterministic_fallback(
        candidates=candidates,
        planning_quantities={
            "PLAN-A": Decimal("5"),
            "PLAN-B": Decimal("5"),
        },
        shared_resource_capacities={
            "cold_storage_units": Decimal("6"),
        },
        candidate_resource_requirements={
            "CAND-A": {
                "cold_storage_units": Decimal("1"),
            },
            "CAND-B": {
                "cold_storage_units": Decimal("1"),
            },
        },
    )

    assert {
        allocation.candidate_id:
        allocation.allocated_quantity
        for allocation in result.allocations
    } == {
        "CAND-A": Decimal("5"),
        "CAND-B": Decimal("1"),
    }

    assert result.shared_resource_usage == {
        "cold_storage_units": Decimal("6"),
    }

    assert (
        "SHARED_RESOURCE_CAPACITY:cold_storage_units"
        in result.allocations[-1].binding_constraint_codes
    )