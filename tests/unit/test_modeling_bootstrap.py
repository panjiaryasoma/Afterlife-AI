"""Tests for paired scenario-group bootstrap."""

import pandas as pd
import pytest

from afterlife_ai.modeling.bootstrap import (
    paired_group_bootstrap,
)


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "scenario_group_id": "G1",
                "candidate_id": "A",
                "simulated_rescue_outcome": 1,
                "lr_score": 0.9,
                "hgb_score": 0.8,
            },
            {
                "scenario_group_id": "G1",
                "candidate_id": "B",
                "simulated_rescue_outcome": 0,
                "lr_score": 0.2,
                "hgb_score": 0.3,
            },
            {
                "scenario_group_id": "G2",
                "candidate_id": "C",
                "simulated_rescue_outcome": 0,
                "lr_score": 0.6,
                "hgb_score": 0.7,
            },
            {
                "scenario_group_id": "G2",
                "candidate_id": "D",
                "simulated_rescue_outcome": 1,
                "lr_score": 0.7,
                "hgb_score": 0.4,
            },
            {
                "scenario_group_id": "G3",
                "candidate_id": "E",
                "simulated_rescue_outcome": 1,
                "lr_score": 0.8,
                "hgb_score": 0.9,
            },
            {
                "scenario_group_id": "G3",
                "candidate_id": "F",
                "simulated_rescue_outcome": 0,
                "lr_score": 0.1,
                "hgb_score": 0.2,
            },
        ]
    )


def test_paired_bootstrap_is_deterministic() -> None:
    frame = _frame()

    first = paired_group_bootstrap(
        frame,
        iterations=100,
        seed=42,
    )
    second = paired_group_bootstrap(
        frame,
        iterations=100,
        seed=42,
    )

    assert first == second


def test_lr_has_higher_top1_on_fixture() -> None:
    report = paired_group_bootstrap(
        _frame(),
        iterations=100,
        seed=42,
    )

    metrics = report["metrics"]

    assert (
        metrics["top1_success_rate"]["lr"]
        > metrics["top1_success_rate"]["hgb"]
    )


def test_duplicate_candidate_is_rejected() -> None:
    frame = _frame()
    frame.loc[1, "candidate_id"] = "A"

    with pytest.raises(
        ValueError,
        match="candidate_id harus unik",
    ):
        paired_group_bootstrap(
            frame,
            iterations=10,
            seed=42,
        )
