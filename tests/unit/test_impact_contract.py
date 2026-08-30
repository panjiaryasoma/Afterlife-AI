from decimal import Decimal

import pytest
from pydantic import ValidationError

from afterlife_ai.contracts.impact import OutcomeObservation


def test_outcome_observation_accepts_partial_confirmation() -> None:
    observation = OutcomeObservation(
        reconciled_quantity=Decimal("100"),
        actual_rescued_quantity=Decimal("60"),
        actual_waste_quantity=Decimal("20"),
    )

    assert observation.reconciled_quantity == Decimal("100")
    assert observation.actual_rescued_quantity == Decimal("60")
    assert observation.actual_waste_quantity == Decimal("20")


def test_outcome_observation_rejects_confirmed_quantity_above_scope() -> None:
    with pytest.raises(ValidationError):
        OutcomeObservation(
            reconciled_quantity=Decimal("100"),
            actual_rescued_quantity=Decimal("90"),
            actual_waste_quantity=Decimal("20"),
        )


def test_outcome_observation_rejects_negative_actual_quantity() -> None:
    with pytest.raises(ValidationError):
        OutcomeObservation(
            reconciled_quantity=Decimal("100"),
            actual_rescued_quantity=Decimal("-1"),
            actual_waste_quantity=Decimal("0"),
        )
