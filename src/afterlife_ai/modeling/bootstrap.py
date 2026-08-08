"""Paired bootstrap utilities for grouped model comparison."""

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)

_REQUIRED_COLUMNS = {
    "scenario_group_id",
    "candidate_id",
    "simulated_rescue_outcome",
    "lr_score",
    "hgb_score",
}


def _group_ranking_values(
    frame: pd.DataFrame,
    *,
    score_column: str,
    group_order: list[str],
) -> dict[str, np.ndarray]:
    """Compute per-group Top-1, MRR, and NDCG@3."""

    top1: list[float] = []
    mrr: list[float] = []
    ndcg: list[float] = []

    for group_id in group_order:
        group = frame.loc[
            frame["scenario_group_id"] == group_id
        ]

        ordered = group.sort_values(
            [score_column, "candidate_id"],
            ascending=[False, True],
            kind="stable",
        )

        relevance = (
            ordered["simulated_rescue_outcome"]
            .to_numpy(dtype=float)
        )

        top1.append(float(relevance[0]))

        positive_positions = np.flatnonzero(
            relevance == 1.0
        )

        if len(positive_positions) == 0:
            mrr.append(0.0)
        else:
            mrr.append(
                1.0 / float(positive_positions[0] + 1)
            )

        observed = relevance[:3]

        discounts = 1.0 / np.log2(
            np.arange(2, len(observed) + 2)
        )

        dcg = float(
            np.sum(observed * discounts)
        )

        ideal = np.sort(relevance)[::-1][:3]

        ideal_discounts = 1.0 / np.log2(
            np.arange(2, len(ideal) + 2)
        )

        idcg = float(
            np.sum(ideal * ideal_discounts)
        )

        ndcg.append(
            0.0 if idcg == 0.0 else dcg / idcg
        )

    return {
        "top1_success_rate": np.asarray(
            top1,
            dtype=float,
        ),
        "mrr": np.asarray(
            mrr,
            dtype=float,
        ),
        "ndcg_at_3": np.asarray(
            ndcg,
            dtype=float,
        ),
    }


