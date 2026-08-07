from decimal import Decimal

import pytest

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
from afterlife_ai.planner.scoring import FixtureScoreProvider


def build_feasible_candidate() -> CandidateAction:
    return CandidateAction(
        candidate_id="CAND-003-REPURPOSE",
        planning_lot_id="PLAN-LOT-003",
        action_type=ActionType.INTERNAL_REPURPOSE,
        destination_id=None,
        destination_type=None,
        maximum_feasible_quantity=Decimal("6"),
        offered_or_selling_price_per_unit=Decimal("2400"),
        direct_action_cost=Decimal("0"),
        logistics_cost=Decimal("0"),
        handling_cost=Decimal("0"),
        estimated_completion_hours=Decimal("2"),
        active_demand_quantity=None,
        available_capacity=Decimal("6"),
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


def build_provider() -> FixtureScoreProvider:
    return FixtureScoreProvider(
        scores={
            "CAND-003-REPURPOSE": Decimal("0.86"),
            "CAND-003-BUNDLE": Decimal("0.80"),
            "CAND-003-DISCOUNT": Decimal("0.74"),
        },
        fixture_version="INTEGRATION-001-v1",
    )


def test_provider_applies_expected_fixture_score() -> None:
    result = build_provider().score(
        build_feasible_candidate()
    )

    assert (
        result.candidate.fixture_rescue_success_score
        == Decimal("0.86")
    )
    assert result.candidate.candidate_id == "CAND-003-REPURPOSE"


def test_fixture_score_does_not_impersonate_model_output() -> None:
    result = build_provider().score(
        build_feasible_candidate()
    )

    assert result.candidate.estimated_rescue_success_score is None
    assert result.candidate.model_version is None
    assert (
        result.candidate.model_scoring_status
        is ModelScoringStatus.DEFERRED
    )


def test_score_result_contains_explicit_provenance() -> None:
    result = build_provider().score(
        build_feasible_candidate()
    )

    assert result.provenance.provider_name == "FixtureScoreProvider"
    assert result.provenance.score_type == "FIXTURE_EXPECTED_SCORE"
    assert result.provenance.source_type == "EVALUATION_FIXTURE"
    assert (
        result.provenance.fixture_version
        == "INTEGRATION-001-v1"
    )


def test_provider_rejects_hard_gate_blocked_candidate() -> None:
    candidate = build_feasible_candidate().model_copy(
        update={
            "feasibility_status": FeasibilityStatus.INFEASIBLE,
            "model_scoring_status": ModelScoringStatus.BLOCKED,
            "rejection_reason_codes": ["SAFETY_HARD_REJECT"],
        }
    )

    with pytest.raises(
        ValueError,
        match="tidak eligible",
    ):
        build_provider().score(candidate)


def test_provider_rejects_candidate_without_fixture_score() -> None:
    candidate = build_feasible_candidate().model_copy(
        update={"candidate_id": "CAND-UNKNOWN"}
    )

    with pytest.raises(
        KeyError,
        match="CAND-UNKNOWN",
    ):
        build_provider().score(candidate)


def test_fixture_scoring_is_deterministic() -> None:
    provider = build_provider()
    candidate = build_feasible_candidate()

    first = provider.score(candidate)
    second = provider.score(candidate)

    assert first == second


def test_provider_rejects_score_outside_probability_range() -> None:
    with pytest.raises(ValueError):
        FixtureScoreProvider(
            scores={
                "CAND-BAD": Decimal("1.01"),
            },
            fixture_version="bad-fixture",
        )
