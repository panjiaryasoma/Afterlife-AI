"""Deterministic inventory triage engine."""

from datetime import datetime
from decimal import Decimal

from afterlife_ai.contracts.enums import (
    InventoryStatus,
    SurplusSource,
    TriageConfidenceStatus,
    UrgencyLevel,
)
from afterlife_ai.contracts.inventory import RawInventoryLot
from afterlife_ai.contracts.triage import InventoryTriageResult

ZERO = Decimal("0")


def triage_inventory_lot(
    lot: RawInventoryLot,
    *,
    analysis_at: datetime,
    effective_sales_window_days: Decimal,
    triage_policy_version: str,
) -> InventoryTriageResult:
    """Route one validated lot using deterministic triage rules."""

    if effective_sales_window_days < ZERO:
        raise ValueError(
            "effective_sales_window_days tidak boleh negatif."
        )

    if (
        lot.units_sold_observation_window is None
        or lot.observation_days is None
    ):
        raise ValueError(
            "Data penjualan historis diperlukan untuk "
            "menjalankan triage healthy stock."
        )

    observation_days = Decimal(lot.observation_days)

    average_daily_sales = (
        lot.units_sold_observation_window / observation_days
    )
    expected_normal_sales = (
        average_daily_sales * effective_sales_window_days
    )

    protected_stock_limit = (
        expected_normal_sales + lot.safety_stock
    )
    protected_normal_stock_quantity = min(
        lot.current_quantity,
        protected_stock_limit,
    )

    if lot.current_quantity > protected_stock_limit:
        surplus_quantity = (
            lot.current_quantity
            - protected_normal_stock_quantity
        )

        return InventoryTriageResult(
            source_lot_id=lot.lot_id,
            analysis_date=analysis_at.date(),
            remaining_shelf_life_days=None,
            remaining_safe_window_hours=None,
            remaining_commercial_window_days=None,
            average_daily_sales=average_daily_sales,
            effective_sales_window_days=(
                effective_sales_window_days
            ),
            expected_normal_sales=expected_normal_sales,
            protected_normal_stock_quantity=(
                protected_normal_stock_quantity
            ),
            monitor_quantity=ZERO,
            surplus_candidate_quantity=surplus_quantity,
            planning_quantity=surplus_quantity,
            expired_quantity=ZERO,
            review_quantity=ZERO,
            inventory_status=(
                InventoryStatus.SURPLUS_CANDIDATE
            ),
            surplus_source=SurplusSource.CALCULATED,
            triage_reason_codes=[
                "PARTIAL_EXCESS_ABOVE_PROTECTED_STOCK"
            ],
            triage_confidence_status=(
                TriageConfidenceStatus.HIGH
            ),
            urgency_level=UrgencyLevel.MEDIUM,
            estimated_current_value=(
                lot.current_quantity * lot.unit_cost
            ),
            triage_policy_version=triage_policy_version,
        )

    return InventoryTriageResult(
        source_lot_id=lot.lot_id,
        analysis_date=analysis_at.date(),
        remaining_shelf_life_days=None,
        remaining_safe_window_hours=None,
        remaining_commercial_window_days=None,
        average_daily_sales=average_daily_sales,
        effective_sales_window_days=effective_sales_window_days,
        expected_normal_sales=expected_normal_sales,
        protected_normal_stock_quantity=(
            protected_normal_stock_quantity
        ),
        monitor_quantity=ZERO,
        surplus_candidate_quantity=ZERO,
        planning_quantity=ZERO,
        expired_quantity=ZERO,
        review_quantity=ZERO,
        inventory_status=InventoryStatus.HEALTHY_STOCK,
        surplus_source=None,
        triage_reason_codes=[
            "WITHIN_PROTECTED_NORMAL_STOCK"
        ],
        triage_confidence_status=(
            TriageConfidenceStatus.HIGH
        ),
        urgency_level=UrgencyLevel.LOW,
        estimated_current_value=(
            lot.current_quantity * lot.unit_cost
        ),
        triage_policy_version=triage_policy_version,
    )


__all__ = ["triage_inventory_lot"]
