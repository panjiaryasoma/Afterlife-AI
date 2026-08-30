from decimal import Decimal

from afterlife_ai.impact.summary import build_sustainability_summary


def test_expected_quantities_are_conserved() -> None:
    summary = build_sustainability_summary(
        reconciled_quantity=Decimal("100"),
        expected_rescue_quantity=Decimal("80"),
        expected_waste_quantity=Decimal("20"),
        package_weight_g=Decimal("500"),
    )

    assert (
        summary.expected_rescue_quantity
        + summary.expected_waste_quantity
        == summary.reconciled_quantity
    )


def test_mass_metrics_are_derived_from_package_weight() -> None:
    summary = build_sustainability_summary(
        reconciled_quantity=Decimal("100"),
        expected_rescue_quantity=Decimal("80"),
        expected_waste_quantity=Decimal("20"),
        package_weight_g=Decimal("500"),
    )

    assert summary.expected_rescue_mass_kg == Decimal("40")
    assert summary.expected_waste_mass_kg == Decimal("10")


def test_missing_weight_does_not_invent_mass_metrics() -> None:
    summary = build_sustainability_summary(
        reconciled_quantity=Decimal("100"),
        expected_rescue_quantity=Decimal("80"),
        expected_waste_quantity=Decimal("20"),
        package_weight_g=None,
    )

    assert summary.expected_rescue_mass_kg is None
    assert summary.expected_waste_mass_kg is None
