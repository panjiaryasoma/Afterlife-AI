from decimal import Decimal

import pytest

from afterlife_ai.planner.value import (
    ExpectedValueInput,
    calculate_expected_value,
)


def test_cash_recovery_matches_integration_fixture_formula() -> None:
    value_input = ExpectedValueInput(
        rescue_probability=Decimal("0.86"),
        quantity=Decimal("1"),
        cash_recovery_per_unit=Decimal("3500"),
        future_branch_recovery_per_unit=Decimal("0"),
        avoided_purchase_cost_per_unit=Decimal("0"),
        direct_action_cost_per_unit=Decimal("1100"),
        logistics_cost_per_unit=Decimal("0"),
        handling_cost_per_unit=Decimal("0"),
        failure_penalty_per_unit=Decimal("0"),
    )

    result = calculate_expected_value(value_input)

    assert result.successful_net_value_per_unit == Decimal("2400")
    assert result.expected_cash_recovery == Decimal("3010")
    assert result.expected_future_branch_recovery == Decimal("0")
    assert result.expected_avoided_purchase_cost == Decimal("0")
    assert result.expected_success_value == Decimal("2064")
    assert result.expected_net_recovery == Decimal("2064")


def test_expected_value_scales_with_quantity() -> None:
    value_input = ExpectedValueInput(
        rescue_probability=Decimal("0.80"),
        quantity=Decimal("4"),
        cash_recovery_per_unit=Decimal("2000"),
        future_branch_recovery_per_unit=Decimal("0"),
        avoided_purchase_cost_per_unit=Decimal("0"),
        direct_action_cost_per_unit=Decimal("400"),
        logistics_cost_per_unit=Decimal("0"),
        handling_cost_per_unit=Decimal("0"),
        failure_penalty_per_unit=Decimal("0"),
    )

    result = calculate_expected_value(value_input)

    assert result.successful_net_value_per_unit == Decimal("1600")
    assert result.expected_net_recovery_per_unit == Decimal("1280")
    assert result.expected_net_recovery == Decimal("5120")


def test_recovery_channels_remain_separate() -> None:
    value_input = ExpectedValueInput(
        rescue_probability=Decimal("0.75"),
        quantity=Decimal("2"),
        cash_recovery_per_unit=Decimal("1000"),
        future_branch_recovery_per_unit=Decimal("500"),
        avoided_purchase_cost_per_unit=Decimal("300"),
        direct_action_cost_per_unit=Decimal("200"),
        logistics_cost_per_unit=Decimal("100"),
        handling_cost_per_unit=Decimal("0"),
        failure_penalty_per_unit=Decimal("0"),
    )

    result = calculate_expected_value(value_input)

    assert result.expected_cash_recovery == Decimal("1500")
    assert result.expected_future_branch_recovery == Decimal("750")
    assert result.expected_avoided_purchase_cost == Decimal("450")
    assert result.expected_net_recovery == Decimal("2250")


def test_failure_penalty_reduces_expected_net_recovery() -> None:
    value_input = ExpectedValueInput(
        rescue_probability=Decimal("0.50"),
        quantity=Decimal("2"),
        cash_recovery_per_unit=Decimal("2000"),
        future_branch_recovery_per_unit=Decimal("0"),
        avoided_purchase_cost_per_unit=Decimal("0"),
        direct_action_cost_per_unit=Decimal("0"),
        logistics_cost_per_unit=Decimal("0"),
        handling_cost_per_unit=Decimal("0"),
        failure_penalty_per_unit=Decimal("400"),
    )

    result = calculate_expected_value(value_input)

    assert result.expected_success_value == Decimal("2000")
    assert result.expected_failure_penalty == Decimal("400")
    assert result.expected_net_recovery == Decimal("1600")


def test_expected_physical_rescue_and_waste_are_complements() -> None:
    value_input = ExpectedValueInput(
        rescue_probability=Decimal("0.75"),
        quantity=Decimal("8"),
        cash_recovery_per_unit=Decimal("1500"),
        future_branch_recovery_per_unit=Decimal("0"),
        avoided_purchase_cost_per_unit=Decimal("0"),
        direct_action_cost_per_unit=Decimal("0"),
        logistics_cost_per_unit=Decimal("0"),
        handling_cost_per_unit=Decimal("0"),
        failure_penalty_per_unit=Decimal("0"),
    )

    result = calculate_expected_value(value_input)

    assert result.expected_physical_rescue_quantity == Decimal("6.00")
    assert result.expected_waste_quantity == Decimal("2.00")
    assert (
        result.expected_physical_rescue_quantity
        + result.expected_waste_quantity
        == Decimal("8")
    )


def test_probability_must_be_between_zero_and_one() -> None:
    with pytest.raises(ValueError):
        ExpectedValueInput(
            rescue_probability=Decimal("1.01"),
            quantity=Decimal("1"),
            cash_recovery_per_unit=Decimal("1000"),
            future_branch_recovery_per_unit=Decimal("0"),
            avoided_purchase_cost_per_unit=Decimal("0"),
            direct_action_cost_per_unit=Decimal("0"),
            logistics_cost_per_unit=Decimal("0"),
            handling_cost_per_unit=Decimal("0"),
            failure_penalty_per_unit=Decimal("0"),
        )


def test_quantity_must_be_positive() -> None:
    with pytest.raises(ValueError):
        ExpectedValueInput(
            rescue_probability=Decimal("0.5"),
            quantity=Decimal("0"),
            cash_recovery_per_unit=Decimal("1000"),
            future_branch_recovery_per_unit=Decimal("0"),
            avoided_purchase_cost_per_unit=Decimal("0"),
            direct_action_cost_per_unit=Decimal("0"),
            logistics_cost_per_unit=Decimal("0"),
            handling_cost_per_unit=Decimal("0"),
            failure_penalty_per_unit=Decimal("0"),
        )
