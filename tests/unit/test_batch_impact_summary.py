from decimal import Decimal

from afterlife_ai.contracts.impact import ImpactQuantitySlice
from afterlife_ai.impact.batch import build_batch_sustainability_summary


def test_single_lot_batch_produces_correct_mass_metrics() -> None:
    summary = build_batch_sustainability_summary(
        slices=[
            ImpactQuantitySlice(
                source_lot_id="LOT-A",
                reconciled_quantity=Decimal("100"),
                expected_rescue_quantity=Decimal("80"),
                expected_waste_quantity=Decimal("20"),
                package_weight_g=Decimal("500"),
            )
        ]
    )

    assert summary.mass_evidence_coverage == "COMPLETE"
    assert summary.expected_rescue_mass_kg == Decimal("40")
    assert summary.expected_waste_mass_kg == Decimal("10")


def test_mixed_weight_lots_aggregate_mass_per_source_lot() -> None:
    summary = build_batch_sustainability_summary(
        slices=[
            ImpactQuantitySlice(
                source_lot_id="LOT-A",
                reconciled_quantity=Decimal("50"),
                expected_rescue_quantity=Decimal("40"),
                expected_waste_quantity=Decimal("10"),
                package_weight_g=Decimal("500"),
            ),
            ImpactQuantitySlice(
                source_lot_id="LOT-B",
                reconciled_quantity=Decimal("40"),
                expected_rescue_quantity=Decimal("30"),
                expected_waste_quantity=Decimal("10"),
                package_weight_g=Decimal("250"),
            ),
        ]
    )

    assert summary.reconciled_quantity == Decimal("90")
    assert summary.expected_rescue_quantity == Decimal("70")
    assert summary.expected_waste_quantity == Decimal("20")
    assert summary.mass_evidence_coverage == "COMPLETE"
    assert summary.expected_rescue_mass_kg == Decimal("27.5")
    assert summary.expected_waste_mass_kg == Decimal("7.5")


def test_missing_weight_yields_partial_mass_evidence_coverage() -> None:
    summary = build_batch_sustainability_summary(
        slices=[
            ImpactQuantitySlice(
                source_lot_id="LOT-A",
                reconciled_quantity=Decimal("50"),
                expected_rescue_quantity=Decimal("40"),
                expected_waste_quantity=Decimal("10"),
                package_weight_g=Decimal("500"),
            ),
            ImpactQuantitySlice(
                source_lot_id="LOT-B",
                reconciled_quantity=Decimal("40"),
                expected_rescue_quantity=Decimal("30"),
                expected_waste_quantity=Decimal("10"),
                package_weight_g=None,
            ),
        ]
    )

    assert summary.mass_evidence_coverage == "PARTIAL"


def test_partial_weight_coverage_does_not_claim_batch_mass() -> None:
    summary = build_batch_sustainability_summary(
        slices=[
            ImpactQuantitySlice(
                source_lot_id="LOT-A",
                reconciled_quantity=Decimal("50"),
                expected_rescue_quantity=Decimal("40"),
                expected_waste_quantity=Decimal("10"),
                package_weight_g=Decimal("500"),
            ),
            ImpactQuantitySlice(
                source_lot_id="LOT-B",
                reconciled_quantity=Decimal("40"),
                expected_rescue_quantity=Decimal("30"),
                expected_waste_quantity=Decimal("10"),
                package_weight_g=None,
            ),
        ]
    )

    assert summary.expected_rescue_mass_kg is None
    assert summary.expected_waste_mass_kg is None


def test_no_weight_evidence_produces_no_mass_claim() -> None:
    summary = build_batch_sustainability_summary(
        slices=[
            ImpactQuantitySlice(
                source_lot_id="LOT-A",
                reconciled_quantity=Decimal("10"),
                expected_rescue_quantity=Decimal("6"),
                expected_waste_quantity=Decimal("4"),
                package_weight_g=None,
            )
        ]
    )

    assert summary.mass_evidence_coverage == "NONE"
    assert summary.expected_rescue_mass_kg is None
    assert summary.expected_waste_mass_kg is None
