"""Validation metrics for candidate ranking scores."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
)


@dataclass(frozen=True)
class RankingMetrics:
    """Predictive and grouped-ranking validation metrics."""

    roc_auc: float
    pr_auc: float
    top1_success_rate: float
    mrr: float
    ndcg_at_3: float
    scenario_groups: int
    candidate_rows: int


def _group_reciprocal_rank(group: pd.DataFrame) -> float:
    ordered = group.sort_values(
        ["baseline_score", "candidate_id"],
        ascending=[False, True],
        kind="stable",
    )

    positives = np.flatnonzero(
        ordered["simulated_rescue_outcome"].to_numpy() == 1
    )

    if len(positives) == 0:
        return 0.0

    return 1.0 / float(positives[0] + 1)


def _group_ndcg_at_k(
    group: pd.DataFrame,
    *,
    k: int,
) -> float:
    ordered = group.sort_values(
        ["baseline_score", "candidate_id"],
        ascending=[False, True],
        kind="stable",
    )

    relevance = (
        ordered["simulated_rescue_outcome"]
        .to_numpy(dtype=float)[:k]
    )

    discounts = 1.0 / np.log2(
        np.arange(2, len(relevance) + 2)
    )

    dcg = float(np.sum(relevance * discounts))

    ideal = np.sort(
        group["simulated_rescue_outcome"].to_numpy(dtype=float)
    )[::-1][:k]

    ideal_discounts = 1.0 / np.log2(
        np.arange(2, len(ideal) + 2)
    )

    idcg = float(np.sum(ideal * ideal_discounts))

    if idcg == 0.0:
        return 0.0

    return dcg / idcg


def evaluate_ranking_scores(
    predictions: pd.DataFrame,
) -> RankingMetrics:
    """Evaluate one baseline/model prediction table."""

    required = {
        "scenario_group_id",
        "candidate_id",
        "simulated_rescue_outcome",
        "baseline_score",
    }

    missing = required - set(predictions.columns)

    if missing:
        raise ValueError(
            f"Prediction table kehilangan columns: {sorted(missing)}"
        )

    target = predictions["simulated_rescue_outcome"]
    score = predictions["baseline_score"]

    target_values = set(int(value) for value in target.unique())

    if target_values != {0, 1}:
        raise ValueError(
            "Validation target harus mengandung kedua kelas 0 dan 1."
        )

    grouped = predictions.groupby(
        "scenario_group_id",
        sort=True,
    )

    reciprocal_ranks: list[float] = []
    ndcg_values: list[float] = []
    top1_results: list[float] = []

    for _, group in grouped:
        ordered = group.sort_values(
            ["baseline_score", "candidate_id"],
            ascending=[False, True],
            kind="stable",
        )

        top1_results.append(
            float(
                ordered[
                    "simulated_rescue_outcome"
                ].iloc[0]
            )
        )

        reciprocal_ranks.append(
            _group_reciprocal_rank(group)
        )

        ndcg_values.append(
            _group_ndcg_at_k(group, k=3)
        )

    return RankingMetrics(
        roc_auc=float(
            roc_auc_score(target, score)
        ),
        pr_auc=float(
            average_precision_score(target, score)
        ),
        top1_success_rate=float(np.mean(top1_results)),
        mrr=float(np.mean(reciprocal_ranks)),
        ndcg_at_3=float(np.mean(ndcg_values)),
        scenario_groups=int(
            predictions["scenario_group_id"].nunique()
        ),
        candidate_rows=len(predictions),
    )


__all__ = [
    "RankingMetrics",
    "evaluate_ranking_scores",
]
