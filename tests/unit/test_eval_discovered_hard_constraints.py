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


def build_partner_candidate() -> CandidateAction:
    return CandidateAction(
        candidate_id="CAND-STALE-PARTNER",
        planning_lot_id="PLAN-001",
        action_type=ActionType.EXTERNAL_PARTNER,
        destination_id="P-HIGH",
        destination_type=None,
        maximum_feasible_quantity=Decimal("10"),
        offered_or_selling_price_per_unit=None,
        direct_action_cost=Decimal("0"),
        logistics_cost=Decimal("0"),
        handling_cost=Decimal("0"),
        estimated_completion_hours=None,
        active_demand_quantity=Decimal("10"),
        available_capacity=Decimal("10"),
        minimum_order_quantity=None,
        capability_resource_ratio=None,
        demand_coverage_ratio=None,
        demand_freshness_hours=Decimal("72"),
        distance_km=None,
        category_match_status=MatchStatus.MATCH,
        package_size_match_status=MatchStatus.MATCH,
        customer_segment_match_status=MatchStatus.MATCH,
        storage_compatibility_status=MatchStatus.MATCH,
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


def test_stale_partner_demand_is_blocked_before_scoring() -> None:
    result = evaluate_hard_gates(
        build_partner_candidate(),
        HardGateContext(
            validation_passed=True,
            coverage_supported=True,
            safety_status=SafetyStatus.ACCEPTABLE,
            verification_sufficient=True,
            storage_compatible=True,
            timing_feasible=True,
            action_eligible=True,
            partner_demand_fresh=False,
        ),
    )

    assert result.feasibility_status is FeasibilityStatus.INFEASIBLE
    assert result.model_scoring_status is ModelScoringStatus.BLOCKED
    assert "STALE_PARTNER_DEMAND" in result.rejection_reason_codes
