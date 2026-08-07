from decimal import Decimal

import pytest
from pydantic import ValidationError

from afterlife_ai.contracts.enums import (
    DefectSeverity,
    ProductCategory,
    StorageHistoryStatus,
    StorageRequirementMode,
    StorageType,
    SurplusSource,
    UnitCode,
    UrgencyLevel,
    VerificationStatus,
)
from afterlife_ai.contracts.planning import SurplusPlanningLot


def build_valid_planning_lot() -> SurplusPlanningLot:
    return SurplusPlanningLot(
        planning_lot_id="PLAN-LOT-001",
        source_lot_id="LOT-001",
        sku="SKU-001",
        product_name="Minuman Kemasan",
        product_category=ProductCategory.PACKAGED_BEVERAGE,
        product_subcategory=None,
        planning_quantity=Decimal("12"),
        unit=UnitCode.SACHET,
        unit_cost=Decimal("1500"),
        normal_selling_price=Decimal("2000"),
        minimum_recovery_price=Decimal("1000"),
        source_location="Toko Utama",
        remaining_shelf_life_days=30,
        remaining_safe_window_hours=None,
        remaining_commercial_window_days=None,
        urgency_level=UrgencyLevel.MEDIUM,
        surplus_source=SurplusSource.CALCULATED,
        seasonality_status=None,
        storage_type=StorageType.DRY_AMBIENT,
        storage_requirement_mode=StorageRequirementMode.AMBIENT_ALLOWED,
        storage_history_status=StorageHistoryStatus.NOT_APPLICABLE,
        product_condition=None,
        packaging_condition=None,
        defect_severity=DefectSeverity.NONE,
        quality_inspection_status=None,
        verification_status=VerificationStatus.VERIFIED,
        estimated_current_value=Decimal("18000"),
    )


def test_valid_surplus_planning_lot_is_accepted() -> None:
    planning_lot = build_valid_planning_lot()

    assert planning_lot.planning_lot_id == "PLAN-LOT-001"
    assert planning_lot.source_lot_id == "LOT-001"
    assert planning_lot.planning_quantity == Decimal("12")


def test_planning_quantity_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        SurplusPlanningLot(
            **{
                **build_valid_planning_lot().model_dump(),
                "planning_quantity": Decimal("0"),
            }
        )


def test_estimated_current_value_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        SurplusPlanningLot(
            **{
                **build_valid_planning_lot().model_dump(),
                "estimated_current_value": Decimal("-1"),
            }
        )


def test_contract_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        SurplusPlanningLot(
            **build_valid_planning_lot().model_dump(),
            unexpected_field="nope",
        )
