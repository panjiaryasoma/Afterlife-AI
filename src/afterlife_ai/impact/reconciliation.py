"""Operator-confirmed outcome reconciliation."""

from decimal import Decimal

from afterlife_ai.contracts.impact import (
    OutcomeObservation,
    OutcomeReconciliation,
)

ZERO = Decimal("0")
QUANTITY_TOLERANCE = Decimal("1E-18")


def reconcile_outcome(
    *,
    observation: OutcomeObservation,
    expected_rescue_quantity: Decimal,
    expected_waste_quantity: Decimal,
) -> OutcomeReconciliation:
    """Compare expected quantities with confirmed actual outcomes."""

    expected_total = (
        expected_rescue_quantity
        + expected_waste_quantity
    )

    if (
        abs(expected_total - observation.reconciled_quantity)
        > QUANTITY_TOLERANCE
    ):
        raise ValueError(
            "expected rescue quantity + expected waste quantity "
            "must equal reconciled quantity."
        )

    confirmed_quantity = (
        observation.actual_rescued_quantity
        + observation.actual_waste_quantity
    )

    unresolved_quantity = (
        observation.reconciled_quantity
        - confirmed_quantity
    )

    realized_diversion_ratio = (
        observation.actual_rescued_quantity
        / confirmed_quantity
        if confirmed_quantity > ZERO
        else None
    )

    return OutcomeReconciliation(
        reconciled_quantity=observation.reconciled_quantity,
        actual_rescued_quantity=observation.actual_rescued_quantity,
        actual_waste_quantity=observation.actual_waste_quantity,
        unresolved_quantity=unresolved_quantity,
        realized_diversion_ratio=realized_diversion_ratio,
        rescue_quantity_delta=(
            observation.actual_rescued_quantity
            - expected_rescue_quantity
        ),
        waste_quantity_delta=(
            observation.actual_waste_quantity
            - expected_waste_quantity
        ),
    )


__all__ = ["reconcile_outcome"]
