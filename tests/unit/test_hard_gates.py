from decimal import Decimal

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    CoverageStatus,
    FeasibilityStatus,
    MatchStatus,
    ModelScoringStatus,
    SafetyStatus,
    ValidationStatus,
    VerificationStatus,
)
from afterlife_ai.planner.gates import (
    HardGateContext,
    evaluate_hard_gates,
)


def build_candidate(
    *,
    action_type: ActionType = ActionType.LOCAL_DISCOUNT,
) -> CandidateAction:
    return CandidateAction(
        candidate_id="CAND-003-DISCOUNT",
        planning_lot_id="PLAN-LOT-003",
        action_type=action_type,
        destination_id=None,
        destination_type=None,
        maximum_feasible_quantity=Decimal("10"),
        offered_or_selling_price_per_unit=Decimal("1500"),
        direct_action_cost=Decimal("0"),
        logistics_cost=Decimal("0"),
        handling_cost=Decimal("0"),
        estimated_completion_hours=Decimal("1"),
        active_demand_quantity=None,
        available_capacity=Decimal("10"),
        minimum_order_quantity=None,
        capability_resource_ratio=Decimal("1"),
        demand_coverage_ratio=None,
        demand_freshness_hours=None,
        distance_km=None,
        category_match_status=MatchStatus.NOT_APPLICABLE,
        package_size_match_status=MatchStatus.NOT_APPLICABLE,
        customer_segment_match_status=MatchStatus.NOT_APPLICABLE,
        storage_compatibility_status=MatchStatus.NOT_APPLICABLE,
        validation_status=ValidationStatus.PARTIAL,
        coverage_status=CoverageStatus.INSUFFICIENT_FEATURE_COVERAGE,
        safety_status=SafetyStatus.UNVERIFIED,
        verification_status=VerificationStatus.VERIFIED,
        feasibility_status=FeasibilityStatus.NEEDS_REVIEW,
        model_scoring_status=ModelScoringStatus.DEFERRED,
        rejection_reason_codes=[],
        fixture_rescue_success_score=None,
        estimated_rescue_success_score=None,
        model_version=None,
        expected_cash_recovery=Decimal("0"),
        expected_future_branch_recovery=Decimal("0"),
        expected_avoided_purchase_cost=Decimal("0"),
        expected_physical_rescue_quantity=Decimal("0"),
        expected_waste_quantity=Decimal("0"),
        expected_net_recovery=Decimal("0"),
    )


def build_context() -> HardGateContext:
    return HardGateContext(
        validation_passed=True,
        coverage_supported=True,
        safety_status=SafetyStatus.ACCEPTABLE,
        verification_sufficient=True,
        storage_compatible=True,
        timing_feasible=True,
        action_eligible=True,
        qualifying_transactions=1,
    )


def test_feasible_candidate_passes_hard_gates() -> None:
    result = evaluate_hard_gates(
        build_candidate(),
        build_context(),
    )

    assert result.validation_status is ValidationStatus.PASSED
    assert result.coverage_status is CoverageStatus.SUPPORTED
    assert result.safety_status is SafetyStatus.ACCEPTABLE
    assert result.feasibility_status is FeasibilityStatus.FEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.DEFERRED
    assert result.rejection_reason_codes == []


