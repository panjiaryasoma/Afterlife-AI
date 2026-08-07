"""Build planner-eligible surplus planning lots."""

from afterlife_ai.contracts.enums import (
    DefectSeverity,
    InventoryStatus,
    StorageRequirementMode,
)
from afterlife_ai.contracts.inventory import RawInventoryLot
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.contracts.triage import InventoryTriageResult


def build_surplus_planning_lot(
    lot: RawInventoryLot,
    triage: InventoryTriageResult,
    *,
    storage_requirement_mode: StorageRequirementMode,
    defect_severity: DefectSeverity,
) -> SurplusPlanningLot | None:
    """Build one planning lot only from planner-eligible surplus quantity."""

    if triage.source_lot_id != lot.lot_id:
        raise ValueError(
            "triage source_lot_id harus sama dengan inventory lot_id."
        )

    if (
        triage.inventory_status is not InventoryStatus.SURPLUS_CANDIDATE
        or triage.planning_quantity <= 0
    ):
        return None

    if triage.surplus_source is None:
        raise ValueError(
            "surplus_source wajib tersedia untuk planner-eligible surplus."
        )

    return SurplusPlanningLot(
        planning_lot_id=f"PLAN-{lot.lot_id}",
        source_lot_id=lot.lot_id,
        sku=lot.sku,
        product_name=lot.product_name,
        product_category=lot.product_category,
        product_subcategory=lot.product_subcategory,
        planning_quantity=triage.planning_quantity,
        unit=lot.unit,
        unit_cost=lot.unit_cost,
        normal_selling_price=lot.normal_selling_price,
        minimum_recovery_price=lot.minimum_recovery_price,
        source_location=lot.source_location,
        remaining_shelf_life_days=triage.remaining_shelf_life_days,
        remaining_safe_window_hours=triage.remaining_safe_window_hours,
        remaining_commercial_window_days=(
            triage.remaining_commercial_window_days
        ),
        urgency_level=triage.urgency_level,
        surplus_source=triage.surplus_source,
        seasonality_status=None,
        storage_type=lot.storage_type,
        storage_requirement_mode=storage_requirement_mode,
        storage_history_status=lot.storage_history_status,
        product_condition=lot.product_condition,
        packaging_condition=lot.packaging_condition,
        defect_severity=defect_severity,
        quality_inspection_status=lot.quality_inspection_status,
        verification_status=lot.verification_status,
        package_volume_ml=lot.package_volume_ml,
        package_weight_g=lot.package_weight_g,
        package_format=lot.package_format,
        estimated_current_value=triage.estimated_current_value,
    )


__all__ = ["build_surplus_planning_lot"]
