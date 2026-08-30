"""Adapters from production planning/report data to sustainability impact."""

from decimal import Decimal

from afterlife_ai.contracts.impact import (
    BatchSustainabilitySummary,
    ImpactQuantitySlice,
)
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.impact.batch import build_batch_sustainability_summary
from afterlife_ai.planner.report import (
    ReportAllocation,
    ReportBatchMetrics,
)

ZERO = Decimal("0")


def build_report_sustainability_summary(
    *,
    planning_lots: list[SurplusPlanningLot],
    selected_allocations: list[ReportAllocation],
    unallocated_quantities: dict[str, Decimal],
    batch_metrics: ReportBatchMetrics,
) -> BatchSustainabilitySummary:
    """Build impact while preserving canonical report quantity semantics."""

    planning_by_id = {
        lot.planning_lot_id: lot
        for lot in planning_lots
    }
    slices: list[ImpactQuantitySlice] = []

    for allocation in selected_allocations:
        planning_lot = planning_by_id[
            allocation.planning_lot_id
        ]
        slices.append(
            ImpactQuantitySlice(
                source_lot_id=allocation.source_lot_id,
                reconciled_quantity=allocation.allocated_quantity,
                expected_rescue_quantity=(
                    allocation.expected_physical_rescue_quantity
                ),
                expected_waste_quantity=(
                    allocation.expected_waste_quantity
                ),
                package_weight_g=planning_lot.package_weight_g,
            )
        )

    for planning_lot_id, quantity in unallocated_quantities.items():
        if quantity <= ZERO:
            continue

        planning_lot = planning_by_id[planning_lot_id]
        slices.append(
            ImpactQuantitySlice(
                source_lot_id=planning_lot.source_lot_id,
                reconciled_quantity=quantity,
                expected_rescue_quantity=ZERO,
                expected_waste_quantity=quantity,
                package_weight_g=planning_lot.package_weight_g,
            )
        )

    detailed_summary = build_batch_sustainability_summary(
        slices=slices
    )

    expected_rescue_quantity = (
        batch_metrics.expected_physical_rescue_quantity
        if batch_metrics.expected_physical_rescue_quantity is not None
        else detailed_summary.expected_rescue_quantity
    )
    expected_waste_quantity = (
        batch_metrics.expected_waste_quantity
        if batch_metrics.expected_waste_quantity is not None
        else detailed_summary.expected_waste_quantity
    )
    expected_rescue_ratio = (
        batch_metrics.expected_rescue_ratio
        if batch_metrics.expected_rescue_ratio is not None
        else detailed_summary.expected_rescue_ratio
    )

    return BatchSustainabilitySummary(
        reconciled_quantity=batch_metrics.planning_quantity,
        expected_rescue_quantity=expected_rescue_quantity,
        expected_waste_quantity=expected_waste_quantity,
        expected_rescue_ratio=expected_rescue_ratio,
        mass_evidence_coverage=(
            detailed_summary.mass_evidence_coverage
        ),
        expected_rescue_mass_kg=(
            detailed_summary.expected_rescue_mass_kg
        ),
        expected_waste_mass_kg=(
            detailed_summary.expected_waste_mass_kg
        ),
    )


__all__ = ["build_report_sustainability_summary"]
