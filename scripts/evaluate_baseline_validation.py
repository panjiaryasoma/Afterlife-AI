"""Evaluate B0/B1 score-layer baselines on validation only."""

import json
from pathlib import Path

import pandas as pd

from afterlife_ai.modeling.metrics import (
    evaluate_ranking_scores,
)

INPUT_PATH = Path(
    "reports/evidence/modeling/"
    "BASELINE_VALIDATION_PREDICTIONS_v1.csv"
)

OUTPUT_PATH = Path(
    "reports/evidence/modeling/"
    "BASELINE_VALIDATION_METRICS_v1.json"
)


def main() -> None:
    """Evaluate validation predictions without test access."""

    predictions = pd.read_csv(INPUT_PATH)

    results: dict[str, object] = {
        "report_version": "1.0.0",
        "evaluation_split": "validation",
        "test_accessed": False,
        "score_layer_only": True,
        "baselines": {},
    }

    baseline_results = results["baselines"]
    assert isinstance(baseline_results, dict)

    for baseline_id in ("B0", "B1"):
        frame = predictions.loc[
            predictions["baseline_id"] == baseline_id
        ].copy()

        metrics = evaluate_ranking_scores(frame)

        payload = {
            "candidate_rows": metrics.candidate_rows,
            "scenario_groups": metrics.scenario_groups,
            "roc_auc": metrics.roc_auc,
            "pr_auc": metrics.pr_auc,
            "top1_success_rate": metrics.top1_success_rate,
            "mrr": metrics.mrr,
            "ndcg_at_3": metrics.ndcg_at_3,
        }

        baseline_results[baseline_id] = payload

        print()
        print(f"=== {baseline_id} ===")

        for key, value in payload.items():
            if isinstance(value, float):
                print(f"{key:<20}: {value:.6f}")
            else:
                print(f"{key:<20}: {value}")

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

    print()
    print(f"Evidence: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
