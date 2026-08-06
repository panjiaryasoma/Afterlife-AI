from datetime import date
from decimal import Decimal
from pathlib import Path

import yaml

from afterlife_ai.contracts import (
    InventoryStatus,
    TriageConfidenceStatus,
    UrgencyLevel,
)
from afterlife_ai.contracts.triage import InventoryTriageResult

REPO_ROOT = Path(__file__).resolve().parents[2]

SCHEMA_PATH = (
    REPO_ROOT
    / "docs"
    / "contracts"
    / "FEATURE_SCHEMA_FINAL_v2.0.yaml"
)


def test_triage_result_fields_match_schema_v2() -> None:
    schema = yaml.safe_load(
        SCHEMA_PATH.read_text(encoding="utf-8")
    )
    expected_fields = tuple(
        schema["entities"]["INVENTORY_TRIAGE_RESULT"]["fields"]
    )

    assert tuple(InventoryTriageResult.model_fields) == expected_fields


def test_valid_healthy_stock_triage_result_is_accepted() -> None:
    result = InventoryTriageResult(
        source_lot_id="LOT-HEALTHY-001",
        analysis_date=date(2026, 8, 7),
        protected_normal_stock_quantity=Decimal("15"),
        monitor_quantity=Decimal("0"),
        surplus_candidate_quantity=Decimal("0"),
        planning_quantity=Decimal("0"),
        expired_quantity=Decimal("0"),
        review_quantity=Decimal("0"),
        inventory_status=InventoryStatus.HEALTHY_STOCK,
        triage_reason_codes=["NORMAL_STOCK_PROTECTED"],
        triage_confidence_status=TriageConfidenceStatus.HIGH,
        urgency_level=UrgencyLevel.LOW,
        estimated_current_value=Decimal("22500"),
        triage_policy_version="triage-v1.0",
    )

    assert result.source_lot_id == "LOT-HEALTHY-001"
    assert result.inventory_status is InventoryStatus.HEALTHY_STOCK
    assert result.protected_normal_stock_quantity == Decimal("15")
    assert result.planning_quantity == Decimal("0")
    assert result.surplus_source is None
