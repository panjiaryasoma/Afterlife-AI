from decimal import Decimal

import pytest

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    CoverageStatus,
    FeasibilityStatus,
    MatchStatus,
    ModelScoringStatus,
    OptimizationObjective,
    SafetyStatus,
    SolverStatus,
    ValidationStatus,
    VerificationStatus,
)
from afterlife_ai.planner.optimizer import optimize_with_cp_sat


def build_candidate(
    *,
    candidate_id: str,
    planning_lot_id: str,
    action_type: ActionType,
    maximum_quantity: str,
    expected_value_per_unit: str,
    feasible: bool = True,
    minimum_order_quantity: str | None = None,
) -> CandidateAction:
    maximum = Decimal(maximum_quantity)
    expected_per_unit = Decimal(expected_value_per_unit)

    feasibility_status = (
        FeasibilityStatus.FEASIBLE
        if feasible
        else FeasibilityStatus.INFEASIBLE
    )

    scoring_status = (
        ModelScoringStatus.DEFERRED
        if feasible
        else ModelScoringStatus.BLOCKED
    )

    return CandidateAction(
        candidate_id=candidate_id,
        planning_lot_id=planning_lot_id,
        action_type=action_type,
        destination_id=None,
        destination_type=None,
        maximum_feasible_quantity=maximum,
        offered_or_selling_price_per_unit=None,
        direct_action_cost=Decimal("0"),
        logistics_cost=Decimal("0"),
        handling_cost=Decimal("0"),
        estimated_completion_hours=None,
        active_demand_quantity=None,
        available_capacity=maximum,
        minimum_order_quantity=(
            Decimal(minimum_order_quantity)
            if minimum_order_quantity is not None
            else None
        ),
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
        feasibility_status=feasibility_status,
        model_scoring_status=scoring_status,
        rejection_reason_codes=(
            [] if feasible else ["NO_QUALIFYING_TRANSACTION"]
        ),
        fixture_rescue_success_score=Decimal("0.5") if feasible else None,
        estimated_rescue_success_score=None,
        model_version=None,
        expected_cash_recovery=Decimal("0"),
        expected_future_branch_recovery=Decimal("0"),
        expected_avoided_purchase_cost=Decimal("0"),
        expected_physical_rescue_quantity=Decimal("0"),
        expected_waste_quantity=Decimal("0"),
        expected_net_recovery=expected_per_unit * maximum,
    )


def build_candidates() -> list[CandidateAction]:
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


def optimize_fixture():
    return optimize_with_cp_sat(
        candidates=build_candidates(),
        planning_quantities={
            "PLAN-LOT-003": Decimal("10"),
            "PLAN-LOT-006": Decimal("8"),
        },
        shared_action_capacities={
            ActionType.INTERNAL_REPURPOSE: Decimal("6"),
        },
    )


def test_optimizer_matches_integration_fixture_allocation() -> None:
    result = optimize_fixture()

    allocations = {
        allocation.candidate_id: allocation.allocated_quantity
        for allocation in result.allocations
    }

    assert allocations == {
        "CAND-003-REPURPOSE": Decimal("6"),
        "CAND-003-BUNDLE": Decimal("4"),
        "CAND-006-DISCOUNT": Decimal("8"),
    }


def test_optimizer_respects_shared_action_capacity() -> None:
    result = optimize_fixture()

    repurpose_total = sum(
        allocation.allocated_quantity
        for allocation in result.allocations
        if allocation.action_type is ActionType.INTERNAL_REPURPOSE
    )

    assert repurpose_total == Decimal("6")


def test_optimizer_preserves_quantity_conservation() -> None:
    result = optimize_fixture()

    allocated_by_lot = {
        "PLAN-LOT-003": Decimal("0"),
        "PLAN-LOT-006": Decimal("0"),
    }

    for allocation in result.allocations:
        allocated_by_lot[allocation.planning_lot_id] += (
            allocation.allocated_quantity
        )

    for planning_lot_id, planning_quantity in {
        "PLAN-LOT-003": Decimal("10"),
        "PLAN-LOT-006": Decimal("8"),
    }.items():
        assert (
            allocated_by_lot[planning_lot_id]
            + result.unallocated_quantities[planning_lot_id]
            == planning_quantity
        )


