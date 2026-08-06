from datetime import date, datetime
from decimal import Decimal

from afterlife_ai.contracts import (
    IntegrityStatus,
    InventoryStatus,
    PackagingCondition,
    ProductCategory,
    RawInventoryLot,
    StorageHistoryStatus,
    StorageType,
    UnitCode,
    VerificationStatus,
)
from afterlife_ai.triage.engine import triage_inventory_lot


def test_triage_006_missing_storage_evidence_requires_review() -> None:
    lot = RawInventoryLot(
        lot_id="LOT-REVIEW-001",
        sku="FROZEN-001",
        product_name="Frozen Prepared Food",
        product_category=ProductCategory.FROZEN_PREPARED_FOOD,
        current_quantity=Decimal("20"),
        unit=UnitCode.PACK,
        unit_cost=Decimal("8000"),
        normal_selling_price=Decimal("12000"),
        source_location="STORE-01",
        expiry_date=date(2026, 9, 15),
        expiry_label_readable=True,
        storage_type=StorageType.FROZEN,
        storage_history_status=StorageHistoryStatus.UNKNOWN,
        temperature_log_available=False,
        packaging_condition=PackagingCondition.INTACT,
        seal_integrity=IntegrityStatus.INTACT,
        verification_status=VerificationStatus.VERIFIED,
        units_sold_observation_window=Decimal("12"),
        observation_days=30,
        safety_stock=Decimal("4"),
        declared_surplus=False,
        declared_surplus_quantity=Decimal("0"),
    )

    result = triage_inventory_lot(
        lot,
        analysis_at=datetime(2026, 8, 7, 0, 0),
        effective_sales_window_days=Decimal("10"),
        expiry_monitor_threshold_days=14,
        cold_chain_evidence_required=True,
        triage_policy_version="triage-acceptance-v1.0",
    )

    assert result.remaining_shelf_life_days == 39

    assert result.protected_normal_stock_quantity == Decimal("0")
    assert result.monitor_quantity == Decimal("0")
    assert result.surplus_candidate_quantity == Decimal("0")
    assert result.planning_quantity == Decimal("0")
    assert result.expired_quantity == Decimal("0")
    assert result.review_quantity == Decimal("20")

    assert result.inventory_status is InventoryStatus.NEEDS_REVIEW
    assert result.surplus_source is None
    assert "UNKNOWN_STORAGE_HISTORY" in result.triage_reason_codes

    # Critical safety uncertainty harus menang sebelum kalkulasi surplus.
    assert result.average_daily_sales is None
    assert result.effective_sales_window_days is None
    assert result.expected_normal_sales is None

    routed_quantity = (
        result.protected_normal_stock_quantity
        + result.monitor_quantity
        + result.planning_quantity
        + result.expired_quantity
        + result.review_quantity
    )

    assert routed_quantity == lot.current_quantity
