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


def test_triage_003_near_window_stock_is_monitored() -> None:
    lot = RawInventoryLot(
        lot_id="LOT-MONITOR-001",
        sku="DRINK-003",
        product_name="Minuman Serbuk Kemasan",
        product_category=ProductCategory.PACKAGED_BEVERAGE,
        current_quantity=Decimal("10"),
        unit=UnitCode.SACHET,
        unit_cost=Decimal("1250"),
        normal_selling_price=Decimal("2000"),
        source_location="STORE-01",
        expiry_date=date(2026, 8, 19),
        storage_type=StorageType.DRY_AMBIENT,
        storage_history_status=(
            StorageHistoryStatus.VERIFIED_ACCEPTABLE
        ),
        packaging_condition=PackagingCondition.INTACT,
        verification_status=VerificationStatus.VERIFIED,
        units_sold_observation_window=Decimal("30"),
        observation_days=30,
        safety_stock=Decimal("0"),
        declared_surplus=False,
    )

    result = triage_inventory_lot(
        lot,
        analysis_at=datetime(2026, 8, 7, 0, 0),
        effective_sales_window_days=Decimal("10"),
        expiry_monitor_threshold_days=14,
        triage_policy_version="triage-acceptance-v1.0",
    )

    assert result.remaining_shelf_life_days == 12
    assert result.average_daily_sales == Decimal("1")
    assert result.expected_normal_sales == Decimal("10")

    assert result.protected_normal_stock_quantity == Decimal("0")
    assert result.monitor_quantity == Decimal("10")
    assert result.surplus_candidate_quantity == Decimal("0")
    assert result.planning_quantity == Decimal("0")
    assert result.expired_quantity == Decimal("0")
    assert result.review_quantity == Decimal("0")

    assert result.inventory_status is InventoryStatus.MONITOR
    assert result.surplus_source is None
    assert result.triage_reason_codes == [
        "WITHIN_EXPIRY_MONITOR_WINDOW"
    ]

    routed_quantity = (
        result.protected_normal_stock_quantity
        + result.monitor_quantity
        + result.planning_quantity
        + result.expired_quantity
        + result.review_quantity
    )

    assert routed_quantity == lot.current_quantity