def test_blocked_candidate_never_enters_allocation() -> None:
    result = optimize_fixture()

    allocated_ids = {
        allocation.candidate_id
        for allocation in result.allocations
    }

    assert "CAND-006-BONUS" not in allocated_ids


def test_optimizer_reports_solver_status_and_objective() -> None:
    result = optimize_fixture()

    assert result.solver_status in {
        SolverStatus.OPTIMAL,
        SolverStatus.FEASIBLE,
    }
    assert result.objective_value == Decimal("26624")


def test_optimizer_is_deterministic() -> None:
    first = optimize_fixture()
    second = optimize_fixture()

    assert first == second



def test_optimizer_respects_shared_destination_capacity() -> None:
    high_value = build_candidate(
        candidate_id="CAND-A-PARTNER",
        planning_lot_id="PLAN-LOT-A",
        action_type=ActionType.EXTERNAL_PARTNER,
        maximum_quantity="5",
        expected_value_per_unit="2000",
    ).model_copy(
        update={"destination_id": "PARTNER-001"}
    )

    lower_value = build_candidate(
        candidate_id="CAND-B-PARTNER",
        planning_lot_id="PLAN-LOT-B",
        action_type=ActionType.EXTERNAL_PARTNER,
        maximum_quantity="5",
        expected_value_per_unit="1000",
    ).model_copy(
        update={"destination_id": "PARTNER-001"}
    )

    result = optimize_with_cp_sat(
        candidates=[high_value, lower_value],
        planning_quantities={
            "PLAN-LOT-A": Decimal("5"),
            "PLAN-LOT-B": Decimal("5"),
        },
        shared_destination_capacities={
            "PARTNER-001": Decimal("5"),
        },
    )

    allocated = {
        allocation.candidate_id: allocation.allocated_quantity
        for allocation in result.allocations
    }

    assert allocated == {
        "CAND-A-PARTNER": Decimal("5"),
    }

    assert (
        sum(
            allocation.allocated_quantity
            for allocation in result.allocations
            if allocation.candidate_id
            in {"CAND-A-PARTNER", "CAND-B-PARTNER"}
        )
        == Decimal("5")
    )


def test_optimizer_rejects_duplicate_candidate_ids() -> None:
    candidate = build_candidate(
        candidate_id="CAND-DUPLICATE",
        planning_lot_id="PLAN-LOT-001",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity="5",
        expected_value_per_unit="1000",
    )

    with pytest.raises(
        ValueError,
        match="Duplicate candidate_id",
    ):
        optimize_with_cp_sat(
            candidates=[candidate, candidate],
            planning_quantities={
                "PLAN-LOT-001": Decimal("5"),
            },
        )


def test_optimizer_rejects_negative_shared_action_capacity() -> None:
    candidate = build_candidate(
        candidate_id="CAND-NEGATIVE-CAP",
        planning_lot_id="PLAN-LOT-001",
        action_type=ActionType.INTERNAL_REPURPOSE,
        maximum_quantity="5",
        expected_value_per_unit="1000",
    )

    with pytest.raises(
        ValueError,
        match="shared action capacity",
    ):
        optimize_with_cp_sat(
            candidates=[candidate],
            planning_quantities={
                "PLAN-LOT-001": Decimal("5"),
            },
            shared_action_capacities={
                ActionType.INTERNAL_REPURPOSE: Decimal("-1"),
            },
        )


def test_optimizer_rejects_negative_destination_capacity() -> None:
    candidate = build_candidate(
        candidate_id="CAND-PARTNER",
        planning_lot_id="PLAN-LOT-001",
        action_type=ActionType.EXTERNAL_PARTNER,
        maximum_quantity="5",
        expected_value_per_unit="1000",
    ).model_copy(
        update={"destination_id": "PARTNER-001"}
    )

    with pytest.raises(
        ValueError,
        match="shared destination capacity",
    ):
        optimize_with_cp_sat(
            candidates=[candidate],
            planning_quantities={
                "PLAN-LOT-001": Decimal("5"),
            },
            shared_destination_capacities={
                "PARTNER-001": Decimal("-1"),
            },
        )


