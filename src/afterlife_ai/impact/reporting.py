"""Adapters from production planning/report data to sustainability impact."""

from decimal import Decimal

from afterlife_ai.contracts.impact import (
    BatchSustainabilitySummary,
    ImpactQuantitySlice,
)
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.impact.batch import build_batch_sustainability_summary
from afterlife_ai.planner.report import ReportAllocation

ZERO = Decimal("0")


def build_report_sustainability_summary(
    *,
    planning_lots: list[SurplusPlanningLot],
    selected_allocations: list[ReportAllocation],
    unallocated_quantities: dict[str, Decimal],
) -> BatchSustainabilitySummary:
    """Build batch impact from report allocations plus unallocated surplus."""

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

    return build_batch_sustainability_summary(
        slices=slices
    )


__all__ = ["build_report_sustainability_summary"]
