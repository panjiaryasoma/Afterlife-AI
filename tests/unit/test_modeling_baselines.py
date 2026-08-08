"""Tests for leakage-safe deterministic baselines."""

from pathlib import Path

import pandas as pd
import pytest

from afterlife_ai.modeling.baselines import (
    attach_split_assignments,
    fit_action_prior,
    load_baseline_config,
    score_action_prior,
    score_rule_priority,
    select_modeling_split,
)
from afterlife_ai.synthetic.catalog import MODEL_SCORED_ACTIONS

CONFIG_PATH = Path("configs/baseline_v1.yaml")


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "scenario_group_id": "SG-001",
                "candidate_id": "C-001",
                "action_type": "INTERNAL_REPURPOSE",
                "simulated_rescue_outcome": 1,
            },
            {
                "scenario_group_id": "SG-001",
                "candidate_id": "C-002",
                "action_type": "DONATION",
                "simulated_rescue_outcome": 0,
            },
            {
                "scenario_group_id": "SG-002",
                "candidate_id": "C-003",
                "action_type": "DONATION",
                "simulated_rescue_outcome": 1,
            },
            {
                "scenario_group_id": "SG-003",
                "candidate_id": "C-004",
                "action_type": "INTERNAL_REPURPOSE",
                "simulated_rescue_outcome": 0,
            },
        ]
    )


def _assignments() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "scenario_group_id": "SG-001",
                "split": "train",
            },
            {
                "scenario_group_id": "SG-002",
                "split": "train",
            },
            {
                "scenario_group_id": "SG-003",
                "split": "validation",
            },
        ]
    )


def test_b0_priority_covers_all_model_scored_actions() -> None:
    config = load_baseline_config(CONFIG_PATH)

    expected = {
        action.value
        for action in MODEL_SCORED_ACTIONS
    }

    assert set(config.b0_rule_priority.action_priority) == expected


def test_split_assignment_merge_is_many_to_one() -> None:
    merged = attach_split_assignments(
        _frame(),
        _assignments(),
    )

    assert len(merged) == 4
    assert set(merged["split"]) == {
        "train",
        "validation",
    }


def test_test_split_cannot_be_selected_for_development() -> None:
    merged = attach_split_assignments(
        _frame(),
        _assignments(),
    )

    with pytest.raises(
        ValueError,
        match="train dan validation",
    ):
        select_modeling_split(merged, "test")  # type: ignore[arg-type]


def test_b0_fixed_priority_is_deterministic() -> None:
    config = load_baseline_config(CONFIG_PATH)
    frame = _frame()

    first = score_rule_priority(
        frame,
        config.b0_rule_priority,
    )
    second = score_rule_priority(
        frame,
        config.b0_rule_priority,
    )

    pd.testing.assert_frame_equal(first, second)

    repurpose = first.loc[
        first["action_type"] == "INTERNAL_REPURPOSE",
        "baseline_score",
    ].iloc[0]

    donation = first.loc[
        first["action_type"] == "DONATION",
        "baseline_score",
    ].iloc[0]

    assert repurpose > donation


def test_b1_action_prior_is_fit_from_train_only() -> None:
    config = load_baseline_config(CONFIG_PATH)

    merged = attach_split_assignments(
        _frame(),
        _assignments(),
    )
    train = select_modeling_split(merged, "train")

    model = fit_action_prior(
        train,
        config.b1_action_prior,
    )

    assert model.training_rows == 3
    assert model.global_prior == pytest.approx(2 / 3)

    assert model.action_priors["INTERNAL_REPURPOSE"] == pytest.approx(1.0)
    assert model.action_priors["DONATION"] == pytest.approx(0.5)


def test_b1_rejects_validation_rows_during_fit() -> None:
    config = load_baseline_config(CONFIG_PATH)

    merged = attach_split_assignments(
        _frame(),
        _assignments(),
    )

    with pytest.raises(
        ValueError,
        match="train split",
    ):
        fit_action_prior(
            merged,
            config.b1_action_prior,
        )


def test_b1_unseen_action_uses_global_train_prior() -> None:
    config = load_baseline_config(CONFIG_PATH)

    merged = attach_split_assignments(
        _frame(),
        _assignments(),
    )
    train = select_modeling_split(merged, "train")

    model = fit_action_prior(
        train,
        config.b1_action_prior,
    )

    validation = pd.DataFrame(
        [
            {
                "scenario_group_id": "SG-X",
                "candidate_id": "C-X",
                "action_type": "WHOLESALE",
                "simulated_rescue_outcome": 0,
            }
        ]
    )

    scored = score_action_prior(
        validation,
        model,
        config.b1_action_prior,
    )

    assert scored["baseline_score"].iloc[0] == pytest.approx(
        model.global_prior
    )
