"""Tests for grouped ranking metrics."""

import pandas as pd
import pytest

from afterlife_ai.modeling.metrics import (
    evaluate_ranking_scores,
)


def test_perfect_ranking_has_perfect_group_metrics() -> None:
    predictions = pd.DataFrame(
        [
            {
                "scenario_group_id": "G1",
                "candidate_id": "A",
                "simulated_rescue_outcome": 1,
                "baseline_score": 0.9,
            },
            {
                "scenario_group_id": "G1",
                "candidate_id": "B",
                "simulated_rescue_outcome": 0,
                "baseline_score": 0.1,
            },
            {
                "scenario_group_id": "G2",
                "candidate_id": "C",
                "simulated_rescue_outcome": 1,
                "baseline_score": 0.8,
            },
            {
                "scenario_group_id": "G2",
                "candidate_id": "D",
                "simulated_rescue_outcome": 0,
                "baseline_score": 0.2,
            },
        ]
    )

    metrics = evaluate_ranking_scores(predictions)

    assert metrics.roc_auc == pytest.approx(1.0)
    assert metrics.pr_auc == pytest.approx(1.0)
    assert metrics.top1_success_rate == pytest.approx(1.0)
    assert metrics.mrr == pytest.approx(1.0)
    assert metrics.ndcg_at_3 == pytest.approx(1.0)


def test_groups_without_positive_receive_zero_group_credit() -> None:
    predictions = pd.DataFrame(
        [
            {
                "scenario_group_id": "G1",
                "candidate_id": "A",
                "simulated_rescue_outcome": 1,
                "baseline_score": 0.9,
            },
            {
                "scenario_group_id": "G1",
                "candidate_id": "B",
                "simulated_rescue_outcome": 0,
                "baseline_score": 0.1,
            },
            {
                "scenario_group_id": "G2",
                "candidate_id": "C",
                "simulated_rescue_outcome": 0,
                "baseline_score": 0.8,
            },
            {
                "scenario_group_id": "G2",
                "candidate_id": "D",
                "simulated_rescue_outcome": 0,
                "baseline_score": 0.2,
            },
        ]
    )

    metrics = evaluate_ranking_scores(predictions)

    assert metrics.top1_success_rate == pytest.approx(0.5)
    assert metrics.mrr == pytest.approx(0.5)
    assert metrics.ndcg_at_3 == pytest.approx(0.5)
