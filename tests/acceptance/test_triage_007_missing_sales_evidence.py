from datetime import date, datetime
from decimal import Decimal

from afterlife_ai.contracts import (
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


def test_triage_007_missing_sales_evidence_requires_review() -> None:
    lot = RawInventoryLot(
        lot_id="LOT-SALES-REVIEW-001",
        sku="DRINK-007",
        product_name="Minuman Serbuk Kemasan",
        product_category=ProductCategory.PACKAGED_BEVERAGE,
        current_quantity=Decimal("24"),
        unit=UnitCode.SACHET,
        unit_cost=Decimal("1250"),
        normal_selling_price=Decimal("2000"),
        source_location="STORE-01",
        expiry_date=date(2026, 12, 31),
        expiry_label_readable=True,
        storage_type=StorageType.DRY_AMBIENT,
        storage_history_status=(
            StorageHistoryStatus.VERIFIED_ACCEPTABLE
        ),
        packaging_condition=PackagingCondition.INTACT,
        verification_status=VerificationStatus.VERIFIED,
        units_sold_observation_window=None,
        observation_days=None,
        safety_stock=Decimal("5"),
        declared_surplus=False,
        declared_surplus_quantity=Decimal("0"),
    )

    result = triage_inventory_lot(
        lot,
        analysis_at=datetime(2026, 8, 7, 0, 0),
        effective_sales_window_days=Decimal("10"),
        expiry_monitor_threshold_days=14,
        triage_policy_version="triage-acceptance-v1.0",
    )

    assert result.remaining_shelf_life_days == 146

    assert result.average_daily_sales is None
    assert result.effective_sales_window_days is None
    assert result.expected_normal_sales is None

    assert result.protected_normal_stock_quantity == Decimal("0")
    assert result.monitor_quantity == Decimal("0")
    assert result.surplus_candidate_quantity == Decimal("0")
    assert result.planning_quantity == Decimal("0")
    assert result.expired_quantity == Decimal("0")
    assert result.review_quantity == Decimal("24")

    assert result.inventory_status is InventoryStatus.NEEDS_REVIEW
    assert result.surplus_source is None
    assert result.triage_reason_codes == [
        "SALES_EVIDENCE_MISSING"
    ]

    routed_quantity = (
        result.protected_normal_stock_quantity
        + result.monitor_quantity
        + result.planning_quantity
        + result.expired_quantity
        + result.review_quantity
    )

    assert routed_quantity == lot.current_quantity
