from decimal import Decimal

from afterlife_ai.contracts.enums import (
    ActionType,
    BusinessType,
    DefectSeverity,
    PackagingCondition,
    ProductCategory,
    ProductCondition,
    QualityInspectionStatus,
    SeasonalityStatus,
    StorageHistoryStatus,
    StorageRequirementMode,
    StorageType,
    SurplusSource,
    UnitCode,
    UrgencyLevel,
    VerificationStatus,
)
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.planner.candidates import (
    CandidateActionSpec,
    generate_candidates,
)
from afterlife_ai.scoring.features import build_model_feature_row


def test_build_model_feature_row_maps_runtime_objects() -> None:
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
        storage_requirement_mode=(
            StorageRequirementMode.AMBIENT_ALLOWED
        ),
        storage_history_status=(
            StorageHistoryStatus.NOT_APPLICABLE
        ),
        product_condition=ProductCondition.GOOD,
        packaging_condition=PackagingCondition.INTACT,
        defect_severity=DefectSeverity.NONE,
        quality_inspection_status=(
            QualityInspectionStatus.PASSED
        ),
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
                direct_action_cost=Decimal("0"),
                logistics_cost=Decimal("0"),
                handling_cost=Decimal("0"),
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

    features = build_model_feature_row(
        planning_lot=planning_lot,
        candidate=candidate,
        business_type=BusinessType.SMALL_RETAIL,
    )

    assert features["product_category"] == "PACKAGED_BEVERAGE"
    assert features["action_type"] == "LOCAL_DISCOUNT"
    assert features["business_type"] == "SMALL_RETAIL"

    assert features["planning_quantity"] == Decimal("20")
    assert features["unit_cost"] == Decimal("1250")
    assert (
        features["offered_or_selling_price_per_unit"]
        == Decimal("1500")
    )

    assert len(features) == 30