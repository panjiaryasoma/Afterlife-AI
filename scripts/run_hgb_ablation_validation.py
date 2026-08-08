"""Run the bounded HGB regularization experiment on validation only."""

import json
from pathlib import Path

import pandas as pd
import yaml
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
    HistGradientBoostingConfig,
    fit_hist_gradient_boosting,
    predict_hist_gradient_probabilities,
)
from afterlife_ai.modeling.metrics import (
    evaluate_ranking_scores,
)
from afterlife_ai.synthetic.schema_contract import (
    load_model_feature_contract,
)

ABLATION_CONFIG = Path("configs/hgb_ablation_v1.yaml")
SCHEMA_PATH = Path(
    "docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml"
)

CANDIDATE_PATH = Path(
    "data/generated/synthetic_candidates_v2.csv"
)

SPLIT_PATH = Path(
    "reports/evidence/synthetic_dataset/SPLIT_GROUPS_v2.csv"
)

LR_METRICS_PATH = Path(
    "reports/evidence/modeling/"
    "LOGISTIC_VALIDATION_METRICS_v1.json"
)

LR_HGB_DIAGNOSTIC_PATH = Path(
    "reports/evidence/modeling/"
    "LR_VS_HGB_DIAGNOSTIC_v1.json"
)

OUTPUT_JSON = Path(
    "reports/evidence/modeling/"
    "HGB_ABLATION_VALIDATION_v1.json"
)

OUTPUT_CSV = Path(
    "reports/evidence/modeling/"
    "HGB_ABLATION_VALIDATION_v1.csv"
)


ALLOWED_VARIANTS = {
    "HGB_A",
    "HGB_B",
    "HGB_C",
    "HGB_D",
    "HGB_E",
    "HGB_V1",
}


def evaluate(
    frame: pd.DataFrame,
    score_column: str,
) -> dict[str, float]:
    """Calculate probabilistic and ranking metrics."""

    target = frame["simulated_rescue_outcome"]
    score = frame[score_column]

    ranking_frame = frame.rename(
        columns={score_column: "baseline_score"}
    )

    ranking = evaluate_ranking_scores(
        ranking_frame
    )

    return {
        "pr_auc": float(
            average_precision_score(
                target,
                score,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                target,
                score,
            )
        ),
        "brier_score": float(
            brier_score_loss(
                target,
                score,
            )
        ),
        "top1_success_rate": (
            ranking.top1_success_rate
        ),
        "mrr": ranking.mrr,
        "ndcg_at_3": ranking.ndcg_at_3,
    }


