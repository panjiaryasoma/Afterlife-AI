"""Production expected-value calculation for scored rescue candidates."""

from __future__ import annotations

from decimal import Decimal

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import ModelScoringStatus
from afterlife_ai.planner.value import (
    ExpectedValueInput,
    calculate_expected_value,
)

ZERO = Decimal("0")


def _apply_expected_value(
    candidate: CandidateAction,
) -> CandidateAction:
    """Calculate deterministic economic value for one scored candidate."""

    if (
        candidate.model_scoring_status
        is not ModelScoringStatus.ALLOWED
    ):
        raise ValueError(
            "Expected-value calculation hanya menerima "
            f"candidate ALLOWED: {candidate.candidate_id}."
        )

    probability = (
        candidate.estimated_rescue_success_score
    )

    if probability is None:
        raise ValueError(
            "Candidate tidak memiliki rescue-success score: "
            f"{candidate.candidate_id}."
        )

    quantity = candidate.maximum_feasible_quantity

    if quantity <= ZERO:
        raise ValueError(
            "maximum_feasible_quantity harus positif untuk "
            f"{candidate.candidate_id}."
        )

    cash_recovery_per_unit = (
        candidate.offered_or_selling_price_per_unit
        or ZERO
    )

    value_result = calculate_expected_value(
        ExpectedValueInput(
            rescue_probability=probability,
            quantity=quantity,
            cash_recovery_per_unit=(
                cash_recovery_per_unit
            ),
            future_branch_recovery_per_unit=ZERO,
            avoided_purchase_cost_per_unit=ZERO,
            direct_action_cost_per_unit=(
                candidate.direct_action_cost
                / quantity
            ),
            logistics_cost_per_unit=(
                candidate.logistics_cost
                / quantity
            ),
            handling_cost_per_unit=(
                candidate.handling_cost
                / quantity
            ),
            failure_penalty_per_unit=ZERO,
        )
    )

    total_success_value = (
        cash_recovery_per_unit * quantity
        - candidate.direct_action_cost
        - candidate.logistics_cost
        - candidate.handling_cost
    )

    exact_expected_net_recovery = (
        probability * total_success_value
    )

    return candidate.model_copy(
        update={
            "expected_cash_recovery": (
                value_result.expected_cash_recovery
            ),
            "expected_future_branch_recovery": (
                value_result
                .expected_future_branch_recovery
            ),
            "expected_avoided_purchase_cost": (
                value_result
                .expected_avoided_purchase_cost
            ),
            "expected_physical_rescue_quantity": (
                value_result
                .expected_physical_rescue_quantity
            ),
            "expected_waste_quantity": (
                value_result.expected_waste_quantity
            ),
            "expected_net_recovery": (
                exact_expected_net_recovery
            ),
        }
    )


def apply_production_expected_values(
    *,
    candidates: list[CandidateAction],
) -> list[CandidateAction]:
    """Apply expected-value calculation without reviving blocked candidates."""

    valued: list[CandidateAction] = []

    for candidate in candidates:
        if (
            candidate.model_scoring_status
            is ModelScoringStatus.BLOCKED
        ):
            valued.append(candidate)
            continue

        valued.append(
            _apply_expected_value(candidate)
        )

    return valued


__all__ = ["apply_production_expected_values"]