def test_optimizer_supports_fractional_quantities() -> None:
    candidate = build_candidate(
        candidate_id="CAND-FRACTIONAL",
        planning_lot_id="PLAN-LOT-001",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity="1.5",
        expected_value_per_unit="1000",
    )

    result = optimize_with_cp_sat(
        candidates=[candidate],
        planning_quantities={
            "PLAN-LOT-001": Decimal("1.5"),
        },
    )

    assert result.allocations[0].allocated_quantity == Decimal("1.5")
    assert result.objective_value == Decimal("1500")
    assert (
        result.unallocated_quantities["PLAN-LOT-001"]
        == Decimal("0.0")
    )


def test_optimizer_does_not_force_negative_value_allocation() -> None:
    candidate = build_candidate(
        candidate_id="CAND-NEGATIVE-VALUE",
        planning_lot_id="PLAN-LOT-001",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity="5",
        expected_value_per_unit="-100",
    )

    result = optimize_with_cp_sat(
        candidates=[candidate],
        planning_quantities={
            "PLAN-LOT-001": Decimal("5"),
        },
    )

    assert result.allocations == []
    assert result.objective_value == Decimal("0")
    assert (
        result.unallocated_quantities["PLAN-LOT-001"]
        == Decimal("5")
    )



def test_optimizer_respects_global_logistics_budget() -> None:
    candidate_a = build_candidate(
        candidate_id="CAND-BUDGET-A",
        planning_lot_id="PLAN-A",
        action_type=ActionType.EXTERNAL_PARTNER,
        maximum_quantity="20",
        expected_value_per_unit="3000",
    ).model_copy(
        update={
            "destination_id": "PARTNER-A",
            "logistics_cost": Decimal("10000"),
        }
    )

    candidate_b = build_candidate(
        candidate_id="CAND-BUDGET-B",
        planning_lot_id="PLAN-B",
        action_type=ActionType.EXTERNAL_PARTNER,
        maximum_quantity="15",
        expected_value_per_unit="4000",
    ).model_copy(
        update={
            "destination_id": "PARTNER-B",
            "logistics_cost": Decimal("20000"),
        }
    )

    candidate_c = build_candidate(
        candidate_id="CAND-BUDGET-C",
        planning_lot_id="PLAN-C",
        action_type=ActionType.EXTERNAL_PARTNER,
        maximum_quantity="25",
        expected_value_per_unit="100",
    ).model_copy(
        update={
            "destination_id": "PARTNER-C",
            "logistics_cost": Decimal("15000"),
        }
    )

    candidates = [
        candidate_a,
        candidate_b,
        candidate_c,
    ]

    result = optimize_with_cp_sat(
        candidates=candidates,
        planning_quantities={
            "PLAN-A": Decimal("20"),
            "PLAN-B": Decimal("15"),
            "PLAN-C": Decimal("25"),
        },
        max_logistics_budget=Decimal("30000"),
    )

    allocated_ids = {
        allocation.candidate_id
        for allocation in result.allocations
    }

    assert allocated_ids == {
        "CAND-BUDGET-A",
        "CAND-BUDGET-B",
    }

    assert result.total_logistics_cost == Decimal("30000")