def test_safety_hard_reject_blocks_candidate() -> None:
    context = build_context().model_copy(
        update={"safety_status": SafetyStatus.HARD_REJECT}
    )

    result = evaluate_hard_gates(
        build_candidate(),
        context,
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.BLOCKED
    assert "SAFETY_HARD_REJECT" in result.rejection_reason_codes


def test_storage_mismatch_blocks_candidate() -> None:
    context = build_context().model_copy(
        update={"storage_compatible": False}
    )

    result = evaluate_hard_gates(
        build_candidate(),
        context,
    )

    assert result.storage_compatibility_status is MatchStatus.MISMATCH
    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.BLOCKED
    assert "STORAGE_INCOMPATIBLE" in result.rejection_reason_codes


def test_candidate_capacity_must_cover_feasible_quantity() -> None:
    candidate = build_candidate().model_copy(
        update={"available_capacity": Decimal("4")}
    )

    result = evaluate_hard_gates(
        candidate,
        build_context(),
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.BLOCKED
    assert "INSUFFICIENT_CAPACITY" in result.rejection_reason_codes


def test_minimum_order_quantity_must_be_feasible() -> None:
    candidate = build_candidate().model_copy(
        update={"minimum_order_quantity": Decimal("11")}
    )

    result = evaluate_hard_gates(
        candidate,
        build_context(),
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.BLOCKED
    assert "MINIMUM_ORDER_NOT_MET" in result.rejection_reason_codes


def test_promotional_bonus_requires_qualifying_transaction() -> None:
    candidate = build_candidate(
        action_type=ActionType.PROMOTIONAL_BONUS,
    )

    context = build_context().model_copy(
        update={"qualifying_transactions": 0}
    )

    result = evaluate_hard_gates(
        candidate,
        context,
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.BLOCKED
    assert "NO_QUALIFYING_TRANSACTION" in result.rejection_reason_codes



def test_shelf_life_infeasible_blocks_candidate() -> None:
    context = build_context().model_copy(
        update={"shelf_life_feasible": False}
    )

    result = evaluate_hard_gates(
        build_candidate(),
        context,
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.BLOCKED
    assert "SHELF_LIFE_INFEASIBLE" in result.rejection_reason_codes


def test_logistics_infeasible_blocks_candidate() -> None:
    context = build_context().model_copy(
        update={"logistics_feasible": False}
    )

    result = evaluate_hard_gates(
        build_candidate(),
        context,
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.BLOCKED
    assert "LOGISTICS_INFEASIBLE" in result.rejection_reason_codes


def test_external_partner_requires_active_demand() -> None:
    candidate = build_candidate(
        action_type=ActionType.EXTERNAL_PARTNER,
    ).model_copy(
        update={
            "active_demand_quantity": Decimal("0"),
            "available_capacity": Decimal("10"),
            "category_match_status": MatchStatus.MATCH,
            "package_size_match_status": MatchStatus.MATCH,
            "customer_segment_match_status": MatchStatus.MATCH,
        }
    )

    result = evaluate_hard_gates(
        candidate,
        build_context(),
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.BLOCKED
    assert "NO_ACTIVE_PARTNER_DEMAND" in result.rejection_reason_codes


def test_external_partner_cannot_exceed_active_demand() -> None:
    candidate = build_candidate(
        action_type=ActionType.EXTERNAL_PARTNER,
    ).model_copy(
        update={
            "active_demand_quantity": Decimal("4"),
            "available_capacity": Decimal("10"),
            "category_match_status": MatchStatus.MATCH,
            "package_size_match_status": MatchStatus.MATCH,
            "customer_segment_match_status": MatchStatus.MATCH,
        }
    )

    result = evaluate_hard_gates(
        candidate,
        build_context(),
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.BLOCKED
    assert (
        "ACTIVE_DEMAND_QUANTITY_EXCEEDED"
        in result.rejection_reason_codes
    )


def test_external_partner_requires_category_match() -> None:
    candidate = build_candidate(
        action_type=ActionType.EXTERNAL_PARTNER,
    ).model_copy(
        update={
            "active_demand_quantity": Decimal("10"),
            "category_match_status": MatchStatus.MISMATCH,
            "package_size_match_status": MatchStatus.MATCH,
            "customer_segment_match_status": MatchStatus.MATCH,
        }
    )

    result = evaluate_hard_gates(
        candidate,
        build_context(),
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert "PARTNER_CATEGORY_MISMATCH" in result.rejection_reason_codes


def test_external_partner_requires_package_match() -> None:
    candidate = build_candidate(
        action_type=ActionType.EXTERNAL_PARTNER,
    ).model_copy(
        update={
            "active_demand_quantity": Decimal("10"),
            "category_match_status": MatchStatus.MATCH,
            "package_size_match_status": MatchStatus.MISMATCH,
            "customer_segment_match_status": MatchStatus.MATCH,
        }
    )

    result = evaluate_hard_gates(
        candidate,
        build_context(),
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert (
        "PARTNER_PACKAGE_SIZE_MISMATCH"
        in result.rejection_reason_codes
    )


def test_external_partner_requires_customer_segment_match() -> None:
    candidate = build_candidate(
        action_type=ActionType.EXTERNAL_PARTNER,
    ).model_copy(
        update={
            "active_demand_quantity": Decimal("10"),
            "category_match_status": MatchStatus.MATCH,
            "package_size_match_status": MatchStatus.MATCH,
            "customer_segment_match_status": MatchStatus.MISMATCH,
        }
    )

    result = evaluate_hard_gates(
        candidate,
        build_context(),
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert (
        "PARTNER_CUSTOMER_SEGMENT_MISMATCH"
        in result.rejection_reason_codes
    )


def test_action_specific_ineligibility_blocks_candidate() -> None:
    context = build_context().model_copy(
        update={"action_eligible": False}
    )

    result = evaluate_hard_gates(
        build_candidate(),
        context,
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.BLOCKED
    assert "ACTION_NOT_ELIGIBLE" in result.rejection_reason_codes
