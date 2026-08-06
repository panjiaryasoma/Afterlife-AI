"""Deterministic inventory triage engine."""

from datetime import datetime
from decimal import Decimal

from afterlife_ai.contracts.enums import (
    InventoryStatus,
    StorageHistoryStatus,
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
    expiry_monitor_threshold_days: int = 14,
    cold_chain_evidence_required: bool = False,
) -> InventoryTriageResult:
    """Route one validated lot using deterministic triage rules."""

    if effective_sales_window_days < ZERO:
        raise ValueError(
            "effective_sales_window_days tidak boleh negatif."
        )

    if expiry_monitor_threshold_days < 0:
        raise ValueError(
            "expiry_monitor_threshold_days tidak boleh negatif."
        )

    remaining_shelf_life_days = (
        (lot.expiry_date - analysis_at.date()).days
        if lot.expiry_date is not None
        else None
    )

    if (
        remaining_shelf_life_days is not None
        and remaining_shelf_life_days < 0
    ):
        return InventoryTriageResult(
            source_lot_id=lot.lot_id,
            analysis_date=analysis_at.date(),
            remaining_shelf_life_days=(
                remaining_shelf_life_days
            ),
            remaining_safe_window_hours=None,
            remaining_commercial_window_days=None,
            average_daily_sales=None,
            effective_sales_window_days=None,
            expected_normal_sales=None,
            protected_normal_stock_quantity=ZERO,
            monitor_quantity=ZERO,
            surplus_candidate_quantity=ZERO,
            planning_quantity=ZERO,
            expired_quantity=lot.current_quantity,
            review_quantity=ZERO,
            inventory_status=InventoryStatus.EXPIRED,
            surplus_source=None,
            triage_reason_codes=[
                "EXPIRED_HARD_REJECT"
            ],
            triage_confidence_status=(
                TriageConfidenceStatus.HIGH
            ),
            urgency_level=UrgencyLevel.HIGH,
            estimated_current_value=(
                lot.current_quantity * lot.unit_cost
            ),
            triage_policy_version=triage_policy_version,
        )

    critical_storage_evidence_missing = (
        cold_chain_evidence_required
        and (
            lot.storage_history_status
            is not StorageHistoryStatus.VERIFIED_ACCEPTABLE
            or lot.temperature_log_available is not True
        )
    )

    if critical_storage_evidence_missing:
        return InventoryTriageResult(
            source_lot_id=lot.lot_id,
            analysis_date=analysis_at.date(),
            remaining_shelf_life_days=(
                remaining_shelf_life_days
            ),
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
                "UNKNOWN_STORAGE_HISTORY"
            ],
            triage_confidence_status=(
                TriageConfidenceStatus.LOW
            ),
            urgency_level=UrgencyLevel.HIGH,
            estimated_current_value=(
                lot.current_quantity * lot.unit_cost
            ),
            triage_policy_version=triage_policy_version,
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

    is_within_monitor_window = (
        remaining_shelf_life_days is not None
        and 0 <= remaining_shelf_life_days
        <= expiry_monitor_threshold_days
    )
    expected_to_sell_normally = (
        lot.current_quantity <= expected_normal_sales
    )

    if is_within_monitor_window and expected_to_sell_normally:
        return InventoryTriageResult(
            source_lot_id=lot.lot_id,
            analysis_date=analysis_at.date(),
            remaining_shelf_life_days=(
                remaining_shelf_life_days
            ),
            remaining_safe_window_hours=None,
            remaining_commercial_window_days=None,
            average_daily_sales=average_daily_sales,
            effective_sales_window_days=(
                effective_sales_window_days
            ),
            expected_normal_sales=expected_normal_sales,
            protected_normal_stock_quantity=ZERO,
            monitor_quantity=lot.current_quantity,
            surplus_candidate_quantity=ZERO,
            planning_quantity=ZERO,
            expired_quantity=ZERO,
            review_quantity=ZERO,
            inventory_status=InventoryStatus.MONITOR,
            surplus_source=None,
            triage_reason_codes=[
                "WITHIN_EXPIRY_MONITOR_WINDOW"
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

    if (
        is_within_monitor_window
        and lot.current_quantity > expected_normal_sales
    ):
        monitor_quantity = min(
            lot.current_quantity,
            expected_normal_sales,
        )
        surplus_quantity = (
            lot.current_quantity - monitor_quantity
        )

        return InventoryTriageResult(
            source_lot_id=lot.lot_id,
            analysis_date=analysis_at.date(),
            remaining_shelf_life_days=(
                remaining_shelf_life_days
            ),
            remaining_safe_window_hours=None,
            remaining_commercial_window_days=None,
            average_daily_sales=average_daily_sales,
            effective_sales_window_days=(
                effective_sales_window_days
            ),
            expected_normal_sales=expected_normal_sales,
            protected_normal_stock_quantity=ZERO,
            monitor_quantity=monitor_quantity,
            surplus_candidate_quantity=surplus_quantity,
            planning_quantity=surplus_quantity,
            expired_quantity=ZERO,
            review_quantity=ZERO,
            inventory_status=(
                InventoryStatus.SURPLUS_CANDIDATE
            ),
            surplus_source=SurplusSource.CALCULATED,
            triage_reason_codes=[
                "PARTIAL_EXCESS_WITH_MONITORED_NORMAL_STOCK"
            ],
            triage_confidence_status=(
                TriageConfidenceStatus.HIGH
            ),
            urgency_level=UrgencyLevel.HIGH,
            estimated_current_value=(
                lot.current_quantity * lot.unit_cost
            ),
            triage_policy_version=triage_policy_version,
        )

    if lot.current_quantity > protected_stock_limit:
        surplus_quantity = (
            lot.current_quantity
            - protected_normal_stock_quantity
        )

        return InventoryTriageResult(
            source_lot_id=lot.lot_id,
            analysis_date=analysis_at.date(),
            remaining_shelf_life_days=remaining_shelf_life_days,
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
        remaining_shelf_life_days=remaining_shelf_life_days,
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