def test_optimizer_enforces_aggregated_action_minimum_quantity() -> None:
    candidates = [
        build_candidate(
            candidate_id="CAND-A-WHOLESALE",
            planning_lot_id="PLAN-A",
            action_type=ActionType.WHOLESALE,
            maximum_quantity="30",
            expected_value_per_unit="300",
        ),
        build_candidate(
            candidate_id="CAND-A-DISCOUNT",
            planning_lot_id="PLAN-A",
            action_type=ActionType.LOCAL_DISCOUNT,
            maximum_quantity="30",
            expected_value_per_unit="100",
        ),
        build_candidate(
            candidate_id="CAND-B-WHOLESALE",
            planning_lot_id="PLAN-B",
            action_type=ActionType.WHOLESALE,
            maximum_quantity="25",
            expected_value_per_unit="300",
        ),
        build_candidate(
            candidate_id="CAND-B-DISCOUNT",
            planning_lot_id="PLAN-B",
            action_type=ActionType.LOCAL_DISCOUNT,
            maximum_quantity="25",
            expected_value_per_unit="100",
        ),
    ]

    result = optimize_with_cp_sat(
        candidates=candidates,
        planning_quantities={
            "PLAN-A": Decimal("30"),
            "PLAN-B": Decimal("25"),
        },
        shared_action_capacities={
            ActionType.WHOLESALE: Decimal("50"),
        },
        shared_action_minimum_quantities={
            ActionType.WHOLESALE: Decimal("50"),
        },
    )

    wholesale_quantity = sum(
        allocation.allocated_quantity
        for allocation in result.allocations
        if allocation.action_type is ActionType.WHOLESALE
    )

    discount_quantity = sum(
        allocation.allocated_quantity
        for allocation in result.allocations
        if allocation.action_type is ActionType.LOCAL_DISCOUNT
    )

    assert wholesale_quantity == Decimal("50")
    assert discount_quantity == Decimal("5")


def test_optimizer_does_not_use_action_when_aggregate_moq_cannot_be_met() -> None:
    candidates = [
        build_candidate(
            candidate_id="CAND-A-WHOLESALE",
            planning_lot_id="PLAN-A",
            action_type=ActionType.WHOLESALE,
            maximum_quantity="20",
            expected_value_per_unit="300",
        ),
        build_candidate(
            candidate_id="CAND-A-DISCOUNT",
            planning_lot_id="PLAN-A",
            action_type=ActionType.LOCAL_DISCOUNT,
            maximum_quantity="20",
            expected_value_per_unit="100",
        ),
        build_candidate(
            candidate_id="CAND-B-WHOLESALE",
            planning_lot_id="PLAN-B",
            action_type=ActionType.WHOLESALE,
            maximum_quantity="25",
            expected_value_per_unit="300",
        ),
        build_candidate(
            candidate_id="CAND-B-DISCOUNT",
            planning_lot_id="PLAN-B",
            action_type=ActionType.LOCAL_DISCOUNT,
            maximum_quantity="25",
            expected_value_per_unit="100",
        ),
    ]

    result = optimize_with_cp_sat(
        candidates=candidates,
        planning_quantities={
            "PLAN-A": Decimal("20"),
            "PLAN-B": Decimal("25"),
        },
        shared_action_minimum_quantities={
            ActionType.WHOLESALE: Decimal("50"),
        },
    )

    wholesale_quantity = sum(
        allocation.allocated_quantity
        for allocation in result.allocations
        if allocation.action_type is ActionType.WHOLESALE
    )

    discount_quantity = sum(
        allocation.allocated_quantity
        for allocation in result.allocations
        if allocation.action_type is ActionType.LOCAL_DISCOUNT
    )

    assert wholesale_quantity == Decimal("0")
    assert discount_quantity == Decimal("45")

def test_optimizer_does_not_allocate_below_candidate_minimum_order_quantity() -> None:
    candidate = build_candidate(
        candidate_id="CAND-PARTNER-MOQ",
        planning_lot_id="PLAN-MOQ",
        action_type=ActionType.EXTERNAL_PARTNER,
        maximum_quantity="10",
        expected_value_per_unit="1000",
        minimum_order_quantity="5",
    )

    result = optimize_with_cp_sat(
        candidates=[candidate],
        planning_quantities={
            "PLAN-MOQ": Decimal("3"),
        },
    )

    assert result.allocations == []
    assert (
        result.unallocated_quantities["PLAN-MOQ"]
        == Decimal("3")
    )

