"""Diagnose why LR and HGB differ on validation ranking."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)

from afterlife_ai.modeling.baselines import (
    attach_split_assignments,
    select_modeling_split,
)
from afterlife_ai.modeling.hist_gradient import (
    fit_hist_gradient_boosting,
    load_hist_gradient_config,
    predict_hist_gradient_probabilities,
)
from afterlife_ai.modeling.training import (
    fit_logistic_regression,
    load_modeling_config,
    predict_logistic_probabilities,
)
from afterlife_ai.synthetic.schema_contract import (
    load_model_feature_contract,
)

MODELING_CONFIG = Path("configs/modeling_v1.yaml")
SCHEMA_PATH = Path("docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml")
CANDIDATE_PATH = Path(
    "data/generated/synthetic_candidates_v2.csv"
)
SPLIT_PATH = Path(
    "reports/evidence/synthetic_dataset/SPLIT_GROUPS_v2.csv"
)

OUTPUT_PATH = Path(
    "reports/evidence/modeling/"
    "LR_VS_HGB_DIAGNOSTIC_v1.json"
)


def binary_metrics(
    target: pd.Series,
    score: pd.Series,
) -> dict[str, float]:
    return {
        "roc_auc": float(
            roc_auc_score(target, score)
        ),
        "pr_auc": float(
            average_precision_score(target, score)
        ),
        "brier": float(
            brier_score_loss(target, score)
        ),
    }


def top1_success(frame: pd.DataFrame) -> float:
    ordered = frame.sort_values(
        [
            "scenario_group_id",
            "score",
            "candidate_id",
        ],
        ascending=[True, False, True],
        kind="stable",
    )

    top = ordered.groupby(
        "scenario_group_id",
        sort=True,
    ).head(1)

    return float(
        top["simulated_rescue_outcome"].mean()
    )


def group_score_summary(
    frame: pd.DataFrame,
) -> dict[str, float]:
    grouped = frame.groupby(
        "scenario_group_id",
        sort=True,
    )["score"]

    score_range = grouped.max() - grouped.min()
    score_std = grouped.std(ddof=0)

    ordered = frame.sort_values(
        [
            "scenario_group_id",
            "score",
            "candidate_id",
        ],
        ascending=[True, False, True],
        kind="stable",
    )

    margins: list[float] = []

    for _, group in ordered.groupby(
        "scenario_group_id",
        sort=True,
    ):
        scores = group["score"].to_numpy()

        if len(scores) >= 2:
            margins.append(
                float(scores[0] - scores[1])
            )

    return {
        "mean_group_score_range": float(
            score_range.mean()
        ),
        "median_group_score_range": float(
            score_range.median()
        ),
        "mean_group_score_std": float(
            score_std.mean()
        ),
        "mean_top1_margin": float(
            np.mean(margins)
        ),
        "median_top1_margin": float(
            np.median(margins)
        ),
    }


def pairwise_within_group_accuracy(
    frame: pd.DataFrame,
) -> float:
    correct = 0.0
    total = 0

    for _, group in frame.groupby(
        "scenario_group_id",
        sort=True,
    ):
        positive_scores = group.loc[
            group["simulated_rescue_outcome"] == 1,
            "score",
        ].to_numpy()

        negative_scores = group.loc[
            group["simulated_rescue_outcome"] == 0,
            "score",
        ].to_numpy()

        for positive in positive_scores:
            for negative in negative_scores:
                total += 1

                if positive > negative:
                    correct += 1.0
                elif positive == negative:
                    correct += 0.5

    if total == 0:
        return 0.0

    return correct / total


def calibration_bins(
    frame: pd.DataFrame,
) -> list[dict[str, float | int | str]]:
    working = frame.copy()

    working["bin"] = pd.cut(
        working["score"],
        bins=np.linspace(0.0, 1.0, 11),
        include_lowest=True,
    )

    rows: list[dict[str, float | int | str]] = []

    for interval, group in working.groupby(
        "bin",
        observed=True,
    ):
        rows.append(
            {
                "bin": str(interval),
                "rows": int(len(group)),
                "mean_score": float(
                    group["score"].mean()
                ),
                "observed_rate": float(
                    group[
                        "simulated_rescue_outcome"
                    ].mean()
                ),
                "absolute_gap": float(
                    abs(
                        group["score"].mean()
                        - group[
                            "simulated_rescue_outcome"
                        ].mean()
                    )
                ),
            }
        )

    return rows


def expected_calibration_error(
    bins: list[dict[str, float | int | str]],
) -> float:
    total = sum(
        int(row["rows"])
        for row in bins
    )

    if total == 0:
        return 0.0

    return sum(
        (
            int(row["rows"]) / total
        )
        * float(row["absolute_gap"])
        for row in bins
    )


def main() -> None:
    modeling_config = load_modeling_config(
        MODELING_CONFIG
    )
    hgb_config = load_hist_gradient_config(
        MODELING_CONFIG
    )
    contract = load_model_feature_contract(
        SCHEMA_PATH
    )

    candidate = pd.read_csv(CANDIDATE_PATH)
    assignments = pd.read_csv(SPLIT_PATH)

    modeling = attach_split_assignments(
        candidate,
        assignments,
    )

    train = select_modeling_split(
        modeling,
        "train",
    )
    validation = select_modeling_split(
        modeling,
        "validation",
    )

    lr_model = fit_logistic_regression(
        train,
        contract=contract,
        config=modeling_config.logistic_regression,
    )

    hgb_model = fit_hist_gradient_boosting(
        train,
        contract=contract,
        config=hgb_config,
    )

    results: dict[str, object] = {
        "report_version": "1.0.0",
        "test_accessed": False,
        "metric_policy": {
            "primary": [
                "top1_success_rate",
                "mrr",
                "ndcg_at_3",
            ],
            "secondary": [
                "brier",
                "pr_auc",
                "roc_auc",
            ],
        },
        "models": {},
    }

    model_results = results["models"]
    assert isinstance(model_results, dict)

    lr_train_predictions = (
        predict_logistic_probabilities(
            lr_model,
            train,
            contract=contract,
        ).rename(
            columns={"model_score": "score"}
        )
    )

    lr_validation_predictions = (
        predict_logistic_probabilities(
            lr_model,
            validation,
            contract=contract,
        ).rename(
            columns={"model_score": "score"}
        )
    )

    hgb_train_predictions = (
        predict_hist_gradient_probabilities(
            hgb_model,
            train,
            contract=contract,
        ).rename(
            columns={"model_score": "score"}
        )
    )

    hgb_validation_predictions = (
        predict_hist_gradient_probabilities(
            hgb_model,
            validation,
            contract=contract,
        ).rename(
            columns={"model_score": "score"}
        )
    )

    model_prediction_sets = {
        "LR": {
            "train": lr_train_predictions,
            "validation": lr_validation_predictions,
        },
        "HGB": {
            "train": hgb_train_predictions,
            "validation": hgb_validation_predictions,
        },
    }

    for name, prediction_sets in model_prediction_sets.items():
        split_results: dict[str, object] = {}

        for split_name in ("train", "validation"):
            predictions = prediction_sets[split_name]

            target = predictions[
                contract.canonical_target
            ]
            score = predictions["score"]

            binary = binary_metrics(
                target,
                score,
            )

            bins = calibration_bins(
                predictions
            )

            split_results[split_name] = {
                **binary,
                "top1_success_rate": top1_success(
                    predictions
                ),
                "pairwise_within_group_accuracy": (
                    pairwise_within_group_accuracy(
                        predictions
                    )
                ),
                "score_separation": (
                    group_score_summary(
                        predictions
                    )
                ),
                "ece_10_bin": (
                    expected_calibration_error(
                        bins
                    )
                ),
                "calibration_bins": bins,
            }

        model_results[name] = split_results

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            results,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    for name in ("LR", "HGB"):
        payload = model_results[name]
        assert isinstance(payload, dict)

        train_result = payload["train"]
        validation_result = payload["validation"]

        assert isinstance(train_result, dict)
        assert isinstance(validation_result, dict)

        print()
        print(f"=== {name} ===")

        print(
            "Train ROC-AUC              : "
            f"{train_result['roc_auc']:.6f}"
        )
        print(
            "Validation ROC-AUC         : "
            f"{validation_result['roc_auc']:.6f}"
        )

        print(
            "Train PR-AUC               : "
            f"{train_result['pr_auc']:.6f}"
        )
        print(
            "Validation PR-AUC          : "
            f"{validation_result['pr_auc']:.6f}"
        )

        print(
            "Validation Brier           : "
            f"{validation_result['brier']:.6f}"
        )
        print(
            "Validation ECE             : "
            f"{validation_result['ece_10_bin']:.6f}"
        )

        print(
            "Validation Top-1           : "
            f"{validation_result['top1_success_rate']:.6f}"
        )

        print(
            "Within-group pair accuracy : "
            f"{validation_result['pairwise_within_group_accuracy']:.6f}"
        )

        separation = validation_result[
            "score_separation"
        ]
        assert isinstance(separation, dict)

        print(
            "Mean within-group range    : "
            f"{separation['mean_group_score_range']:.6f}"
        )
        print(
            "Mean top-1 margin          : "
            f"{separation['mean_top1_margin']:.6f}"
        )

    print()
    print(f"Evidence: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
