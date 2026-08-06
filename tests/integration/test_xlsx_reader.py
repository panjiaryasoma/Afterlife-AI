from pathlib import Path

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