def test_optimizer_respects_generic_shared_resource_capacity() -> None:
    chocolate = build_candidate(
        candidate_id="CAND-CHOC-COLD",
        planning_lot_id="PLAN-CHOC",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity="20",
        expected_value_per_unit="1000",
    )

    drink_chilled = build_candidate(
        candidate_id="CAND-DRINK-CHILLED",
        planning_lot_id="PLAN-DRINK",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity="24",
        expected_value_per_unit="200",
    )

    drink_ambient = build_candidate(
        candidate_id="CAND-DRINK-AMBIENT",
        planning_lot_id="PLAN-DRINK",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity="24",
        expected_value_per_unit="100",
    )

    result = optimize_with_cp_sat(
        candidates=[
            chocolate,
            drink_chilled,
            drink_ambient,
        ],
        planning_quantities={
            "PLAN-CHOC": Decimal("20"),
            "PLAN-DRINK": Decimal("24"),
        },
        shared_resource_capacities={
            "COLD_STORAGE": Decimal("32"),
        },
        candidate_resource_requirements={
            "CAND-CHOC-COLD": {
                "COLD_STORAGE": Decimal("1"),
            },
            "CAND-DRINK-CHILLED": {
                "COLD_STORAGE": Decimal("1"),
            },
        },
    )

    allocations = {
        allocation.candidate_id:
        allocation.allocated_quantity
        for allocation in result.allocations
    }

    assert allocations == {
        "CAND-CHOC-COLD": Decimal("20"),
        "CAND-DRINK-CHILLED": Decimal("12"),
        "CAND-DRINK-AMBIENT": Decimal("12"),
    }

    assert result.shared_resource_usage == {
        "COLD_STORAGE": Decimal("32"),
    }


def build_objective_candidates() -> list[CandidateAction]:
    discount = build_candidate(
        candidate_id="CAND-OBJECTIVE-DISCOUNT",
        planning_lot_id="PLAN-OBJECTIVE",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity="25",
        expected_value_per_unit="4800",
    ).model_copy(
        update={
            "expected_physical_rescue_quantity":
                Decimal("20"),
        }
    )

    partner = build_candidate(
        candidate_id="CAND-OBJECTIVE-PARTNER",
        planning_lot_id="PLAN-OBJECTIVE",
        action_type=ActionType.EXTERNAL_PARTNER,
        maximum_quantity="15",
        expected_value_per_unit="4000",
    ).model_copy(
        update={
            "destination_id": "PARTNER-COMMERCIAL",
            "expected_physical_rescue_quantity":
                Decimal("13.5"),
        }
    )

    donation = build_candidate(
        candidate_id="CAND-OBJECTIVE-DONATION",
        planning_lot_id="PLAN-OBJECTIVE",
        action_type=ActionType.DONATION,
        maximum_quantity="40",
        expected_value_per_unit="0",
    ).model_copy(
        update={
            "expected_physical_rescue_quantity":
                Decimal("39.2"),
        }
    )

    return [
        discount,
        partner,
        donation,
    ]


def test_optimizer_maximize_recovery_objective_matches_eval_029() -> None:
    result = optimize_with_cp_sat(
        candidates=build_objective_candidates(),
        planning_quantities={
            "PLAN-OBJECTIVE": Decimal("40"),
        },
        optimization_objective=(
            OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
        ),
    )

    allocations = {
        allocation.action_type:
        allocation.allocated_quantity
        for allocation in result.allocations
    }

    assert allocations == {
        ActionType.LOCAL_DISCOUNT: Decimal("25"),
        ActionType.EXTERNAL_PARTNER: Decimal("15"),
    }

    assert result.objective_value == Decimal("180000")


def test_optimizer_minimize_waste_objective_matches_eval_029() -> None:
    result = optimize_with_cp_sat(
        candidates=build_objective_candidates(),
        planning_quantities={
            "PLAN-OBJECTIVE": Decimal("40"),
        },
        optimization_objective=(
            OptimizationObjective.MINIMIZE_WASTE
        ),
    )

    allocations = {
        allocation.action_type:
        allocation.allocated_quantity
        for allocation in result.allocations
    }

    assert allocations == {
        ActionType.DONATION: Decimal("40"),
    }

    assert (
        result.expected_physical_rescue_quantity
        == Decimal("39.2")
    )


