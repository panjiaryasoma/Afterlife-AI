"""Deterministic hard gates for rescue candidates."""

from pydantic import BaseModel, ConfigDict, Field

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    CoverageStatus,
    FeasibilityStatus,
    MatchStatus,
    ModelScoringStatus,
    SafetyStatus,
    ValidationStatus,
)


class HardGateContext(BaseModel):
    """External deterministic facts needed to evaluate hard gates."""

    model_config = ConfigDict(extra="forbid")

    validation_passed: bool
    coverage_supported: bool
    safety_status: SafetyStatus
    verification_sufficient: bool

    storage_compatible: bool
    timing_feasible: bool
    action_eligible: bool

    shelf_life_feasible: bool = True
    logistics_feasible: bool = True

    partner_demand_fresh: bool = True

    qualifying_transactions: int = Field(
        default=0,
        ge=0,
    )


def evaluate_hard_gates(
    candidate: CandidateAction,
    context: HardGateContext,
) -> CandidateAction:
    """Apply non-negotiable feasibility gates before scoring."""

    rejection_reason_codes: list[str] = []

    validation_status = (
        ValidationStatus.PASSED
        if context.validation_passed
        else ValidationStatus.FAILED
    )

    if not context.validation_passed:
        rejection_reason_codes.append(
            "VALIDATION_FAILED"
        )

    coverage_status = (
        CoverageStatus.SUPPORTED
        if context.coverage_supported
        else CoverageStatus.UNSUPPORTED
    )

    if not context.coverage_supported:
        rejection_reason_codes.append(
            "UNSUPPORTED_FEATURE_COVERAGE"
        )

    if context.safety_status is SafetyStatus.HARD_REJECT:
        rejection_reason_codes.append(
            "SAFETY_HARD_REJECT"
        )

    elif context.safety_status is SafetyStatus.UNVERIFIED:
        rejection_reason_codes.append(
            "SAFETY_UNVERIFIED"
        )

    if not context.verification_sufficient:
        rejection_reason_codes.append(
            "VERIFICATION_INSUFFICIENT"
        )

    storage_status = (
        MatchStatus.MATCH
        if context.storage_compatible
        else MatchStatus.MISMATCH
    )

    if not context.storage_compatible:
        rejection_reason_codes.append(
            "STORAGE_INCOMPATIBLE"
        )

    if not context.shelf_life_feasible:
        rejection_reason_codes.append(
            "SHELF_LIFE_INFEASIBLE"
        )

    if not context.timing_feasible:
        rejection_reason_codes.append(
            "TIMING_INFEASIBLE"
        )

    if not context.logistics_feasible:
        rejection_reason_codes.append(
            "LOGISTICS_INFEASIBLE"
        )

    if not context.action_eligible:
        rejection_reason_codes.append(
            "ACTION_NOT_ELIGIBLE"
        )

    if (
        candidate.available_capacity is not None
        and candidate.available_capacity
        < candidate.maximum_feasible_quantity
    ):
        rejection_reason_codes.append(
            "INSUFFICIENT_CAPACITY"
        )

    if (
        candidate.minimum_order_quantity is not None
        and candidate.maximum_feasible_quantity
        < candidate.minimum_order_quantity
    ):
        rejection_reason_codes.append(
            "MINIMUM_ORDER_NOT_MET"
        )

    if (
        candidate.action_type
        is ActionType.PROMOTIONAL_BONUS
        and context.qualifying_transactions <= 0
    ):
        rejection_reason_codes.append(
            "NO_QUALIFYING_TRANSACTION"
        )

    if (
        candidate.action_type
        is ActionType.EXTERNAL_PARTNER
    ):
        if not context.partner_demand_fresh:
            rejection_reason_codes.append(
                "STALE_PARTNER_DEMAND"
            )

        if (
            candidate.active_demand_quantity is None
            or candidate.active_demand_quantity <= 0
        ):
            rejection_reason_codes.append(
                "NO_ACTIVE_PARTNER_DEMAND"
            )

        elif (
            candidate.maximum_feasible_quantity
            > candidate.active_demand_quantity
        ):
            rejection_reason_codes.append(
                "ACTIVE_DEMAND_QUANTITY_EXCEEDED"
            )

        if (
            candidate.category_match_status
            is not MatchStatus.MATCH
        ):
            rejection_reason_codes.append(
                "PARTNER_CATEGORY_MISMATCH"
            )

        if (
            candidate.package_size_match_status
            is not MatchStatus.MATCH
        ):
            rejection_reason_codes.append(
                "PARTNER_PACKAGE_SIZE_MISMATCH"
            )

        if (
            candidate.customer_segment_match_status
            is not MatchStatus.MATCH
        ):
            rejection_reason_codes.append(
                "PARTNER_CUSTOMER_SEGMENT_MISMATCH"
            )

    # Deduplicate without losing deterministic order.
    rejection_reason_codes = list(
        dict.fromkeys(rejection_reason_codes)
    )

    if rejection_reason_codes:
        if rejection_reason_codes == [
            "UNSUPPORTED_FEATURE_COVERAGE"
        ]:
            feasibility_status = (
                FeasibilityStatus.UNSUPPORTED
            )
        else:
            feasibility_status = (
                FeasibilityStatus.INFEASIBLE
            )

        model_scoring_status = (
            ModelScoringStatus.BLOCKED
        )

    else:
        feasibility_status = (
            FeasibilityStatus.FEASIBLE
        )
        model_scoring_status = (
            ModelScoringStatus.DEFERRED
        )

    return candidate.model_copy(
        update={
            "validation_status": validation_status,
            "coverage_status": coverage_status,
            "safety_status": context.safety_status,
            "storage_compatibility_status": (
                storage_status
            ),
            "feasibility_status": (
                feasibility_status
            ),
            "model_scoring_status": (
                model_scoring_status
            ),
            "rejection_reason_codes": (
                rejection_reason_codes
            ),
        }
    )


__all__ = [
    "HardGateContext",
    "evaluate_hard_gates",
]
