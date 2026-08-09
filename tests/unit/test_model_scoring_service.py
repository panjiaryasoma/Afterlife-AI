from decimal import Decimal
from pathlib import Path

import pytest

from afterlife_ai.contracts.enums import (
    ActionType,
    BusinessType,
    CoverageStatus,
    DefectSeverity,
    FeasibilityStatus,
    MatchStatus,
    ModelScoringStatus,
    PackagingCondition,
    ProductCategory,
    ProductCondition,
    QualityInspectionStatus,
    SafetyStatus,
    SeasonalityStatus,
    StorageHistoryStatus,
    StorageRequirementMode,
    StorageType,
    SurplusSource,
    UnitCode,
    UrgencyLevel,
    ValidationStatus,
    VerificationStatus,
)
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.planner.candidates import (
    CandidateActionSpec,
    generate_candidates,
)
from afterlife_ai.scoring.model_provider import ModelScoreProvider
from afterlife_ai.scoring.service import score_candidate


def _build_runtime_case():
    planning_lot = SurplusPlanningLot(
        planning_lot_id="PLAN-LOT-001",
        source_lot_id="LOT-001",
        sku="NUTRI-001",
        product_name="Nutrisari Es Rujak",
        product_category=ProductCategory.PACKAGED_BEVERAGE,
        product_subcategory="POWDER_DRINK",
        planning_quantity=Decimal("20"),
        unit=UnitCode.SACHET,
        unit_cost=Decimal("1250"),
        normal_selling_price=Decimal("2000"),
        minimum_recovery_price=Decimal("1000"),
        source_location="STORE-001",
        remaining_shelf_life_days=30,
        remaining_safe_window_hours=None,
        remaining_commercial_window_days=Decimal("30"),
        urgency_level=UrgencyLevel.HIGH,
        surplus_source=SurplusSource.CALCULATED,
        seasonality_status=SeasonalityStatus.POST_SEASON,
        storage_type=StorageType.DRY_AMBIENT,
        storage_requirement_mode=StorageRequirementMode.AMBIENT_ALLOWED,
        storage_history_status=StorageHistoryStatus.NOT_APPLICABLE,
        product_condition=ProductCondition.GOOD,
        packaging_condition=PackagingCondition.INTACT,
        defect_severity=DefectSeverity.NONE,
        quality_inspection_status=QualityInspectionStatus.PASSED,
        verification_status=VerificationStatus.VERIFIED,
        package_volume_ml=Decimal("20"),
        package_weight_g=Decimal("25"),
        package_format="SACHET",
        estimated_current_value=Decimal("40000"),
    )

    candidate = generate_candidates(
        planning_lot,
        [
            CandidateActionSpec(
                action_type=ActionType.LOCAL_DISCOUNT,
                maximum_quantity=Decimal("20"),
                destination_type="LOCAL_CUSTOMER",
                offered_or_selling_price_per_unit=Decimal("1500"),
                estimated_completion_hours=Decimal("1"),
                active_demand_quantity=Decimal("20"),
                available_capacity=Decimal("20"),
                minimum_order_quantity=Decimal("1"),
                capability_resource_ratio=Decimal("1"),
                demand_coverage_ratio=Decimal("1"),
                demand_freshness_hours=Decimal("0"),
                distance_km=Decimal("0"),
            )
        ],
    )[0]

    candidate = candidate.model_copy(
        update={
            "validation_status": ValidationStatus.PASSED,
            "coverage_status": CoverageStatus.SUPPORTED,
            "safety_status": SafetyStatus.ACCEPTABLE,
            "verification_status": VerificationStatus.VERIFIED,
            "feasibility_status": FeasibilityStatus.FEASIBLE,
            "model_scoring_status": ModelScoringStatus.DEFERRED,
            "rejection_reason_codes": [],
            "category_match_status": MatchStatus.NOT_APPLICABLE,
            "package_size_match_status": MatchStatus.NOT_APPLICABLE,
            "customer_segment_match_status": MatchStatus.NOT_APPLICABLE,
            "storage_compatibility_status": MatchStatus.MATCH,
        }
    )

    return planning_lot, candidate


def test_score_candidate_attaches_production_model_score() -> None:
    planning_lot, candidate = _build_runtime_case()

    provider = ModelScoreProvider.from_artifact(
        artifact_path=Path("models/HGB_E_v1.joblib"),
    )

    scored = score_candidate(
        planning_lot=planning_lot,
        candidate=candidate,
        business_type=BusinessType.SMALL_RETAIL,
        provider=provider,
    )

    assert scored.model_scoring_status is ModelScoringStatus.ALLOWED
    assert scored.estimated_rescue_success_score is not None

    assert (
        Decimal("0")
        <= scored.estimated_rescue_success_score
        <= Decimal("1")
    )

    assert scored.model_version is not None


def test_score_candidate_rejects_blocked_candidate() -> None:
    planning_lot, candidate = _build_runtime_case()

    blocked = candidate.model_copy(
        update={
            "model_scoring_status": ModelScoringStatus.BLOCKED,
            "feasibility_status": FeasibilityStatus.INFEASIBLE,
            "rejection_reason_codes": ["SAFETY_HARD_REJECT"],
        }
    )

    provider = ModelScoreProvider.from_artifact(
        artifact_path=Path("models/HGB_E_v1.joblib"),
    )

    with pytest.raises(
        ValueError,
        match="tidak eligible untuk model scoring",
    ):
        score_candidate(
            planning_lot=planning_lot,
            candidate=blocked,
            business_type=BusinessType.SMALL_RETAIL,
            provider=provider,
        )
        