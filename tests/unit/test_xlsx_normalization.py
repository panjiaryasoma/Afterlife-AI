from datetime import date, datetime
from decimal import Decimal

from afterlife_ai.intake.normalization import normalize_inventory_row


def test_inventory_row_values_are_normalized() -> None:
    raw_row: dict[str, object] = {
        "lot_id": " LOT-002 ",
        "sku": " SKU-002 ",
        "product_name": " Reference Product ",
        "current_quantity": "10.5",
        "unit_cost": "1000.25",
        "normal_selling_price": "1500",
        "minimum_recovery_price": "",
        "declared_surplus": "TRUE",
        "declared_surplus_quantity": "2",
        "temperature_log_available": "false",
        "purchase_date": "2026-08-01",
        "safe_use_by_at": "2026-08-10T14:30:00",
    }

    normalized = normalize_inventory_row(raw_row)

    assert normalized["lot_id"] == "LOT-002"
    assert normalized["sku"] == "SKU-002"
    assert normalized["product_name"] == "Reference Product"

    assert normalized["current_quantity"] == Decimal("10.5")
    assert normalized["unit_cost"] == Decimal("1000.25")
    assert normalized["normal_selling_price"] == Decimal("1500")
    assert normalized["minimum_recovery_price"] is None
    assert normalized["declared_surplus_quantity"] == Decimal("2")

    assert normalized["declared_surplus"] is True
    assert normalized["temperature_log_available"] is False

    assert normalized["purchase_date"] == date(2026, 8, 1)
    assert normalized["safe_use_by_at"] == datetime(2026, 8, 10, 14, 30)



def test_blank_safety_stock_uses_contract_default() -> None:
    from afterlife_ai.contracts.inventory import RawInventoryLot

    raw_row: dict[str, object] = {
        "lot_id": "LOT-BLANK-SAFETY",
        "sku": "SKU-BLANK-SAFETY",
        "product_name": "Blank Safety Stock Product",
        "product_category": "PACKAGED_BEVERAGE",
        "current_quantity": "20",
        "unit": "SACHET",
        "unit_cost": "1000",
        "normal_selling_price": "2000",
        "source_location": "STORE-01",
        "safety_stock": None,
        "storage_type": "DRY_AMBIENT",
        "verification_status": "VERIFIED",
    }

    normalized = normalize_inventory_row(raw_row)

    # Blank spreadsheet input must not override the
    # RawInventoryLot contract default of Decimal("0").
    assert "safety_stock" not in normalized

    lot = RawInventoryLot.model_validate(normalized)

    assert lot.safety_stock == Decimal("0")
