"""Regression tests for candidate-level cost semantics."""

from decimal import Decimal

from afterlife_ai.planner.value import (
    ExpectedValueInput,
    calculate_expected_value,
)


def test_candidate_total_cost_can_be_amortized_without_multiplication() -> None:
    quantity = Decimal("52")
    total_direct = Decimal("287.48")
    total_logistics = Decimal("41138.08")
    total_handling = Decimal("11085.35")

    result = calculate_expected_value(
        ExpectedValueInput(
            rescue_probability=Decimal("1"),
            quantity=quantity,
            cash_recovery_per_unit=Decimal("100000"),
            future_branch_recovery_per_unit=Decimal("0"),
            avoided_purchase_cost_per_unit=Decimal("0"),
            direct_action_cost_per_unit=(
                total_direct / quantity
            ),
            logistics_cost_per_unit=(
                total_logistics / quantity
            ),
            handling_cost_per_unit=(
                total_handling / quantity
            ),
            failure_penalty_per_unit=Decimal("0"),
        )
    )

    expected_cost = (
        total_direct
        + total_logistics
        + total_handling
    )

    assert (
        result.expected_success_cost.quantize(
            Decimal("0.01")
        )
        == expected_cost.quantize(
            Decimal("0.01")
        )
    )
