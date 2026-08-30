"""HTTP routes for NextStep sustainability outcome reconciliation."""

from decimal import Decimal
from typing import Self

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field, model_validator

from afterlife_ai.contracts.impact import (
    OutcomeObservation,
    OutcomeReconciliation,
)
from afterlife_ai.impact.reconciliation import reconcile_outcome

ZERO = Decimal("0")
QUANTITY_TOLERANCE = Decimal("1E-18")

router = APIRouter(
    prefix="/api",
    tags=["impact"],
)


class OutcomeReconciliationRequest(BaseModel):
    """Expected plan quantities plus one operator-confirmed observation."""

    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=1)
    observation: OutcomeObservation
    expected_rescue_quantity: Decimal = Field(ge=ZERO)
    expected_waste_quantity: Decimal = Field(ge=ZERO)

    @model_validator(mode="after")
    def validate_expected_quantity_scope(self) -> Self:
        expected_total = (
            self.expected_rescue_quantity
            + self.expected_waste_quantity
        )

        if (
            abs(
                expected_total
                - self.observation.reconciled_quantity
            )
            > QUANTITY_TOLERANCE
        ):
            raise ValueError(
                "expected rescue quantity + expected waste quantity "
                "must equal reconciled quantity."
            )

        return self


class OutcomeReconciliationResponse(BaseModel):
    """Traceable stateless reconciliation result for one report request."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    reconciliation: OutcomeReconciliation


@router.post(
    "/outcomes/reconcile",
    response_model=OutcomeReconciliationResponse,
)
def reconcile_report_outcome(
    payload: OutcomeReconciliationRequest,
) -> OutcomeReconciliationResponse:
    """Compute realized impact without persisting or mutating the rescue plan."""

    result = reconcile_outcome(
        observation=payload.observation,
        expected_rescue_quantity=(
            payload.expected_rescue_quantity
        ),
        expected_waste_quantity=(
            payload.expected_waste_quantity
        ),
    )

    return OutcomeReconciliationResponse(
        request_id=payload.request_id,
        reconciliation=result,
    )


__all__ = [
    "OutcomeReconciliationRequest",
    "OutcomeReconciliationResponse",
    "router",
]
