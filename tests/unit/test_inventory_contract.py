from decimal import Decimal

import pytest
from pydantic import ValidationError

from afterlife_ai.contracts import (
    ProductCategory,
    StorageType,
    UnitCode,
    VerificationStatus,
)
from afterlife_ai.contracts.inventory import RawInventoryLot


def valid_inventory_payload() -> dict[str, object]:
    return {
        "lot_id": "LOT-001",
        "sku": "SKU-001",
        "product_name": "Reference Product",
        "product_category": next(iter(ProductCategory)),
        "current_quantity": Decimal("10"),
        "unit": next(iter(UnitCode)),
        "unit_cost": Decimal("1000"),
        "normal_selling_price": Decimal("1500"),
        "source_location": "STORE-01",
        "storage_type": next(iter(StorageType)),
        "verification_status": next(iter(VerificationStatus)),
    }


def test_valid_inventory_lot_is_accepted() -> None:
    lot = RawInventoryLot.model_validate(valid_inventory_payload())

    assert lot.lot_id == "LOT-001"
    assert lot.current_quantity == Decimal("10")


def test_negative_quantity_is_rejected() -> None:
    payload = valid_inventory_payload()
    payload["current_quantity"] = Decimal("-1")

    with pytest.raises(ValidationError):
        RawInventoryLot.model_validate(payload)


def test_unknown_field_is_rejected() -> None:
    payload = valid_inventory_payload()
    payload["invented_field"] = "not allowed"

    with pytest.raises(ValidationError):
        RawInventoryLot.model_validate(payload)


def test_declared_surplus_requires_quantity() -> None:
    payload = valid_inventory_payload()
    payload["declared_surplus"] = True

    with pytest.raises(ValidationError):
        RawInventoryLot.model_validate(payload)


def test_declared_surplus_cannot_exceed_current_quantity() -> None:
    payload = valid_inventory_payload()
    payload["declared_surplus"] = True
    payload["declared_surplus_quantity"] = Decimal("11")

    with pytest.raises(ValidationError):
        RawInventoryLot.model_validate(payload)


def test_sales_observation_requires_observation_days() -> None:
    payload = valid_inventory_payload()
    payload["units_sold_observation_window"] = Decimal("4")

    with pytest.raises(ValidationError):
        RawInventoryLot.model_validate(payload)



def test_expiry_date_before_production_date_is_rejected() -> None:
    from datetime import date

    import pytest
    from pydantic import ValidationError

    from afterlife_ai.contracts import (
        ProductCategory,
        RawInventoryLot,
        StorageType,
        UnitCode,
        VerificationStatus,
    )

    payload = {
        "lot_id": "LOT-DATE-001",
        "sku": "SKU-DATE-001",
        "product_name": "Date Validation Product",
        "product_category": next(iter(ProductCategory)).value,
        "current_quantity": 10,
        "unit": next(iter(UnitCode)).value,
        "unit_cost": 1000,
        "normal_selling_price": 1500,
        "source_location": "STORE-01",
        "storage_type": next(iter(StorageType)).value,
        "verification_status": next(iter(VerificationStatus)).value,
        "production_date": date(2026, 8, 10),
        "expiry_date": date(2026, 8, 9),
    }

    with pytest.raises(
        ValidationError,
        match="expiry_date tidak boleh lebih awal",
    ):
        RawInventoryLot.model_validate(payload)
