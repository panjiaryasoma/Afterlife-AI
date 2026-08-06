from pathlib import Path

import yaml

from afterlife_ai.contracts.spreadsheet import (
    CONDITIONAL_COLUMNS,
    EXTENSION_COLUMN_PREFIX,
    REQUIRED_COLUMNS,
    SHEET_NAME,
)

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "contracts"
    / "FEATURE_SCHEMA_FINAL_v2.0.yaml"
)


def test_spreadsheet_contract_matches_active_schema() -> None:
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    contract = schema["spreadsheet_contract"]

    assert SHEET_NAME == contract["sheet_name"]
    assert REQUIRED_COLUMNS == tuple(contract["required_columns"])
    assert CONDITIONAL_COLUMNS == tuple(contract["conditional_columns"])
    assert EXTENSION_COLUMN_PREFIX == "x_"


def test_sheet_name_matches_schema_contract() -> None:
    assert SHEET_NAME == "inventory_lots"


def test_required_columns_match_schema_contract() -> None:
    assert REQUIRED_COLUMNS == (
        "lot_id",
        "sku",
        "product_name",
        "product_category",
        "current_quantity",
        "unit",
        "unit_cost",
        "normal_selling_price",
        "source_location",
        "storage_type",
        "verification_status",
    )


def test_required_and_conditional_columns_do_not_overlap() -> None:
    assert set(REQUIRED_COLUMNS).isdisjoint(CONDITIONAL_COLUMNS)


def test_extension_columns_use_x_prefix() -> None:
    assert EXTENSION_COLUMN_PREFIX == "x_"
