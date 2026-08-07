"""Expected-value calculation for rescue action candidates."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

ZERO = Decimal("0")
ONE = Decimal("1")


class ExpectedValueInput(BaseModel):
    """Inputs required for deterministic expected-value calculation."""

    model_config = ConfigDict(extra="forbid")

    rescue_probability: Decimal = Field(
        ge=ZERO,
        le=ONE,
    )
    quantity: Decimal = Field(gt=ZERO)

    cash_recovery_per_unit: Decimal = Field(ge=ZERO)
    future_branch_recovery_per_unit: Decimal = Field(ge=ZERO)
    avoided_purchase_cost_per_unit: Decimal = Field(ge=ZERO)

    direct_action_cost_per_unit: Decimal = Field(ge=ZERO)
    logistics_cost_per_unit: Decimal = Field(ge=ZERO)
    handling_cost_per_unit: Decimal = Field(ge=ZERO)

    failure_penalty_per_unit: Decimal = Field(ge=ZERO)


class ExpectedValueResult(BaseModel):
    """Deterministic expected-value components for one candidate quantity."""

    model_config = ConfigDict(extra="forbid")

    rescue_probability: Decimal
    quantity: Decimal

    gross_recovery_per_unit: Decimal
    successful_cost_per_unit: Decimal
    successful_net_value_per_unit: Decimal

    expected_cash_recovery: Decimal
    expected_future_branch_recovery: Decimal
    expected_avoided_purchase_cost: Decimal

    expected_success_cost: Decimal
    expected_success_value: Decimal
    expected_failure_penalty: Decimal

    expected_physical_rescue_quantity: Decimal
    expected_waste_quantity: Decimal

    expected_net_recovery_per_unit: Decimal
    expected_net_recovery: Decimal


def calculate_expected_value(
    value_input: ExpectedValueInput,
) -> ExpectedValueResult:
    """Calculate expected rescue value without mixing recovery channels."""

    probability = value_input.rescue_probability
    failure_probability = ONE - probability
    quantity = value_input.quantity

    gross_recovery_per_unit = (
        value_input.cash_recovery_per_unit
        + value_input.future_branch_recovery_per_unit
        + value_input.avoided_purchase_cost_per_unit
    )

    successful_cost_per_unit = (
        value_input.direct_action_cost_per_unit
        + value_input.logistics_cost_per_unit
        + value_input.handling_cost_per_unit
    )

    successful_net_value_per_unit = (
        gross_recovery_per_unit
        - successful_cost_per_unit
    )

    expected_cash_recovery = (
        probability
        * value_input.cash_recovery_per_unit
        * quantity
    )

    expected_future_branch_recovery = (
        probability
        * value_input.future_branch_recovery_per_unit
        * quantity
    )

    expected_avoided_purchase_cost = (
        probability
        * value_input.avoided_purchase_cost_per_unit
        * quantity
    )

    expected_success_cost = (
        probability
        * successful_cost_per_unit
        * quantity
    )

    expected_success_value = (
        probability
        * successful_net_value_per_unit
        * quantity
    )

    expected_failure_penalty = (
        failure_probability
        * value_input.failure_penalty_per_unit
        * quantity
    )

    expected_net_recovery = (
        expected_success_value
        - expected_failure_penalty
    )

    expected_net_recovery_per_unit = (
        expected_net_recovery / quantity
    )

    expected_physical_rescue_quantity = (
        probability * quantity
    )

    expected_waste_quantity = (
        failure_probability * quantity
    )

    return ExpectedValueResult(
        rescue_probability=probability,
        quantity=quantity,
        gross_recovery_per_unit=gross_recovery_per_unit,
        successful_cost_per_unit=successful_cost_per_unit,
        successful_net_value_per_unit=successful_net_value_per_unit,
        expected_cash_recovery=expected_cash_recovery,
        expected_future_branch_recovery=(
            expected_future_branch_recovery
        ),
        expected_avoided_purchase_cost=(
            expected_avoided_purchase_cost
        ),
        expected_success_cost=expected_success_cost,
        expected_success_value=expected_success_value,
        expected_failure_penalty=expected_failure_penalty,
        expected_physical_rescue_quantity=(
            expected_physical_rescue_quantity
        ),
        expected_waste_quantity=expected_waste_quantity,
        expected_net_recovery_per_unit=(
            expected_net_recovery_per_unit
        ),
        expected_net_recovery=expected_net_recovery,
    )


__all__ = [
    "ExpectedValueInput",
    "ExpectedValueResult",
    "calculate_expected_value",
]
