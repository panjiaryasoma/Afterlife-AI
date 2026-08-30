"""Batch sustainability impact aggregation across mixed inventory lots."""

from decimal import Decimal

from afterlife_ai.contracts.impact import (
    BatchSustainabilitySummary,
    ImpactQuantitySlice,
)

ZERO = Decimal("0")
GRAMS_PER_KILOGRAM = Decimal("1000")


def build_batch_sustainability_summary(
    *,
    slices: list[ImpactQuantitySlice],
) -> BatchSustainabilitySummary:
    """Aggregate expected impact without overstating partial mass evidence."""

    reconciled_quantity = sum(
        (item.reconciled_quantity for item in slices),
        ZERO,
    )
    expected_rescue_quantity = sum(
        (item.expected_rescue_quantity for item in slices),
        ZERO,
    )
    expected_waste_quantity = sum(
        (item.expected_waste_quantity for item in slices),
        ZERO,
    )

    expected_rescue_ratio = (
        expected_rescue_quantity / reconciled_quantity
        if reconciled_quantity > ZERO
        else None
    )

    relevant_slices = [
        item
        for item in slices
        if item.reconciled_quantity > ZERO
    ]
    weighted_slices = [
        item
        for item in relevant_slices
        if item.package_weight_g is not None
    ]

    if not relevant_slices or not weighted_slices:
        coverage = "NONE"
    elif len(weighted_slices) == len(relevant_slices):
        coverage = "COMPLETE"
    else:
        coverage = "PARTIAL"

    expected_rescue_mass_kg: Decimal | None = None
    expected_waste_mass_kg: Decimal | None = None

    if coverage == "COMPLETE":
        expected_rescue_mass_kg = sum(
            (
                item.expected_rescue_quantity
                * item.package_weight_g
                / GRAMS_PER_KILOGRAM
                for item in relevant_slices
                if item.package_weight_g is not None
            ),
            ZERO,
        )
        expected_waste_mass_kg = sum(
            (
                item.expected_waste_quantity
                * item.package_weight_g
                / GRAMS_PER_KILOGRAM
                for item in relevant_slices
                if item.package_weight_g is not None
            ),
            ZERO,
        )

    return BatchSustainabilitySummary(
        reconciled_quantity=reconciled_quantity,
        expected_rescue_quantity=expected_rescue_quantity,
        expected_waste_quantity=expected_waste_quantity,
        expected_rescue_ratio=expected_rescue_ratio,
        mass_evidence_coverage=coverage,
        expected_rescue_mass_kg=expected_rescue_mass_kg,
        expected_waste_mass_kg=expected_waste_mass_kg,
    )


__all__ = ["build_batch_sustainability_summary"]
