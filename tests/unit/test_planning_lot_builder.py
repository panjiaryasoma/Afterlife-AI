from datetime import date
from decimal import Decimal

import pytest

from afterlife_ai.contracts.enums import (
    DefectSeverity,
    InventoryStatus,
    ProductCategory,
    StorageHistoryStatus,
    StorageRequirementMode,
    StorageType,
    SurplusSource,
    TriageConfidenceStatus,
    UnitCode,
    UrgencyLevel,
    VerificationStatus,
)
from afterlife_ai.contracts.inventory import RawInventoryLot
from afterlife_ai.contracts.triage import InventoryTriageResult
from afterlife_ai.planner.planning_lots import build_surplus_planning_lot


def build_inventory_lot() -> RawInventoryLot:
    return RawInventoryLot(
        lot_id="LOT-003",
        sku="PBEV-003",
        product_name="Minuman Serbuk Rasa Mangga",
        product_category=ProductCategory.PACKAGED_BEVERAGE,
        current_quantity=Decimal("25"),
        unit=UnitCode.SACHET,
        unit_cost=Decimal("1500"),
        normal_selling_price=Decimal("2000"),
        minimum_recovery_price=Decimal("1000"),
        source_location="Toko Utama",
        expiry_date=date(2026, 12, 31),
        units_sold_observation_window=Decimal("14"),
        observation_days=14,
        safety_stock=Decimal("5"),
        storage_type=StorageType.DRY_AMBIENT,
        storage_history_status=StorageHistoryStatus.NOT_APPLICABLE,
        package_weight_g=Decimal("10"),
        package_format="SACHET",
        verification_status=VerificationStatus.VERIFIED,
    )


def build_surplus_triage_result() -> InventoryTriageResult:
    return InventoryTriageResult(
        source_lot_id="LOT-003",
        analysis_date=date(2026, 8, 7),
        remaining_shelf_life_days=146,
        remaining_safe_window_hours=None,
        remaining_commercial_window_days=None,
        average_daily_sales=Decimal("1"),
        effective_sales_window_days=Decimal("10"),
        expected_normal_sales=Decimal("10"),
        protected_normal_stock_quantity=Decimal("15"),
        monitor_quantity=Decimal("0"),
        surplus_candidate_quantity=Decimal("10"),
        planning_quantity=Decimal("10"),
        expired_quantity=Decimal("0"),
        review_quantity=Decimal("0"),
        inventory_status=InventoryStatus.SURPLUS_CANDIDATE,
        surplus_source=SurplusSource.CALCULATED,
        triage_reason_codes=["PARTIAL_EXCESS_ABOVE_PROTECTED_STOCK"],
        triage_confidence_status=TriageConfidenceStatus.HIGH,
        urgency_level=UrgencyLevel.MEDIUM,
        estimated_current_value=Decimal("37500"),
        triage_policy_version="triage-v1",
    )


def test_builder_emits_traceable_planning_lot() -> None:
    lot = build_inventory_lot()
    triage = build_surplus_triage_result()

    planning_lot = build_surplus_planning_lot(
        lot,
        triage,
        storage_requirement_mode=StorageRequirementMode.AMBIENT_ALLOWED,
        defect_severity=DefectSeverity.NONE,
    )

    assert planning_lot is not None
    assert planning_lot.planning_lot_id == "PLAN-LOT-003"
    assert planning_lot.source_lot_id == "LOT-003"
    assert planning_lot.sku == "PBEV-003"
    assert planning_lot.planning_quantity == Decimal("10")
    assert planning_lot.package_weight_g == Decimal("10")
    assert planning_lot.package_format == "SACHET"


def test_builder_uses_only_planning_quantity_for_mixed_routing_lot() -> None:
    lot = build_inventory_lot()

    triage = build_surplus_triage_result().model_copy(
        update={
            "protected_normal_stock_quantity": Decimal("0"),
            "surplus_candidate_quantity": Decimal("8"),
            "planning_quantity": Decimal("8"),
            "review_quantity": Decimal("17"),
            "surplus_source": SurplusSource.USER_DECLARED,
        }
    )

    planning_lot = build_surplus_planning_lot(
        lot,
        triage,
        storage_requirement_mode=StorageRequirementMode.AMBIENT_ALLOWED,
        defect_severity=DefectSeverity.NONE,
    )

    assert planning_lot is not None
    assert planning_lot.planning_quantity == Decimal("8")


def test_builder_returns_none_for_non_planner_eligible_status() -> None:
    lot = build_inventory_lot()

    triage = build_surplus_triage_result().model_copy(
        update={
            "protected_normal_stock_quantity": Decimal("25"),
            "surplus_candidate_quantity": Decimal("0"),
            "planning_quantity": Decimal("0"),
            "inventory_status": InventoryStatus.HEALTHY_STOCK,
            "surplus_source": None,
        }
    )

    planning_lot = build_surplus_planning_lot(
        lot,
        triage,
        storage_requirement_mode=StorageRequirementMode.AMBIENT_ALLOWED,
        defect_severity=DefectSeverity.NONE,
    )

    assert planning_lot is None


def test_builder_rejects_mismatched_source_lot() -> None:
    lot = build_inventory_lot()

    triage = build_surplus_triage_result().model_copy(
        update={"source_lot_id": "LOT-WRONG"}
    )

    with pytest.raises(ValueError, match="source_lot_id"):
        build_surplus_planning_lot(
            lot,
            triage,
            storage_requirement_mode=StorageRequirementMode.AMBIENT_ALLOWED,
            defect_severity=DefectSeverity.NONE,
        )
