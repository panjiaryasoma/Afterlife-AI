import json
from pathlib import Path

import yaml

from afterlife_ai.intake.canonical import (
    build_canonical_inventory_records,
)
from afterlife_ai.intake.xlsx_reader import read_inventory_workbook

REPO_ROOT = Path(__file__).resolve().parents[2]

FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "inventory_valid.xlsx"
)

SCHEMA_PATH = (
    REPO_ROOT
    / "docs"
    / "contracts"
    / "FEATURE_SCHEMA_FINAL_v2.0.yaml"
)


def test_valid_workbook_produces_schema_v2_canonical_records() -> None:
    inventory_lots = read_inventory_workbook(FIXTURE_PATH)

    canonical_records = build_canonical_inventory_records(
        inventory_lots
    )

    schema = yaml.safe_load(
        SCHEMA_PATH.read_text(encoding="utf-8")
    )
    expected_fields = tuple(
        schema["entities"]["INVENTORY_LOT"]["fields"]
    )

    assert len(canonical_records) == 1

    record = canonical_records[0]

    assert tuple(record) == expected_fields
    assert record["lot_id"] == "LOT-001"
    assert record["sku"] == "SKU-001"
    assert record["current_quantity"] == "10"

    serialized = json.dumps(record)

    assert isinstance(serialized, str)
