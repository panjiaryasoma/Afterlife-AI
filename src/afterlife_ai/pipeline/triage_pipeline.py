"""Production XLSX-to-triage application pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from afterlife_ai.contracts.enums import (
    InventoryStatus,
    TriageConfidenceStatus,
    UrgencyLevel,
)
from afterlife_ai.contracts.inventory import RawInventoryLot
from afterlife_ai.contracts.triage import InventoryTriageResult
from afterlife_ai.intake.canonical import (
    CanonicalInventoryRecord,
    build_canonical_inventory_records,
)
from afterlife_ai.intake.xlsx_reader import read_inventory_workbook
from afterlife_ai.pipeline.runtime_config import (
    RuntimeConfig,
    load_runtime_config,
)
from afterlife_ai.triage.engine import triage_inventory_lot

ZERO = Decimal("0")


@dataclass(frozen=True)
class TriagePipelineResult:
    """Observable outputs from the production triage stage."""

    raw_inventory_lots: list[RawInventoryLot]
    canonical_inventory_records: list[CanonicalInventoryRecord]
    triage_results: list[InventoryTriageResult]


def _unsupported_category_result(
    *,
    lot: RawInventoryLot,
    analysis_at: datetime,
    config: RuntimeConfig,
) -> InventoryTriageResult:
    """Route a category without runtime policy to human review."""

    remaining_shelf_life_days = (
        (lot.expiry_date - analysis_at.date()).days
        if lot.expiry_date is not None
        else None
    )

    return InventoryTriageResult(
        source_lot_id=lot.lot_id,
        analysis_date=analysis_at.date(),
        remaining_shelf_life_days=remaining_shelf_life_days,
        remaining_safe_window_hours=None,
        remaining_commercial_window_days=None,
        average_daily_sales=None,
        effective_sales_window_days=None,
        expected_normal_sales=None,
        protected_normal_stock_quantity=ZERO,
        monitor_quantity=ZERO,
        surplus_candidate_quantity=ZERO,
        planning_quantity=ZERO,
        expired_quantity=ZERO,
        review_quantity=lot.current_quantity,
        inventory_status=InventoryStatus.NEEDS_REVIEW,
        surplus_source=None,
        triage_reason_codes=[
            "UNSUPPORTED_RUNTIME_CATEGORY_POLICY"
        ],
        triage_confidence_status=TriageConfidenceStatus.LOW,
        urgency_level=UrgencyLevel.MEDIUM,
        estimated_current_value=(
            lot.current_quantity * lot.unit_cost
        ),
        triage_policy_version=config.triage.policy_version,
    )


def run_triage_pipeline(
    *,
    workbook_path: Path,
    runtime_config_path: Path,
    analysis_at: datetime,
) -> TriagePipelineResult:
    """Read one workbook and execute deterministic inventory triage."""

    config = load_runtime_config(runtime_config_path)

    raw_inventory_lots = read_inventory_workbook(
        workbook_path
    )

    canonical_inventory_records = (
        build_canonical_inventory_records(
            raw_inventory_lots
        )
    )

    triage_results: list[InventoryTriageResult] = []

    for lot in raw_inventory_lots:
        category_policy = (
            config.triage.category_policies.get(
                lot.product_category
            )
        )

        if category_policy is None:
            triage_results.append(
                _unsupported_category_result(
                    lot=lot,
                    analysis_at=analysis_at,
                    config=config,
                )
            )
            continue

        triage_results.append(
            triage_inventory_lot(
                lot,
                analysis_at=analysis_at,
                effective_sales_window_days=(
                    category_policy.effective_sales_window_days
                ),
                triage_policy_version=(
                    config.triage.policy_version
                ),
                expiry_monitor_threshold_days=(
                    category_policy.expiry_monitor_threshold_days
                ),
                cold_chain_evidence_required=(
                    category_policy.cold_chain_evidence_required
                ),
                declared_surplus_allowed=(
                    config.triage.declared_surplus_allowed
                ),
            )
        )

    return TriagePipelineResult(
        raw_inventory_lots=raw_inventory_lots,
        canonical_inventory_records=canonical_inventory_records,
        triage_results=triage_results,
    )


__all__ = [
    "TriagePipelineResult",
    "run_triage_pipeline",
]
