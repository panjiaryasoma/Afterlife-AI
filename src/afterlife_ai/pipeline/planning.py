"""Production adapter from triage results to surplus planning lots."""

from __future__ import annotations

from afterlife_ai.contracts.enums import (
    DefectSeverity,
    InventoryStatus,
    PackagingCondition,
    ProductCondition,
    StorageRequirementMode,
)
from afterlife_ai.contracts.inventory import RawInventoryLot
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.contracts.triage import InventoryTriageResult
from afterlife_ai.pipeline.runtime_config import RuntimeConfig
from afterlife_ai.planner.planning_lots import (
    build_surplus_planning_lot,
)


def _storage_requirement_mode(
    *,
    cold_chain_evidence_required: bool,
) -> StorageRequirementMode:
    """Translate runtime category policy into planner storage semantics."""

    if cold_chain_evidence_required:
        return StorageRequirementMode.SAFETY_CRITICAL_COLD_CHAIN

    return StorageRequirementMode.AMBIENT_ALLOWED


def _defect_severity(
    lot: RawInventoryLot,
) -> DefectSeverity:
    """Derive deterministic defect severity from validated inventory fields."""

    safety_critical_packaging = {
        PackagingCondition.PRIMARY_BARRIER_DAMAGED,
        PackagingCondition.LEAKING,
        PackagingCondition.OPEN_SEAL,
    }

    if (
        lot.packaging_condition in safety_critical_packaging
        or lot.product_condition is ProductCondition.DAMAGED
    ):
        return DefectSeverity.SAFETY_CRITICAL

    if (
        lot.packaging_condition
        is PackagingCondition.COSMETIC_LABEL_DAMAGE
    ):
        return DefectSeverity.COSMETIC_ONLY

    if (
        lot.packaging_condition is PackagingCondition.INTACT
        and lot.product_condition
        in {
            ProductCondition.GOOD,
            ProductCondition.VISUALLY_NORMAL,
        }
    ):
        return DefectSeverity.NONE

    return DefectSeverity.MANUAL_REVIEW


def build_production_planning_lots(
    *,
    lots: list[RawInventoryLot],
    triage_results: list[InventoryTriageResult],
    config: RuntimeConfig,
) -> list[SurplusPlanningLot]:
    """Build planning lots only from planner-eligible surplus."""

    triage_by_lot = {
        result.source_lot_id: result
        for result in triage_results
    }

    if len(triage_by_lot) != len(triage_results):
        raise ValueError(
            "Triage results mengandung duplicate source_lot_id."
        )

    planning_lots: list[SurplusPlanningLot] = []

    for lot in lots:
        triage = triage_by_lot.get(lot.lot_id)

        if triage is None:
            raise ValueError(
                "Triage result tidak ditemukan untuk "
                f"inventory lot {lot.lot_id}."
            )

        if (
            triage.inventory_status
            is not InventoryStatus.SURPLUS_CANDIDATE
            or triage.planning_quantity <= 0
        ):
            continue

        category_policy = (
            config.triage.category_policies.get(
                lot.product_category
            )
        )

        if category_policy is None:
            raise ValueError(
                "Planner-eligible lot tidak memiliki runtime "
                f"category policy: {lot.product_category.value}."
            )

        planning_lot = build_surplus_planning_lot(
            lot,
            triage,
            storage_requirement_mode=(
                _storage_requirement_mode(
                    cold_chain_evidence_required=(
                        category_policy
                        .cold_chain_evidence_required
                    )
                )
            ),
            defect_severity=_defect_severity(lot),
        )

        if planning_lot is None:
            raise RuntimeError(
                "Planner-eligible triage gagal menghasilkan "
                f"planning lot untuk {lot.lot_id}."
            )

        planning_lots.append(planning_lot)

    return planning_lots


__all__ = ["build_production_planning_lots"]
