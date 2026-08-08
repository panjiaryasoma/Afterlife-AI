"""Train HGB on train only and score validation."""

import json
from pathlib import Path

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
from afterlife_ai.modeling.metrics import (
    evaluate_ranking_scores,
)
from afterlife_ai.synthetic.schema_contract import (
    load_model_feature_contract,
)

MODELING_CONFIG_PATH = Path("configs/modeling_v1.yaml")
SCHEMA_PATH = Path(
    "docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml"
)

CANDIDATE_PATH = Path(
    "data/generated/synthetic_candidates_v2.csv"
)
SPLIT_PATH = Path(
    "reports/evidence/synthetic_dataset/SPLIT_GROUPS_v2.csv"
)

PREDICTION_PATH = Path(
    "reports/evidence/modeling/"
    "HIST_GRADIENT_VALIDATION_PREDICTIONS_v1.csv"
)
METRICS_PATH = Path(
    "reports/evidence/modeling/"
    "HIST_GRADIENT_VALIDATION_METRICS_v1.json"
)


def main() -> None:
    """Fit HGB and evaluate validation without test access."""

    config = load_hist_gradient_config(
        MODELING_CONFIG_PATH
    )
    contract = load_model_feature_contract(SCHEMA_PATH)

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

    model = fit_hist_gradient_boosting(
        train,
        contract=contract,
        config=config,
    )

    predictions = predict_hist_gradient_probabilities(
        model,
        validation,
        contract=contract,
    )

    PREDICTION_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    predictions.to_csv(
        PREDICTION_PATH,
        index=False,
        lineterminator="\n",
    )

    metric_frame = predictions.rename(
        columns={"model_score": "baseline_score"}
    )

    ranking = evaluate_ranking_scores(metric_frame)

    target = predictions[contract.canonical_target]
    probability = predictions["model_score"]

    metrics = {
        "report_version": "1.0.0",
        "model_id": model.model_id,
        "fit_split": "train",
        "evaluation_split": "validation",
        "test_accessed": False,
        "training_rows": model.training_rows,
        "validation_rows": len(validation),
        "roc_auc": float(
            roc_auc_score(target, probability)
        ),
        "pr_auc": float(
            average_precision_score(target, probability)
        ),
        "brier_score": float(
            brier_score_loss(target, probability)
        ),
        "top1_success_rate": ranking.top1_success_rate,
        "mrr": ranking.mrr,
        "ndcg_at_3": ranking.ndcg_at_3,
    }

    METRICS_PATH.write_text(
        json.dumps(
            metrics,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print("HistGradientBoosting validation complete")
    print(f"Train rows          : {model.training_rows}")
    print(f"Validation rows     : {len(validation)}")
    print(f"ROC-AUC             : {metrics['roc_auc']:.6f}")
    print(f"PR-AUC              : {metrics['pr_auc']:.6f}")
    print(f"Brier score         : {metrics['brier_score']:.6f}")
    print(
        "Top-1 success       : "
        f"{metrics['top1_success_rate']:.6f}"
    )
    print(f"MRR                 : {metrics['mrr']:.6f}")
    print(f"NDCG@3              : {metrics['ndcg_at_3']:.6f}")
    print(f"Predictions         : {PREDICTION_PATH}")
    print(f"Metrics             : {METRICS_PATH}")


if __name__ == "__main__":
    main()
