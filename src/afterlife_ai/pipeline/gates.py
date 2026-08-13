"""Production deterministic hard-gate context and evaluation."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    DefectSeverity,
    MatchStatus,
    SafetyStatus,
    StorageHistoryStatus,
    StorageRequirementMode,
    UrgencyLevel,
    VerificationStatus,
)
from afterlife_ai.contracts.inventory import RawInventoryLot
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.pipeline.runtime_config import RuntimeConfig
from afterlife_ai.planner.gates import (
    HardGateContext,
    evaluate_hard_gates,
)

HOURS_PER_DAY = Decimal("24")


def _safety_status(
    *,
    planning_lot: SurplusPlanningLot,
    raw_lot: RawInventoryLot,
) -> SafetyStatus:
    """Derive safety state from deterministic product and storage evidence."""

    if (
        planning_lot.defect_severity
        is DefectSeverity.SAFETY_CRITICAL
        or raw_lot.storage_history_status
        is StorageHistoryStatus.VERIFIED_FAILURE
    ):
        return SafetyStatus.HARD_REJECT

    if (
        planning_lot.defect_severity
        is DefectSeverity.MANUAL_REVIEW
    ):
        return SafetyStatus.UNVERIFIED

    if (
        planning_lot.storage_requirement_mode
        is StorageRequirementMode.SAFETY_CRITICAL_COLD_CHAIN
        and (
            raw_lot.storage_history_status
            is not StorageHistoryStatus.VERIFIED_ACCEPTABLE
            or raw_lot.temperature_log_available is not True
        )
    ):
        return SafetyStatus.UNVERIFIED

    if planning_lot.urgency_level in {
        UrgencyLevel.HIGH,
        UrgencyLevel.CRITICAL,
    }:
        return SafetyStatus.ACCEPTABLE_WITH_URGENCY

    return SafetyStatus.ACCEPTABLE


def _verification_sufficient(
    planning_lot: SurplusPlanningLot,
) -> bool:
    """Require verified evidence before automatic model scoring."""

    return planning_lot.verification_status in {
        VerificationStatus.VERIFIED,
        VerificationStatus.PHYSICALLY_INSPECTED,
    }


def _storage_compatible(
    *,
    planning_lot: SurplusPlanningLot,
    raw_lot: RawInventoryLot,
) -> bool:
    """Check whether known source storage evidence satisfies requirements."""

    if (
        planning_lot.storage_requirement_mode
        is not StorageRequirementMode.SAFETY_CRITICAL_COLD_CHAIN
    ):
        return True

    return (
        raw_lot.storage_history_status
        is StorageHistoryStatus.VERIFIED_ACCEPTABLE
        and raw_lot.temperature_log_available is True
    )


def _binding_window_hours(
    planning_lot: SurplusPlanningLot,
) -> Decimal | None:
    """Return the earliest known safety/commercial execution window."""

    windows: list[Decimal] = []

    if planning_lot.remaining_safe_window_hours is not None:
        windows.append(
            planning_lot.remaining_safe_window_hours
        )

    if (
        planning_lot.remaining_commercial_window_days
        is not None
    ):
        windows.append(
            planning_lot.remaining_commercial_window_days
            * HOURS_PER_DAY
        )

    if planning_lot.remaining_shelf_life_days is not None:
        windows.append(
            Decimal(
                planning_lot.remaining_shelf_life_days
            )
            * HOURS_PER_DAY
        )

    if not windows:
        return None

    return min(windows)


def _timing_feasible(
    *,
    candidate: CandidateAction,
    planning_lot: SurplusPlanningLot,
    analysis_at: datetime,
    rescue_deadline_at: datetime | None,
) -> bool:
    """Require completion to fit the earliest binding timing window."""

    completion = candidate.estimated_completion_hours

    if completion is None:
        return False

    windows: list[Decimal] = []

    binding_window = _binding_window_hours(
        planning_lot
    )

    if binding_window is not None:
        windows.append(binding_window)

    if rescue_deadline_at is not None:
        deadline_delta = (
            rescue_deadline_at - analysis_at
        )

        deadline_hours = (
            Decimal(
                str(deadline_delta.total_seconds())
            )
            / Decimal("3600")
        )

        windows.append(deadline_hours)

    if not windows:
        return True

    return completion <= min(windows)


def _shelf_life_feasible(
    *,
    candidate: CandidateAction,
    planning_lot: SurplusPlanningLot,
) -> bool:
    """Reject an action that cannot finish within known shelf life."""

    remaining_days = (
        planning_lot.remaining_shelf_life_days
    )

    if remaining_days is None:
        return True

    if remaining_days < 0:
        return False

    completion = candidate.estimated_completion_hours

    if completion is None:
        return False

    return (
        completion
        <= Decimal(remaining_days) * HOURS_PER_DAY
    )


def _coverage_supported(
    *,
    candidate: CandidateAction,
    planning_lot: SurplusPlanningLot,
    config: RuntimeConfig,
) -> bool:
    """Check static MVP domain and action coverage."""

    category_supported = (
        planning_lot.product_category
        in config.triage.category_policies
    )

    action_supported = (
        config.capabilities.supported_actions.get(
            candidate.action_type,
            False,
        )
    )

    return category_supported and action_supported


def _action_eligible(
    *,
    candidate: CandidateAction,
    config: RuntimeConfig,
) -> bool:
    """Check deterministic runtime action enablement."""

    return config.capabilities.supported_actions.get(
        candidate.action_type,
        False,
    )


def _logistics_feasible(
    candidate: CandidateAction,
) -> bool:
    """Remain conservative until a runtime logistics budget is configured."""

    return candidate.logistics_cost == Decimal("0")


def apply_production_hard_gates(
    *,
    candidates: list[CandidateAction],
    planning_lots: list[SurplusPlanningLot],
    raw_inventory_lots: list[RawInventoryLot],
    config: RuntimeConfig,
    analysis_at: datetime,
    rescue_deadline_at: datetime | None = None,
) -> list[CandidateAction]:
    """Build deterministic gate facts and evaluate every candidate."""

    if analysis_at.tzinfo is None:
        raise ValueError(
            "analysis_at wajib timezone-aware."
        )

    if (
        rescue_deadline_at is not None
        and rescue_deadline_at.tzinfo is None
    ):
        raise ValueError(
            "rescue_deadline_at wajib timezone-aware."
        )

    planning_by_id = {
        item.planning_lot_id: item
        for item in planning_lots
    }

    raw_by_id = {
        item.lot_id: item
        for item in raw_inventory_lots
    }

    gated: list[CandidateAction] = []

    for candidate in candidates:
        planning_lot = planning_by_id.get(
            candidate.planning_lot_id
        )

        if planning_lot is None:
            raise ValueError(
                "Planning lot tidak ditemukan untuk candidate "
                f"{candidate.candidate_id}."
            )

        raw_lot = raw_by_id.get(
            planning_lot.source_lot_id
        )

        if raw_lot is None:
            raise ValueError(
                "Raw inventory lot tidak ditemukan untuk "
                f"{planning_lot.planning_lot_id}."
            )

        context = HardGateContext(
            validation_passed=True,
            coverage_supported=_coverage_supported(
                candidate=candidate,
                planning_lot=planning_lot,
                config=config,
            ),
            safety_status=_safety_status(
                planning_lot=planning_lot,
                raw_lot=raw_lot,
            ),
            verification_sufficient=(
                _verification_sufficient(
                    planning_lot
                )
            ),
            storage_compatible=(
                _storage_compatible(
                    planning_lot=planning_lot,
                    raw_lot=raw_lot,
                )
                and (
                    candidate.action_type
                    is not ActionType.EXTERNAL_PARTNER
                    or (
                        candidate.storage_compatibility_status
                        is MatchStatus.MATCH
                    )
                )
            ),
            timing_feasible=_timing_feasible(
                candidate=candidate,
                planning_lot=planning_lot,
                analysis_at=analysis_at,
                rescue_deadline_at=rescue_deadline_at,
            ),
            action_eligible=_action_eligible(
                candidate=candidate,
                config=config,
            ),
            shelf_life_feasible=(
                _shelf_life_feasible(
                    candidate=candidate,
                    planning_lot=planning_lot,
                )
            ),
            logistics_feasible=(
                _logistics_feasible(candidate)
            ),
            partner_demand_fresh=(
                candidate.action_type
                is not ActionType.EXTERNAL_PARTNER
                or (
                    candidate.demand_freshness_hours
                    is not None
                    and candidate.demand_freshness_hours
                    > Decimal("0")
                )
            ),
            qualifying_transactions=0,
        )

        gated.append(
            evaluate_hard_gates(
                candidate,
                context,
            )
        )

    return gated


__all__ = ["apply_production_hard_gates"]
