from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from openpyxl import Workbook

from afterlife_ai.contracts import (
    ProductCategory,
    StorageType,
    UnitCode,
    VerificationStatus,
)
from afterlife_ai.contracts.spreadsheet import REQUIRED_COLUMNS, SHEET_NAME
from afterlife_ai.intake.xlsx_reader import read_inventory_workbook

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "inventory_valid.xlsx"
)


def test_valid_inventory_workbook_is_read() -> None:
    records = read_inventory_workbook(FIXTURE_PATH)

    assert len(records) == 1

    record = records[0]

    assert record.lot_id == "LOT-001"
    assert record.sku == "SKU-001"
    assert record.product_name == "Reference Product"
    assert record.current_quantity == 10


def test_workbook_values_are_normalized_before_validation(
    tmp_path: Path,
) -> None:
    path = tmp_path / "normalization.xlsx"

    optional_columns = (
        "minimum_recovery_price",
        "declared_surplus",
        "declared_surplus_quantity",
        "temperature_log_available",
        "purchase_date",
        "safe_use_by_at",
    )
    headers = (*REQUIRED_COLUMNS, *optional_columns)

    row: dict[str, object] = {
        "lot_id": " LOT-002 ",
        "sku": " SKU-002 ",
        "product_name": " Reference Product ",
        "product_category": next(iter(ProductCategory)).value,
        "current_quantity": "10.5",
        "unit": next(iter(UnitCode)).value,
        "unit_cost": "1000.25",
        "normal_selling_price": "1500",
        "source_location": " STORE-01 ",
        "storage_type": next(iter(StorageType)).value,
        "verification_status": next(iter(VerificationStatus)).value,
        "minimum_recovery_price": "",
        "declared_surplus": "TRUE",
        "declared_surplus_quantity": "2",
        "temperature_log_available": "false",
        "purchase_date": "2026-08-01",
        "safe_use_by_at": "2026-08-10T14:30:00",
    }

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = SHEET_NAME
    worksheet.append(list(headers))
    worksheet.append([row[column] for column in headers])
    workbook.save(path)
    workbook.close()

    records = read_inventory_workbook(path)

    assert len(records) == 1

    record = records[0]

    assert record.lot_id == "LOT-002"
    assert record.sku == "SKU-002"
    assert record.product_name == "Reference Product"
    assert record.source_location == "STORE-01"

    assert record.current_quantity == Decimal("10.5")
    assert record.unit_cost == Decimal("1000.25")
    assert record.normal_selling_price == Decimal("1500")
    assert record.minimum_recovery_price is None
    assert record.declared_surplus_quantity == Decimal("2")

    assert record.declared_surplus is True
    assert record.temperature_log_available is False

    assert record.purchase_date == date(2026, 8, 1)
    assert record.safe_use_by_at == datetime(2026, 8, 10, 14, 30)
