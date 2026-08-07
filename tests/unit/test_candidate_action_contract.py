from decimal import Decimal

import pytest
from pydantic import ValidationError

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


def build_valid_candidate() -> CandidateAction:
    return CandidateAction(
        candidate_id="CAND-003-DISCOUNT",
        planning_lot_id="PLAN-LOT-003",
        action_type=ActionType.LOCAL_DISCOUNT,
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
        storage_compatibility_status=MatchStatus.MATCH,
        validation_status=ValidationStatus.PASSED,
        coverage_status=CoverageStatus.SUPPORTED,
        safety_status=SafetyStatus.ACCEPTABLE,
        verification_status=VerificationStatus.VERIFIED,
        feasibility_status=FeasibilityStatus.FEASIBLE,
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


def test_valid_candidate_action_is_accepted() -> None:
    candidate = build_valid_candidate()

    assert candidate.candidate_id == "CAND-003-DISCOUNT"
    assert candidate.planning_lot_id == "PLAN-LOT-003"
    assert candidate.action_type is ActionType.LOCAL_DISCOUNT
    assert candidate.maximum_feasible_quantity == Decimal("10")


def test_maximum_feasible_quantity_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        CandidateAction(
            **{
                **build_valid_candidate().model_dump(),
                "maximum_feasible_quantity": Decimal("-1"),
            }
        )


def test_cost_fields_cannot_be_negative() -> None:
    for field_name in (
        "direct_action_cost",
        "logistics_cost",
        "handling_cost",
    ):
        with pytest.raises(ValidationError):
            CandidateAction(
                **{
                    **build_valid_candidate().model_dump(),
                    field_name: Decimal("-1"),
                }
            )


def test_scores_must_remain_between_zero_and_one() -> None:
    for field_name in (
        "fixture_rescue_success_score",
        "estimated_rescue_success_score",
    ):
        with pytest.raises(ValidationError):
            CandidateAction(
                **{
                    **build_valid_candidate().model_dump(),
                    field_name: Decimal("1.01"),
                }
            )


def test_contract_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        CandidateAction(
            **build_valid_candidate().model_dump(),
            unexpected_field="nope",
        )
