"""Contracts for sustainability impact and outcome reconciliation."""

from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

ZERO = Decimal("0")
QUANTITY_TOLERANCE = Decimal("1E-18")


class OutcomeObservation(BaseModel):
    """Operator-confirmed outcome within a reconciliation scope."""

    model_config = ConfigDict(extra="forbid")

    reconciled_quantity: Decimal = Field(ge=ZERO)
    actual_rescued_quantity: Decimal = Field(ge=ZERO)
    actual_waste_quantity: Decimal = Field(ge=ZERO)

    @model_validator(mode="after")
    def validate_confirmed_quantity(self) -> Self:
        confirmed_quantity = (
            self.actual_rescued_quantity
            + self.actual_waste_quantity
        )

        if (
            confirmed_quantity
            - self.reconciled_quantity
            > QUANTITY_TOLERANCE
        ):
            raise ValueError(
                "confirmed outcome quantity cannot exceed "
                "reconciled quantity."
            )

        return self


class SustainabilitySummary(BaseModel):
    """Expected environmental impact derived from a single weight scope."""

    model_config = ConfigDict(extra="forbid")

    reconciled_quantity: Decimal = Field(ge=ZERO)
    expected_rescue_quantity: Decimal = Field(ge=ZERO)
    expected_waste_quantity: Decimal = Field(ge=ZERO)

    expected_rescue_ratio: Decimal | None = Field(
        default=None,
        ge=ZERO,
        le=Decimal("1"),
    )
    expected_rescue_mass_kg: Decimal | None = Field(
        default=None,
        ge=ZERO,
    )
    expected_waste_mass_kg: Decimal | None = Field(
        default=None,
        ge=ZERO,
    )


class ImpactQuantitySlice(BaseModel):
    """One source-lot quantity slice used for batch impact aggregation."""

    model_config = ConfigDict(extra="forbid")

    source_lot_id: str
    reconciled_quantity: Decimal = Field(ge=ZERO)
    expected_rescue_quantity: Decimal = Field(ge=ZERO)
    expected_waste_quantity: Decimal = Field(ge=ZERO)
    package_weight_g: Decimal | None = Field(default=None, ge=ZERO)

    @model_validator(mode="after")
    def validate_quantity_conservation(self) -> Self:
        expected_total = (
            self.expected_rescue_quantity
            + self.expected_waste_quantity
        )

        if (
            abs(expected_total - self.reconciled_quantity)
            > QUANTITY_TOLERANCE
        ):
            raise ValueError(
                "expected rescue quantity + expected waste quantity "
                "must equal reconciled quantity."
            )

        return self


class BatchSustainabilitySummary(BaseModel):
    """Expected batch impact with explicit package-weight evidence coverage."""

    model_config = ConfigDict(extra="forbid")

    reconciled_quantity: Decimal = Field(ge=ZERO)
    expected_rescue_quantity: Decimal = Field(ge=ZERO)
    expected_waste_quantity: Decimal = Field(ge=ZERO)
    expected_rescue_ratio: Decimal | None = Field(
        default=None,
        ge=ZERO,
        le=Decimal("1"),
    )

    mass_evidence_coverage: Literal[
        "COMPLETE",
        "PARTIAL",
        "NONE",
    ]
    expected_rescue_mass_kg: Decimal | None = Field(
        default=None,
        ge=ZERO,
    )
    expected_waste_mass_kg: Decimal | None = Field(
        default=None,
        ge=ZERO,
    )

    @model_validator(mode="after")
    def validate_mass_claim_boundary(self) -> Self:
        if self.mass_evidence_coverage != "COMPLETE" and (
            self.expected_rescue_mass_kg is not None
            or self.expected_waste_mass_kg is not None
        ):
            raise ValueError(
                "batch mass metrics require COMPLETE mass evidence coverage."
            )

        return self


class OutcomeReconciliation(BaseModel):
    """Comparison between expected and operator-confirmed outcomes."""

    model_config = ConfigDict(extra="forbid")

    reconciled_quantity: Decimal = Field(ge=ZERO)
    actual_rescued_quantity: Decimal = Field(ge=ZERO)
    actual_waste_quantity: Decimal = Field(ge=ZERO)
    unresolved_quantity: Decimal = Field(ge=ZERO)

    realized_diversion_ratio: Decimal | None = Field(
        default=None,
        ge=ZERO,
        le=Decimal("1"),
    )

    rescue_quantity_delta: Decimal
    waste_quantity_delta: Decimal


__all__ = [
    "BatchSustainabilitySummary",
    "ImpactQuantitySlice",
    "OutcomeObservation",
    "OutcomeReconciliation",
    "SustainabilitySummary",
]