def test_optimizer_balanced_objective_matches_eval_029() -> None:
    result = optimize_with_cp_sat(
        candidates=build_objective_candidates(),
        planning_quantities={
            "PLAN-OBJECTIVE": Decimal("40"),
        },
        optimization_objective=(
            OptimizationObjective.BALANCED
        ),
        minimum_expected_rescue_ratio=Decimal("0.90"),
    )

    allocations = {
        allocation.action_type:
        allocation.allocated_quantity
        for allocation in result.allocations
    }

    assert allocations == {
        ActionType.LOCAL_DISCOUNT: Decimal("11"),
        ActionType.EXTERNAL_PARTNER: Decimal("15"),
        ActionType.DONATION: Decimal("14"),
    }

    assert result.objective_value == Decimal("112800")
    assert (
        result.expected_physical_rescue_quantity
        == Decimal("36.02")
    )

def test_optimizer_balanced_is_infeasible_when_rescue_floor_cannot_be_met() -> None:
    result = optimize_with_cp_sat(
        candidates=build_objective_candidates(),
        planning_quantities={
            "PLAN-OBJECTIVE": Decimal("40"),
        },
        optimization_objective=(
            OptimizationObjective.BALANCED
        ),
        minimum_expected_rescue_ratio=Decimal("1.00"),
    )

    assert (
        result.solver_status
        is SolverStatus.INFEASIBLE
    )

    assert result.allocations == []

    assert result.unallocated_quantities == {
        "PLAN-OBJECTIVE": Decimal("40"),
    }

def test_optimizer_bounds_high_precision_objective_values() -> None:
    candidate = build_candidate(
        candidate_id="CAND-HIGH-PRECISION",
        planning_lot_id="PLAN-LOT-HIGH-PRECISION",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity="5",
        expected_value_per_unit=(
            "98990.17480769230769230769231"
        ),
    )

    result = optimize_with_cp_sat(
        candidates=[candidate],
        planning_quantities={
            "PLAN-LOT-HIGH-PRECISION": Decimal("5"),
        },
    )

    assert result.solver_status in {
        SolverStatus.OPTIMAL,
        SolverStatus.FEASIBLE,
    }

    assert (
        result.allocations[0].allocated_quantity
        == Decimal("5")
    )

def test_optimizer_minimize_waste_uses_recovery_as_tie_breaker() -> None:
    lower_recovery = build_candidate(
        candidate_id="CAND-A-LOW-RECOVERY",
        planning_lot_id="PLAN-TIE-BREAK",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity="10",
        expected_value_per_unit="100",
    ).model_copy(
        update={
            "expected_physical_rescue_quantity": Decimal("10"),
        }
    )

    higher_recovery = build_candidate(
        candidate_id="CAND-Z-HIGH-RECOVERY",
        planning_lot_id="PLAN-TIE-BREAK",
        action_type=ActionType.BUNDLE,
        maximum_quantity="10",
        expected_value_per_unit="200",
    ).model_copy(
        update={
            "expected_physical_rescue_quantity": Decimal("10"),
        }
    )

    result = optimize_with_cp_sat(
        candidates=[
            lower_recovery,
            higher_recovery,
        ],
        planning_quantities={
            "PLAN-TIE-BREAK": Decimal("10"),
        },
        shared_action_minimum_quantities={
            ActionType.LOCAL_DISCOUNT: Decimal("10"),
            ActionType.BUNDLE: Decimal("10"),
        },
        optimization_objective=(
            OptimizationObjective.MINIMIZE_WASTE
        ),
    )

    allocations = {
        allocation.candidate_id:
        allocation.allocated_quantity
        for allocation in result.allocations
    }

    assert allocations == {
        "CAND-Z-HIGH-RECOVERY": Decimal("10"),
    }