def paired_group_bootstrap(
    frame: pd.DataFrame,
    *,
    iterations: int = 5000,
    seed: int = 42,
) -> dict[str, Any]:
    """Compare LR and HGB using paired scenario-group bootstrap."""

    missing = _REQUIRED_COLUMNS - set(
        frame.columns
    )

    if missing:
        raise ValueError(
            "Comparison frame kehilangan columns: "
            f"{sorted(missing)}"
        )

    if iterations <= 0:
        raise ValueError(
            "Bootstrap iterations harus > 0."
        )

    if frame["candidate_id"].duplicated().any():
        raise ValueError(
            "candidate_id harus unik."
        )

    target = frame[
        "simulated_rescue_outcome"
    ].to_numpy(dtype=int)

    if set(target.tolist()) != {0, 1}:
        raise ValueError(
            "Validation target harus memiliki kelas 0 dan 1."
        )

    lr_score = frame["lr_score"].to_numpy(
        dtype=float
    )
    hgb_score = frame["hgb_score"].to_numpy(
        dtype=float
    )

    group_order = sorted(
        frame["scenario_group_id"]
        .astype(str)
        .unique()
        .tolist()
    )

    group_to_index = {
        group_id: index
        for index, group_id in enumerate(
            group_order
        )
    }

    group_codes = (
        frame["scenario_group_id"]
        .astype(str)
        .map(group_to_index)
        .to_numpy(dtype=int)
    )

    n_groups = len(group_order)

    lr_group = _group_ranking_values(
        frame,
        score_column="lr_score",
        group_order=group_order,
    )

    hgb_group = _group_ranking_values(
        frame,
        score_column="hgb_score",
        group_order=group_order,
    )

    point_lr = {
        "pr_auc": float(
            average_precision_score(
                target,
                lr_score,
            )
        ),
        "brier_score": float(
            brier_score_loss(
                target,
                lr_score,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                target,
                lr_score,
            )
        ),
        "top1_success_rate": float(
            lr_group[
                "top1_success_rate"
            ].mean()
        ),
        "mrr": float(
            lr_group["mrr"].mean()
        ),
        "ndcg_at_3": float(
            lr_group["ndcg_at_3"].mean()
        ),
    }

    point_hgb = {
        "pr_auc": float(
            average_precision_score(
                target,
                hgb_score,
            )
        ),
        "brier_score": float(
            brier_score_loss(
                target,
                hgb_score,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                target,
                hgb_score,
            )
        ),
        "top1_success_rate": float(
            hgb_group[
                "top1_success_rate"
            ].mean()
        ),
        "mrr": float(
            hgb_group["mrr"].mean()
        ),
        "ndcg_at_3": float(
            hgb_group["ndcg_at_3"].mean()
        ),
    }

    metric_names = [
        "pr_auc",
        "brier_score",
        "roc_auc",
        "top1_success_rate",
        "mrr",
        "ndcg_at_3",
    ]

    bootstrap_deltas = {
        name: np.empty(
            iterations,
            dtype=float,
        )
        for name in metric_names
    }

    rng = np.random.default_rng(seed)

    for iteration in range(iterations):
        sampled_groups = rng.integers(
            0,
            n_groups,
            size=n_groups,
        )

        group_counts = np.bincount(
            sampled_groups,
            minlength=n_groups,
        )

        row_weights = group_counts[
            group_codes
        ].astype(float)

        active = row_weights > 0.0

        active_target = target[active]

        if len(set(active_target.tolist())) != 2:
            raise RuntimeError(
                "Bootstrap replicate kehilangan salah satu kelas."
            )

        weights = row_weights[active]

        lr_pr = float(
            average_precision_score(
                active_target,
                lr_score[active],
                sample_weight=weights,
            )
        )

        hgb_pr = float(
            average_precision_score(
                active_target,
                hgb_score[active],
                sample_weight=weights,
            )
        )

        lr_brier = float(
            brier_score_loss(
                active_target,
                lr_score[active],
                sample_weight=weights,
            )
        )

        hgb_brier = float(
            brier_score_loss(
                active_target,
                hgb_score[active],
                sample_weight=weights,
            )
        )

        lr_roc = float(
            roc_auc_score(
                active_target,
                lr_score[active],
                sample_weight=weights,
            )
        )

        hgb_roc = float(
            roc_auc_score(
                active_target,
                hgb_score[active],
                sample_weight=weights,
            )
        )

        bootstrap_deltas["pr_auc"][
            iteration
        ] = lr_pr - hgb_pr

        bootstrap_deltas["brier_score"][
            iteration
        ] = lr_brier - hgb_brier

        bootstrap_deltas["roc_auc"][
            iteration
        ] = lr_roc - hgb_roc

        for metric in (
            "top1_success_rate",
            "mrr",
            "ndcg_at_3",
        ):
            lr_value = float(
                lr_group[metric][
                    sampled_groups
                ].mean()
            )

            hgb_value = float(
                hgb_group[metric][
                    sampled_groups
                ].mean()
            )

            bootstrap_deltas[metric][
                iteration
            ] = lr_value - hgb_value

    metrics: dict[str, Any] = {}

    for metric in metric_names:
        delta_samples = bootstrap_deltas[
            metric
        ]

        observed_delta = (
            point_lr[metric]
            - point_hgb[metric]
        )

        denominator = abs(
            point_hgb[metric]
        )

        relative_delta = (
            observed_delta / denominator
            if denominator > 0.0
            else 0.0
        )

        ci_lower, ci_upper = np.quantile(
            delta_samples,
            [0.025, 0.975],
        )

        lower_is_better = (
            metric == "brier_score"
        )

        if lower_is_better:
            lr_win_fraction = float(
                np.mean(delta_samples < 0.0)
            )
        else:
            lr_win_fraction = float(
                np.mean(delta_samples > 0.0)
            )

        metrics[metric] = {
            "lr": point_lr[metric],
            "hgb": point_hgb[metric],
            "delta_lr_minus_hgb": (
                observed_delta
            ),
            "relative_delta_vs_hgb": (
                relative_delta
            ),
            "bootstrap_delta_mean": float(
                delta_samples.mean()
            ),
            "bootstrap_delta_std": float(
                delta_samples.std(ddof=1)
            ),
            "ci_95_lower": float(
                ci_lower
            ),
            "ci_95_upper": float(
                ci_upper
            ),
            "lr_win_fraction": (
                lr_win_fraction
            ),
            "better_direction": (
                "lower"
                if lower_is_better
                else "higher"
            ),
        }

    return {
        "scenario_groups": n_groups,
        "candidate_rows": len(frame),
        "iterations": iterations,
        "bootstrap_seed": seed,
        "delta_definition": (
            "LR minus HGB; negative favors LR only for Brier."
        ),
        "metrics": metrics,
    }


__all__ = [
    "paired_group_bootstrap",
]
