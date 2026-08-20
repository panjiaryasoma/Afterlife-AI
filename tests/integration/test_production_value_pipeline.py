from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

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
from afterlife_ai.pipeline.candidates import (
    generate_production_candidates,
)
from afterlife_ai.pipeline.gates import (
    apply_production_hard_gates,
)
from afterlife_ai.pipeline.planning import (
    build_production_planning_lots,
)
from afterlife_ai.pipeline.runtime_config import (
    load_runtime_config,
)
from afterlife_ai.pipeline.scoring import (
    score_production_candidates,
)
from afterlife_ai.pipeline.triage_pipeline import (
    run_triage_pipeline,
)
from afterlife_ai.pipeline.value import (
    apply_production_expected_values,
)

FIXTURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integration_001"
)

WORKBOOK_PATH = FIXTURE_DIR / "RAW_INVENTORY_FIXTURE.xlsx"
RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")


def test_production_expected_value_uses_model_score_and_candidate_economics() -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    triage = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=analysis_at,
    )

    planning_lots = build_production_planning_lots(
        lots=triage.raw_inventory_lots,
        triage_results=triage.triage_results,
        config=config,
    )

    candidates = generate_production_candidates(
        planning_lots=planning_lots,
        config=config,
    )

    gated = apply_production_hard_gates(
        candidates=candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=triage.raw_inventory_lots,
        config=config,
        analysis_at=analysis_at,
    )

    scored = score_production_candidates(
        candidates=gated,
        planning_lots=planning_lots,
        config=config,
    )

    valued = apply_production_expected_values(
        candidates=scored,
    )

    assert len(valued) == 5

    for candidate in valued:
        probability = (
            candidate.estimated_rescue_success_score
        )

        assert probability is not None

        quantity = candidate.maximum_feasible_quantity
        price = (
            candidate.offered_or_selling_price_per_unit
            or Decimal("0")
        )

        successful_total_value = (
            price * quantity
            - candidate.direct_action_cost
            - candidate.logistics_cost
            - candidate.handling_cost
        )

        expected_net = (
            probability
            * successful_total_value
        )

        assert (
            candidate.expected_net_recovery
            == expected_net
        )

        assert (
            candidate.expected_physical_rescue_quantity
            == probability * quantity
        )

        assert (
            candidate.expected_waste_quantity
            == (
                Decimal("1") - probability
            ) * quantity
        )
def test_safe_disposal_is_not_counted_as_physical_rescue() -> None:
    candidate = CandidateAction(
        candidate_id="CAND-001-DISPOSAL",
        planning_lot_id="PLAN-LOT-001",
        action_type=ActionType.SAFE_DISPOSAL,
        destination_id=None,
        destination_type=None,
        maximum_feasible_quantity=Decimal("10"),
        offered_or_selling_price_per_unit=Decimal("0"),
        direct_action_cost=Decimal("0"),
        logistics_cost=Decimal("0"),
        handling_cost=Decimal("0"),
        estimated_completion_hours=Decimal("1"),
        active_demand_quantity=None,
        available_capacity=Decimal("10"),
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
    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    [scored] = score_production_candidates(
        candidates=[candidate],
        planning_lots=[],
        config=config,
    )

    assert (
        scored.model_scoring_status
        is ModelScoringStatus.SKIPPED
    )
    assert scored.estimated_rescue_success_score is None
    assert scored.model_version is None

    [valued] = apply_production_expected_values(
        candidates=[scored],
    )

    assert (
        valued.expected_physical_rescue_quantity
        == Decimal("0")
    )
    assert (
        valued.expected_waste_quantity
        == Decimal("10")
    )
