"""Expected sustainability impact calculations."""

from decimal import Decimal

from afterlife_ai.contracts.impact import SustainabilitySummary

ZERO = Decimal("0")
GRAMS_PER_KILOGRAM = Decimal("1000")
QUANTITY_TOLERANCE = Decimal("1E-18")


def build_sustainability_summary(
    *,
    reconciled_quantity: Decimal,
    expected_rescue_quantity: Decimal,
    expected_waste_quantity: Decimal,
    package_weight_g: Decimal | None,
) -> SustainabilitySummary:
    """Build expected impact without inventing missing mass evidence."""

    expected_total = (
        expected_rescue_quantity
        + expected_waste_quantity
    )

    if (
        abs(expected_total - reconciled_quantity)
        > QUANTITY_TOLERANCE
    ):
        raise ValueError(
            "expected rescue quantity + expected waste quantity "
            "must equal reconciled quantity."
        )

    if package_weight_g is not None and package_weight_g < ZERO:
        raise ValueError("package_weight_g cannot be negative.")

    expected_rescue_ratio = (
        expected_rescue_quantity / reconciled_quantity
        if reconciled_quantity > ZERO
        else None
    )

    expected_rescue_mass_kg: Decimal | None = None
    expected_waste_mass_kg: Decimal | None = None

    if package_weight_g is not None:
        expected_rescue_mass_kg = (
            expected_rescue_quantity
            * package_weight_g
            / GRAMS_PER_KILOGRAM
        )
        expected_waste_mass_kg = (
            expected_waste_quantity
            * package_weight_g
            / GRAMS_PER_KILOGRAM
        )

    return SustainabilitySummary(
        reconciled_quantity=reconciled_quantity,
        expected_rescue_quantity=expected_rescue_quantity,
        expected_waste_quantity=expected_waste_quantity,
        expected_rescue_ratio=expected_rescue_ratio,
        expected_rescue_mass_kg=expected_rescue_mass_kg,
        expected_waste_mass_kg=expected_waste_mass_kg,
    )


__all__ = ["build_sustainability_summary"]
