from datetime import date, datetime
from decimal import Decimal

from afterlife_ai.contracts import (
    InventoryStatus,
    PackagingCondition,
    ProductCategory,
    RawInventoryLot,
    StorageHistoryStatus,
    StorageType,
    SurplusSource,
    UnitCode,
    VerificationStatus,
)
from afterlife_ai.triage.engine import triage_inventory_lot


def test_triage_008_declared_surplus_limits_planning_quantity() -> None:
    lot = RawInventoryLot(
        lot_id="LOT-DECLARED-001",
        sku="DRINK-008",
        product_name="Minuman Serbuk Kemasan",
        product_category=ProductCategory.PACKAGED_BEVERAGE,
        current_quantity=Decimal("20"),
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
        declared_surplus=True,
        declared_surplus_quantity=Decimal("8"),
    )

    result = triage_inventory_lot(
        lot,
        analysis_at=datetime(2026, 8, 7, 0, 0),
        effective_sales_window_days=Decimal("10"),
        expiry_monitor_threshold_days=14,
        declared_surplus_allowed=True,
        triage_policy_version="triage-acceptance-v1.0",
    )

    assert result.remaining_shelf_life_days == 146

    assert result.average_daily_sales is None
    assert result.effective_sales_window_days is None
    assert result.expected_normal_sales is None

    assert result.protected_normal_stock_quantity == Decimal("0")
    assert result.monitor_quantity == Decimal("0")
    assert result.planning_quantity == Decimal("8")
    assert result.expired_quantity == Decimal("0")
    assert result.review_quantity == Decimal("12")

    assert (
        result.inventory_status
        is InventoryStatus.SURPLUS_CANDIDATE
    )
    assert result.surplus_source is SurplusSource.USER_DECLARED
    assert result.triage_reason_codes == [
        "VALID_PARTIAL_USER_DECLARED_SURPLUS"
    ]

    routed_quantity = (
        result.protected_normal_stock_quantity
        + result.monitor_quantity
        + result.planning_quantity
        + result.expired_quantity
        + result.review_quantity
    )

    assert routed_quantity == lot.current_quantity
    assert result.planning_quantity < lot.current_quantity