def main() -> None:
    """Run the predefined bounded HGB variants."""

    payload = yaml.safe_load(
        ABLATION_CONFIG.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(payload, dict):
        raise ValueError(
            "Ablation config harus berupa YAML mapping."
        )

    variants = payload.get("variants")
    fixed = payload.get("fixed")
    policy = payload.get("selection_policy")

    if not isinstance(variants, dict):
        raise ValueError(
            "Ablation variants tidak ditemukan."
        )

    if not isinstance(fixed, dict):
        raise ValueError(
            "Fixed HGB parameters tidak ditemukan."
        )

    if not isinstance(policy, dict):
        raise ValueError(
            "Selection policy tidak ditemukan."
        )

    if set(variants) != ALLOWED_VARIANTS:
        raise ValueError(
            "Bounded experiment berubah. "
            "Expected variants: "
            f"{sorted(ALLOWED_VARIANTS)}"
        )

    contract = load_model_feature_contract(
        SCHEMA_PATH
    )

    candidate = pd.read_csv(
        CANDIDATE_PATH
    )

    assignments = pd.read_csv(
        SPLIT_PATH
    )

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

    results: dict[str, object] = {}

    table_rows: list[
        dict[str, object]
    ] = []

    for variant_id in sorted(variants):
        variant = variants[variant_id]

        if not isinstance(variant, dict):
            raise ValueError(
                f"Variant {variant_id} invalid."
            )

        config = HistGradientBoostingConfig(
            model_id="M1_HIST_GRADIENT_BOOSTING",
            learning_rate=float(
                fixed["learning_rate"]
            ),
            max_iter=int(
                variant["max_iter"]
            ),
            max_leaf_nodes=int(
                variant["max_leaf_nodes"]
            ),
            min_samples_leaf=int(
                variant["min_samples_leaf"]
            ),
            l2_regularization=float(
                variant["l2_regularization"]
            ),
            max_bins=int(
                fixed["max_bins"]
            ),
            early_stopping=False,
            random_state=int(
                fixed["random_state"]
            ),
        )

        model = fit_hist_gradient_boosting(
            train,
            contract=contract,
            config=config,
        )

        train_predictions = (
            predict_hist_gradient_probabilities(
                model,
                train,
                contract=contract,
            )
            .rename(
                columns={
                    "model_score": "score"
                }
            )
        )

        validation_predictions = (
            predict_hist_gradient_probabilities(
                model,
                validation,
                contract=contract,
            )
            .rename(
                columns={
                    "model_score": "score"
                }
            )
        )

        train_metrics = evaluate(
            train_predictions,
            "score",
        )

        validation_metrics = evaluate(
            validation_predictions,
            "score",
        )

        pr_gap = (
            train_metrics["pr_auc"]
            - validation_metrics["pr_auc"]
        )

        roc_gap = (
            train_metrics["roc_auc"]
            - validation_metrics["roc_auc"]
        )

        results[variant_id] = {
            "hypothesis": (
                variant["hypothesis"]
            ),
            "parameters": {
                "learning_rate": (
                    config.learning_rate
                ),
                "max_iter": config.max_iter,
                "max_leaf_nodes": (
                    config.max_leaf_nodes
                ),
                "min_samples_leaf": (
                    config.min_samples_leaf
                ),
                "l2_regularization": (
                    config.l2_regularization
                ),
                "early_stopping": (
                    config.early_stopping
                ),
                "random_state": (
                    config.random_state
                ),
            },
            "train": train_metrics,
            "validation": (
                validation_metrics
            ),
            "diagnostic_gap": {
                "pr_auc": pr_gap,
                "roc_auc": roc_gap,
            },
        }

        table_rows.append(
            {
                "model": variant_id,
                "max_iter": config.max_iter,
                "max_leaf_nodes": (
                    config.max_leaf_nodes
                ),
                "min_samples_leaf": (
                    config.min_samples_leaf
                ),
                "l2_regularization": (
                    config.l2_regularization
                ),
                "train_pr_auc": (
                    train_metrics["pr_auc"]
                ),
                "validation_pr_auc": (
                    validation_metrics["pr_auc"]
                ),
                "validation_brier": (
                    validation_metrics[
                        "brier_score"
                    ]
                ),
                "validation_roc_auc": (
                    validation_metrics[
                        "roc_auc"
                    ]
                ),
                "validation_top1": (
                    validation_metrics[
                        "top1_success_rate"
                    ]
                ),
                "validation_mrr": (
                    validation_metrics["mrr"]
                ),
                "validation_ndcg_at_3": (
                    validation_metrics[
                        "ndcg_at_3"
                    ]
                ),
                "pr_gap": pr_gap,
                "roc_gap": roc_gap,
            }
        )

    lr_metrics = json.loads(
        LR_METRICS_PATH.read_text(
            encoding="utf-8"
        )
    )

    diagnostic = json.loads(
        LR_HGB_DIAGNOSTIC_PATH.read_text(
            encoding="utf-8"
        )
    )

    lr_train = (
        diagnostic["models"]["LR"]["train"]
    )

    lr_row: dict[str, object] = {
        "model": "LR",
        "max_iter": None,
        "max_leaf_nodes": None,
        "min_samples_leaf": None,
        "l2_regularization": None,
        "train_pr_auc": float(
            lr_train["pr_auc"]
        ),
        "validation_pr_auc": float(
            lr_metrics["pr_auc"]
        ),
        "validation_brier": float(
            lr_metrics["brier_score"]
        ),
        "validation_roc_auc": float(
            lr_metrics["roc_auc"]
        ),
        "validation_top1": float(
            lr_metrics[
                "top1_success_rate"
            ]
        ),
        "validation_mrr": float(
            lr_metrics["mrr"]
        ),
        "validation_ndcg_at_3": float(
            lr_metrics["ndcg_at_3"]
        ),
        "pr_gap": float(
            lr_train["pr_auc"]
            - lr_metrics["pr_auc"]
        ),
        "roc_gap": float(
            lr_train["roc_auc"]
            - lr_metrics["roc_auc"]
        ),
    }

    table_rows.append(lr_row)

    table = pd.DataFrame(
        table_rows
    )

    best_pr_auc = float(
        table[
            "validation_pr_auc"
        ].max()
    )

    relative_window = float(
        policy["pr_auc_relative_window"]
    )

    threshold = (
        best_pr_auc
        * (1.0 - relative_window)
    )

    table[
        "within_1pct_relative_best_pr"
    ] = (
        table["validation_pr_auc"]
        >= threshold
    )

    competitive = table.loc[
        table[
            "within_1pct_relative_best_pr"
        ]
    ].copy()

    probability_winner = (
        competitive.sort_values(
            [
                "validation_brier",
                "model",
            ],
            ascending=[
                True,
                True,
            ],
            kind="stable",
        )
        .iloc[0]["model"]
    )

    report = {
        "report_version": "1.0.0",
        "experiment": (
            "BOUNDED_HGB_REGULARIZATION"
        ),
        "evaluation_split": "validation",
        "test_accessed": False,
        "bounded_variant_ids": sorted(
            ALLOWED_VARIANTS
        ),
        "hypotheses": {
            "H1": (
                "HGB v1 may use too many "
                "boosting iterations."
            ),
            "H2": (
                "A lower-capacity regularized "
                "configuration package may "
                "generalize better."
            ),
        },
        "interpretation_guardrails": [
            (
                "Train-validation gap is "
                "diagnostic only and is not "
                "a model-selection objective."
            ),
            (
                "HGB_D and HGB_E jointly "
                "change tree size, minimum "
                "leaf samples, and L2; they "
                "are configuration packages, "
                "not single-factor ablations."
            ),
            (
                "Validation is used for bounded "
                "configuration selection; any "
                "post-selection interval is "
                "selection-conditional."
            ),
            (
                "The locked test split remains "
                "untouched until the final "
                "model/configuration is frozen."
            ),
            (
                "Ranking metrics are diagnostic "
                "and do not override the locked "
                "PR-AUC/Brier selection policy."
            ),
        ],
        "selection_policy": {
            "best_validation_pr_auc": (
                best_pr_auc
            ),
            "relative_window": (
                relative_window
            ),
            "competitive_pr_auc_threshold": (
                threshold
            ),
            "probability_metric_shortlist_winner": (
                str(probability_winner)
            ),
            "final_selection_complete": False,
            "remaining_selection_stages": [
                "allocation_regret",
                "complexity",
                "robustness_seeds",
                "AI_value_gate",
            ],
        },
        "hgb_variants": results,
        "comparison_table": (
            table.to_dict(
                orient="records"
            )
        ),
    }

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    table.to_csv(
        OUTPUT_CSV,
        index=False,
        lineterminator="\n",
    )

    display_columns = [
        "model",
        "max_iter",
        "max_leaf_nodes",
        "min_samples_leaf",
        "l2_regularization",
        "train_pr_auc",
        "validation_pr_auc",
        "validation_brier",
        "validation_top1",
        "pr_gap",
        "within_1pct_relative_best_pr",
    ]

    print(
        table[
            display_columns
        ].to_string(
            index=False
        )
    )

    print()
    print(
        "Best validation PR-AUC      : "
        f"{best_pr_auc:.6f}"
    )
    print(
        "1% relative PR threshold   : "
        f"{threshold:.6f}"
    )
    print(
        "Probability shortlist winner: "
        f"{probability_winner}"
    )
    print(
        "Final model selected       : False"
    )
    print()
    print(
        f"Evidence JSON: {OUTPUT_JSON}"
    )
    print(
        f"Evidence CSV : {OUTPUT_CSV}"
    )


if __name__ == "__main__":
    main()
