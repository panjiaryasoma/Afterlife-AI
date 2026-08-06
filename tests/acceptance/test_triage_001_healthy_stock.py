from datetime import datetime
from decimal import Decimal

from afterlife_ai.contracts import (
    InventoryStatus,
    PackagingCondition,
    ProductCategory,
    RawInventoryLot,
    StorageHistoryStatus,
    StorageType,
    TriageConfidenceStatus,
    UnitCode,
    UrgencyLevel,
    VerificationStatus,
)
from afterlife_ai.triage.engine import triage_inventory_lot


def test_triage_001_healthy_stock_is_protected() -> None:
    lot = RawInventoryLot(
        lot_id="LOT-HEALTHY-001",
        sku="DRINK-001",
        product_name="Minuman Serbuk Kemasan",
        product_category=ProductCategory.PACKAGED_BEVERAGE,
        current_quantity=Decimal("15"),
        unit=UnitCode.SACHET,
        unit_cost=Decimal("1250"),
        normal_selling_price=Decimal("2000"),
        source_location="STORE-01",
        storage_type=StorageType.DRY_AMBIENT,
        storage_history_status=(
            StorageHistoryStatus.VERIFIED_ACCEPTABLE
        ),
        packaging_condition=PackagingCondition.INTACT,
        verification_status=VerificationStatus.VERIFIED,
        units_sold_observation_window=Decimal("30"),
        observation_days=30,
        safety_stock=Decimal("5"),
        declared_surplus=False,
    )

    result = triage_inventory_lot(
        lot,
        analysis_at=datetime(2026, 8, 7, 0, 0),
        effective_sales_window_days=Decimal("10"),
        triage_policy_version="triage-acceptance-v1.0",
    )

    assert result.source_lot_id == "LOT-HEALTHY-001"
    assert result.analysis_date.isoformat() == "2026-08-07"

    assert result.average_daily_sales == Decimal("1")
    assert result.effective_sales_window_days == Decimal("10")
    assert result.expected_normal_sales == Decimal("10")

    assert result.protected_normal_stock_quantity == Decimal("15")
    assert result.monitor_quantity == Decimal("0")
    assert result.surplus_candidate_quantity == Decimal("0")
    assert result.planning_quantity == Decimal("0")
    assert result.expired_quantity == Decimal("0")
    assert result.review_quantity == Decimal("0")

    assert result.inventory_status is InventoryStatus.HEALTHY_STOCK
    assert result.surplus_source is None
    assert result.triage_reason_codes == [
        "WITHIN_PROTECTED_NORMAL_STOCK"
    ]
    assert (
        result.triage_confidence_status
        is TriageConfidenceStatus.HIGH
    )
    assert result.urgency_level is UrgencyLevel.LOW
    assert result.estimated_current_value == Decimal("18750")

    routed_quantity = (
        result.protected_normal_stock_quantity
        + result.monitor_quantity
        + result.planning_quantity
        + result.expired_quantity
        + result.review_quantity
    )

    assert routed_quantity == lot.current_quantity
