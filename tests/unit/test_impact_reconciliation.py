from decimal import Decimal

from afterlife_ai.contracts.impact import OutcomeObservation
from afterlife_ai.impact.reconciliation import reconcile_outcome


def test_partial_outcome_produces_unresolved_quantity() -> None:
    observation = OutcomeObservation(
        reconciled_quantity=Decimal("100"),
        actual_rescued_quantity=Decimal("60"),
        actual_waste_quantity=Decimal("20"),
    )

    result = reconcile_outcome(
        observation=observation,
        expected_rescue_quantity=Decimal("80"),
        expected_waste_quantity=Decimal("20"),
    )

    assert result.unresolved_quantity == Decimal("20")


def test_realized_diversion_ratio_uses_confirmed_outcomes_only() -> None:
    observation = OutcomeObservation(
        reconciled_quantity=Decimal("100"),
        actual_rescued_quantity=Decimal("60"),
        actual_waste_quantity=Decimal("20"),
    )

    result = reconcile_outcome(
        observation=observation,
        expected_rescue_quantity=Decimal("80"),
        expected_waste_quantity=Decimal("20"),
    )

    assert result.realized_diversion_ratio == Decimal("0.75")


def test_reconciliation_reports_expected_vs_realized_delta() -> None:
    observation = OutcomeObservation(
        reconciled_quantity=Decimal("100"),
        actual_rescued_quantity=Decimal("70"),
        actual_waste_quantity=Decimal("20"),
    )

    result = reconcile_outcome(
        observation=observation,
        expected_rescue_quantity=Decimal("80"),
        expected_waste_quantity=Decimal("20"),
    )

    assert result.rescue_quantity_delta == Decimal("-10")
    assert result.waste_quantity_delta == Decimal("0")
    assert result.unresolved_quantity == Decimal("10")


def test_reconciliation_does_not_mutate_observation() -> None:
    observation = OutcomeObservation(
        reconciled_quantity=Decimal("100"),
        actual_rescued_quantity=Decimal("70"),
        actual_waste_quantity=Decimal("20"),
    )

    before = observation.model_dump()

    reconcile_outcome(
        observation=observation,
        expected_rescue_quantity=Decimal("80"),
        expected_waste_quantity=Decimal("20"),
    )

    assert observation.model_dump() == before