def test_optimizer_minimize_waste_tie_breaker_is_not_candidate_id_dependent() -> None:
    higher_recovery = build_candidate(
        candidate_id="CAND-A-HIGH-RECOVERY",
        planning_lot_id="PLAN-TIE-BREAK",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity="10",
        expected_value_per_unit="200",
    ).model_copy(
        update={
            "expected_physical_rescue_quantity": Decimal("10"),
        }
    )

    lower_recovery = build_candidate(
        candidate_id="CAND-Z-LOW-RECOVERY",
        planning_lot_id="PLAN-TIE-BREAK",
        action_type=ActionType.BUNDLE,
        maximum_quantity="10",
        expected_value_per_unit="100",
    ).model_copy(
        update={
            "expected_physical_rescue_quantity": Decimal("10"),
        }
    )

    result = optimize_with_cp_sat(
        candidates=[
            higher_recovery,
            lower_recovery,
        ],
        planning_quantities={
            "PLAN-TIE-BREAK": Decimal("10"),
        },
        shared_action_minimum_quantities={
            ActionType.LOCAL_DISCOUNT: Decimal("10"),
            ActionType.BUNDLE: Decimal("10"),
        },
        optimization_objective=(
            OptimizationObjective.MINIMIZE_WASTE
        ),
    )

    allocations = {
        allocation.candidate_id:
        allocation.allocated_quantity
        for allocation in result.allocations
    }

    assert allocations == {
        "CAND-A-HIGH-RECOVERY": Decimal("10"),
    }

def test_cp_sat_solver_uses_bounded_runtime(
    monkeypatch,
) -> None:
    from afterlife_ai.planner import optimizer

    real_cp_solver = optimizer.cp_model.CpSolver
    captured_solvers = []

    def tracking_solver():
        solver = real_cp_solver()
        captured_solvers.append(solver)
        return solver

    monkeypatch.setattr(
        optimizer.cp_model,
        "CpSolver",
        tracking_solver,
    )

    optimizer.optimize_with_cp_sat(
        candidates=[],
        planning_quantities={},
    )

    assert captured_solvers
    assert (
        captured_solvers[0]
        .parameters
        .max_time_in_seconds
        == optimizer.OPTIMIZER_MAX_TIME_SECONDS
    )
    assert (
        optimizer.OPTIMIZER_MAX_TIME_SECONDS
        == 5.0
    )

def test_optimizer_allocates_when_candidate_minimum_order_quantity_is_met() -> None:
    candidate = build_candidate(
        candidate_id="CAND-PARTNER-MOQ-OK",
        planning_lot_id="PLAN-MOQ-OK",
        action_type=ActionType.EXTERNAL_PARTNER,
        maximum_quantity="10",
        expected_value_per_unit="1000",
        minimum_order_quantity="5",
    )

    result = optimize_with_cp_sat(
        candidates=[candidate],
        planning_quantities={
            "PLAN-MOQ-OK": Decimal("7"),
        },
    )

    assert len(result.allocations) == 1
    assert (
        result.allocations[0].allocated_quantity
        == Decimal("7")
    )
def test_optimizer_handles_repeating_decimal_planning_quantity() -> None:
    planning_quantity = Decimal(
        "78.66666666666666666666666667"
    )

    candidate = build_candidate(
        candidate_id="CAND-REPEATING-PRECISION",
        planning_lot_id="PLAN-REPEATING-PRECISION",
        action_type=ActionType.LOCAL_DISCOUNT,
        maximum_quantity=str(planning_quantity),
        expected_value_per_unit="1000",
    )

    result = optimize_with_cp_sat(
        candidates=[candidate],
        planning_quantities={
            "PLAN-REPEATING-PRECISION": planning_quantity,
        },
    )

    allocated_quantity = sum(
        (
            allocation.allocated_quantity
            for allocation in result.allocations
        ),
        Decimal("0"),
    )

    unallocated_quantity = result.unallocated_quantities[
        "PLAN-REPEATING-PRECISION"
    ]

    assert result.solver_status in {
        SolverStatus.OPTIMAL,
        SolverStatus.FEASIBLE,
    }

    assert allocated_quantity <= planning_quantity
    assert unallocated_quantity >= Decimal("0")

    assert (
        allocated_quantity
        + unallocated_quantity
        == planning_quantity
    )
