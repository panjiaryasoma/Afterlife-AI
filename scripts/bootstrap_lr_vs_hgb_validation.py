"""Paired grouped bootstrap for LR versus HGB validation."""

import json
from pathlib import Path

import pandas as pd

from afterlife_ai.modeling.bootstrap import (
    paired_group_bootstrap,
)

LR_PATH = Path(
    "reports/evidence/modeling/"
    "LOGISTIC_VALIDATION_PREDICTIONS_v1.csv"
)

HGB_PATH = Path(
    "reports/evidence/modeling/"
    "HIST_GRADIENT_VALIDATION_PREDICTIONS_v1.csv"
)

LR_METRICS_PATH = Path(
    "reports/evidence/modeling/"
    "LOGISTIC_VALIDATION_METRICS_v1.json"
)

HGB_METRICS_PATH = Path(
    "reports/evidence/modeling/"
    "HIST_GRADIENT_VALIDATION_METRICS_v1.json"
)

OUTPUT_PATH = Path(
    "reports/evidence/modeling/"
    "LR_VS_HGB_GROUP_BOOTSTRAP_v1.json"
)

ITERATIONS = 5000
BOOTSTRAP_SEED = 42


def main() -> None:
    """Run paired bootstrap using validation scenario groups only."""

    lr = pd.read_csv(LR_PATH)
    hgb = pd.read_csv(HGB_PATH)

    keys = [
        "scenario_group_id",
        "candidate_id",
        "action_type",
        "simulated_rescue_outcome",
    ]

    lr_frame = lr[
        keys + ["model_score"]
    ].rename(
        columns={
            "model_score": "lr_score",
        }
    )

    hgb_frame = hgb[
        keys + ["model_score"]
    ].rename(
        columns={
            "model_score": "hgb_score",
        }
    )

    comparison = lr_frame.merge(
        hgb_frame,
        on=keys,
        how="inner",
        validate="one_to_one",
    )

    if len(comparison) != len(lr):
        raise RuntimeError(
            "LR/HGB validation predictions tidak aligned."
        )

    if len(comparison) != len(hgb):
        raise RuntimeError(
            "LR/HGB validation predictions tidak aligned."
        )

    report = paired_group_bootstrap(
        comparison,
        iterations=ITERATIONS,
        seed=BOOTSTRAP_SEED,
    )

    lr_expected = json.loads(
        LR_METRICS_PATH.read_text(
            encoding="utf-8"
        )
    )

    hgb_expected = json.loads(
        HGB_METRICS_PATH.read_text(
            encoding="utf-8"
        )
    )

    metrics = report["metrics"]

    expected_mapping = {
        "pr_auc": "pr_auc",
        "brier_score": "brier_score",
        "roc_auc": "roc_auc",
        "top1_success_rate": (
            "top1_success_rate"
        ),
        "mrr": "mrr",
        "ndcg_at_3": "ndcg_at_3",
    }

    for metric, evidence_key in (
        expected_mapping.items()
    ):
        lr_error = abs(
            metrics[metric]["lr"]
            - float(
                lr_expected[evidence_key]
            )
        )

        hgb_error = abs(
            metrics[metric]["hgb"]
            - float(
                hgb_expected[evidence_key]
            )
        )

        if lr_error > 1e-12:
            raise RuntimeError(
                f"LR metric mismatch for {metric}: "
                f"{lr_error}"
            )

        if hgb_error > 1e-12:
            raise RuntimeError(
                f"HGB metric mismatch for {metric}: "
                f"{hgb_error}"
            )

    output = {
        "report_version": "1.0.0",
        "evaluation_split": "validation",
        "test_accessed": False,
        "bootstrap_unit": "scenario_group_id",
        "claim_boundary": (
            "Synthetic validation benchmark only; "
            "not real-world rescue performance."
        ),
        **report,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            output,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print("=== LR vs HGB Paired Group Bootstrap ===")
    print(
        f"Scenario groups : {report['scenario_groups']}"
    )
    print(
        f"Iterations      : {report['iterations']}"
    )
    print(
        f"Bootstrap seed  : {report['bootstrap_seed']}"
    )

    for metric_name in (
        "pr_auc",
        "brier_score",
        "roc_auc",
        "top1_success_rate",
        "mrr",
        "ndcg_at_3",
    ):
        metric = metrics[metric_name]

        print()
        print(f"--- {metric_name} ---")
        print(
            f"LR                  : {metric['lr']:.6f}"
        )
        print(
            f"HGB                 : {metric['hgb']:.6f}"
        )
        print(
            "Delta LR-HGB        : "
            f"{metric['delta_lr_minus_hgb']:+.6f}"
        )
        print(
            "95% CI              : "
            f"[{metric['ci_95_lower']:+.6f}, "
            f"{metric['ci_95_upper']:+.6f}]"
        )
        print(
            "LR bootstrap win    : "
            f"{metric['lr_win_fraction']:.2%}"
        )

    print()
    print(f"Evidence: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
