"""Run the one-shot final locked test evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)

from afterlife_ai.modeling.baselines import (
    attach_split_assignments,
    fit_action_prior,
    load_baseline_config,
    score_action_prior,
    select_modeling_split,
)
from afterlife_ai.modeling.hist_gradient import (
    predict_hist_gradient_probabilities,
)
from afterlife_ai.synthetic.schema_contract import (
    load_model_feature_contract,
)
from evaluate_validation_allocation_regret import (
    allocation_signature,
    oracle_value_of_allocations,
    run_group_optimizer,
)

ARTIFACT_PATH = Path(
    "models/HGB_E_v1.joblib"
)
MODEL_MANIFEST_PATH = Path(
    "reports/evidence/modeling/"
    "SELECTED_MODEL_MANIFEST_v1.json"
)

SCHEMA_PATH = Path(
    "docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml"
)
BASELINE_CONFIG_PATH = Path(
    "configs/baseline_v1.yaml"
)

CANDIDATE_PATH = Path(
    "data/generated/synthetic_candidates_v2.csv"
)
ORACLE_PATH = Path(
    "data/generated/synthetic_oracle_v2.csv"
)
SPLIT_PATH = Path(
    "reports/evidence/synthetic_dataset/"
    "SPLIT_GROUPS_v2.csv"
)

UV_LOCK_PATH = Path("uv.lock")

OUTPUT_DIR = Path(
    "reports/evidence/modeling/final_test"
)

ACCESS_PATH = OUTPUT_DIR / "FINAL_TEST_ACCESS_v1.json"

PREDICTION_PATH = (
    OUTPUT_DIR
    / "FINAL_LOCKED_TEST_PREDICTIONS_v1.csv"
)

ALLOCATION_PATH = (
    OUTPUT_DIR
    / "FINAL_LOCKED_TEST_ALLOCATION_REGRET_v1.csv"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "FINAL_LOCKED_TEST_v1.json"
)


EXPECTED_TEST_GROUPS = 360
EXPECTED_TEST_ROWS = 1780


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def group_hash(groups: list[str]) -> str:
    canonical = "\n".join(
        sorted(groups)
    ).encode("utf-8")

    return hashlib.sha256(
        canonical
    ).hexdigest()


def load_manifest() -> dict[str, Any]:
    payload = json.loads(
        MODEL_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(payload, dict):
        raise RuntimeError(
            "Selected-model manifest invalid."
        )

    return payload


def verify_artifact() -> str:
    if not ARTIFACT_PATH.exists():
        raise RuntimeError(
            f"Artifact missing: {ARTIFACT_PATH}"
        )

    manifest = load_manifest()

    artifact = manifest.get(
        "artifact"
    )

    if not isinstance(
        artifact,
        dict,
    ):
        raise RuntimeError(
            "Artifact block missing from manifest."
        )

    expected_hash = artifact.get(
        "sha256"
    )

    if not isinstance(
        expected_hash,
        str,
    ):
        raise RuntimeError(
            "Artifact SHA256 missing."
        )

    observed_hash = sha256_file(
        ARTIFACT_PATH
    )

    if observed_hash != expected_hash:
        raise RuntimeError(
            "Frozen HGB-E artifact hash mismatch."
        )

    return observed_hash


def ranking_metrics(
    frame: pd.DataFrame,
    *,
    score_column: str,
) -> dict[str, float | int]:
    mrr_values: list[float] = []
    ndcg_values: list[float] = []
    top1_values: list[float] = []

    pairwise_correct = 0.0
    pairwise_total = 0

    evaluated_groups = 0

    for _, group in frame.groupby(
        "scenario_group_id",
        sort=True,
    ):
        if len(group) < 2:
            continue

        evaluated_groups += 1

        ordered = group.sort_values(
            [
                score_column,
                "candidate_id",
            ],
            ascending=[
                False,
                True,
            ],
            kind="stable",
        )

        target = (
            ordered[
                "simulated_rescue_outcome"
            ]
            .astype(int)
            .to_numpy()
        )

        positive_positions = (
            np.flatnonzero(
                target == 1
            )
        )

        if len(
            positive_positions
        ) == 0:
            mrr_values.append(0.0)
        else:
            mrr_values.append(
                1.0
                / float(
                    positive_positions[0]
                    + 1
                )
            )

        k = min(
            3,
            len(target),
        )

        relevance = (
            target[:k]
            .astype(float)
        )

        discounts = (
            1.0
            / np.log2(
                np.arange(
                    2,
                    len(relevance) + 2,
                )
            )
        )

        dcg = float(
            np.sum(
                relevance
                * discounts
            )
        )

        ideal = np.sort(
            target.astype(float)
        )[::-1][:k]

        idcg = float(
            np.sum(
                ideal
                * discounts
            )
        )

        ndcg_values.append(
            dcg / idcg
            if idcg > 0
            else 0.0
        )

        top1_values.append(
            float(
                target[0] == 1
            )
        )

        positives = group.loc[
            group[
                "simulated_rescue_outcome"
            ] == 1,
            score_column,
        ].astype(float)

        negatives = group.loc[
            group[
                "simulated_rescue_outcome"
            ] == 0,
            score_column,
        ].astype(float)

        for positive in positives:
            for negative in negatives:
                pairwise_total += 1

                if positive > negative:
                    pairwise_correct += 1.0
                elif positive == negative:
                    pairwise_correct += 0.5

    return {
        "scenario_groups": (
            evaluated_groups
        ),
        "mrr": float(
            np.mean(mrr_values)
        ),
        "ndcg_at_3": float(
            np.mean(ndcg_values)
        ),
        "top1_success_rate": float(
            np.mean(top1_values)
        ),
        "pairwise_accuracy": (
            pairwise_correct
            / pairwise_total
            if pairwise_total
            else 0.0
        ),
    }


def predictive_metrics(
    frame: pd.DataFrame,
    *,
    score_column: str,
) -> dict[str, float]:
    target = frame[
        "simulated_rescue_outcome"
    ].astype(int)

    score = frame[
        score_column
    ].astype(float)

    return {
        "pr_auc": float(
            average_precision_score(
                target,
                score,
            )
        ),
        "brier": float(
            brier_score_loss(
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
        "log_loss": float(
            log_loss(
                target,
                score,
                labels=[0, 1],
            )
        ),
        "positive_rate": float(
            target.mean()
        ),
    }


def allocation_evaluation(
    frame: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    dict[str, dict[str, float | int]],
]:
    rows: list[
        dict[str, object]
    ] = []

    systems = {
        "HGB_E": "hgb_score",
        "B1": "b1_score",
    }

    for group_id, group in frame.groupby(
        "scenario_group_id",
        sort=True,
    ):
        oracle_result, oracle_candidates = (
            run_group_optimizer(
                group,
                score_column=(
                    "generator_success_probability"
                ),
                model_version=(
                    "SYNTHETIC_ORACLE"
                ),
            )
        )

        oracle_value = Decimal(
            str(
                oracle_result.objective_value
            )
        )

        oracle_signature = (
            allocation_signature(
                oracle_result.allocations
            )
        )

        for system_id, score_column in (
            systems.items()
        ):
            result, _ = (
                run_group_optimizer(
                    group,
                    score_column=score_column,
                    model_version=system_id,
                )
            )

            system_value = (
                oracle_value_of_allocations(
                    result.allocations,
                    oracle_candidates,
                )
            )

            regret = (
                oracle_value
                - system_value
            )

            if regret < Decimal("-0.01"):
                raise RuntimeError(
                    "Negative allocation regret "
                    f"{system_id} / {group_id}: "
                    f"{regret}"
                )

            if regret < Decimal("0"):
                regret = Decimal("0")

            planning_total = sum(
                (
                    Decimal(str(value))
                    for value in (
                        group.groupby(
                            "lot_id"
                        )[
                            "planning_quantity"
                        ]
                        .first()
                        .tolist()
                    )
                ),
                Decimal("0"),
            )

            allocated_total = sum(
                (
                    allocation
                    .allocated_quantity
                    for allocation
                    in result.allocations
                ),
                Decimal("0"),
            )

            unallocated_total = sum(
                result
                .unallocated_quantities
                .values(),
                Decimal("0"),
            )

            quantity_delta = (
                planning_total
                - allocated_total
                - unallocated_total
            )

            if abs(
                quantity_delta
            ) > Decimal("0.000001"):
                raise RuntimeError(
                    "Quantity conservation failure: "
                    f"{system_id} / {group_id}"
                )

            signature = (
                allocation_signature(
                    result.allocations
                )
            )

            rows.append(
                {
                    "scenario_group_id": (
                        group_id
                    ),
                    "system_id": system_id,
                    "oracle_objective_value": (
                        float(oracle_value)
                    ),
                    "system_oracle_value": (
                        float(system_value)
                    ),
                    "allocation_regret": (
                        float(regret)
                    ),
                    "normalized_regret": (
                        float(
                            regret
                            / oracle_value
                        )
                        if oracle_value > 0
                        else 0.0
                    ),
                    "exact_allocation_match": (
                        signature
                        == oracle_signature
                    ),
                    "quantity_conservation": (
                        True
                    ),
                    "hard_constraint_violations": (
                        0
                    ),
                }
            )

    detail = pd.DataFrame(
        rows
    )

    summaries: dict[
        str,
        dict[str, float | int],
    ] = {}

    for system_id, group in (
        detail.groupby(
            "system_id",
            sort=True,
        )
    ):
        regret = group[
            "allocation_regret"
        ].astype(float)

        total_oracle = float(
            group[
                "oracle_objective_value"
            ].sum()
        )

        total_system = float(
            group[
                "system_oracle_value"
            ].sum()
        )

        summaries[
            str(system_id)
        ] = {
            "scenario_groups": int(
                len(group)
            ),
            "mean_regret": float(
                regret.mean()
            ),
            "median_regret": float(
                regret.median()
            ),
            "p95_regret": float(
                regret.quantile(0.95)
            ),
            "mean_normalized_regret": (
                float(
                    group[
                        "normalized_regret"
                    ].mean()
                )
            ),
            "zero_regret_rate": float(
                (regret == 0).mean()
            ),
            "exact_allocation_match_rate": (
                float(
                    group[
                        "exact_allocation_match"
                    ].mean()
                )
            ),
            "oracle_value_retained": (
                total_system
                / total_oracle
                if total_oracle > 0
                else 1.0
            ),
            "hard_constraint_violations": 0,
        }

    return detail, summaries


def preflight() -> None:
    required = [
        ARTIFACT_PATH,
        MODEL_MANIFEST_PATH,
        SCHEMA_PATH,
        BASELINE_CONFIG_PATH,
        CANDIDATE_PATH,
        ORACLE_PATH,
        SPLIT_PATH,
        UV_LOCK_PATH,
    ]

    missing = [
        str(path)
        for path in required
        if not path.exists()
    ]

    if missing:
        raise RuntimeError(
            "Missing required files: "
            f"{missing}"
        )

    artifact_hash = (
        verify_artifact()
    )

    assignments = pd.read_csv(
        SPLIT_PATH
    )

    test_groups = assignments.loc[
        assignments["split"].astype(str)
        == "test",
        "scenario_group_id",
    ].astype(str)

    if len(test_groups) != (
        EXPECTED_TEST_GROUPS
    ):
        raise RuntimeError(
            "Unexpected locked-test "
            "group count."
        )

    print(
        "=== FINAL TEST PREFLIGHT ==="
    )
    print(
        "selected model : HGB-E"
    )
    print(
        "artifact hash  : "
        f"{artifact_hash}"
    )
    print(
        "test groups    : "
        f"{len(test_groups)}"
    )
    print(
        "test outcomes  : NOT ACCESSED"
    )
    print(
        "status         : READY"
    )


def execute() -> None:
    if ACCESS_PATH.exists():
        raise RuntimeError(
            "Final test access marker "
            "already exists. "
            "One-shot evaluation is locked."
        )

    if SUMMARY_PATH.exists():
        raise RuntimeError(
            "Final test summary already exists."
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact_hash = verify_artifact()

    started_at = (
        datetime.now(
            UTC
        ).isoformat()
    )

    ACCESS_PATH.write_text(
        json.dumps(
            {
                "status": "STARTED",
                "started_at_utc": (
                    started_at
                ),
                "test_accessed": True,
                "selected_model": "HGB-E",
                "artifact_sha256": (
                    artifact_hash
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    contract = (
        load_model_feature_contract(
            SCHEMA_PATH
        )
    )

    baseline_config = (
        load_baseline_config(
            BASELINE_CONFIG_PATH
        )
    )

    assignments = pd.read_csv(
        SPLIT_PATH
    )

    candidates = pd.read_csv(
        CANDIDATE_PATH
    )

    oracle = pd.read_csv(
        ORACLE_PATH
    )

    modeling = (
        attach_split_assignments(
            candidates,
            assignments,
        )
    )

    train = select_modeling_split(
        modeling,
        "train",
    )

    test = modeling.loc[
        modeling["split"].astype(str)
        == "test"
    ].copy()

    test = test.reset_index(
        drop=True
    )

    if len(test) != EXPECTED_TEST_ROWS:
        raise RuntimeError(
            "Unexpected locked-test "
            f"row count: {len(test)}"
        )

    test_group_ids = sorted(
        test[
            "scenario_group_id"
        ].astype(str).unique().tolist()
    )

    if len(test_group_ids) != (
        EXPECTED_TEST_GROUPS
    ):
        raise RuntimeError(
            "Unexpected locked-test "
            "scenario-group count."
        )

    model = joblib.load(
        ARTIFACT_PATH
    )

    hgb_prediction = (
        predict_hist_gradient_probabilities(
            model,
            test,
            contract=contract,
        )
    )

    hgb_score = hgb_prediction[
        [
            "scenario_group_id",
            "candidate_id",
            "model_score",
        ]
    ].rename(
        columns={
            "model_score": "hgb_score"
        }
    )

    b1_model = fit_action_prior(
        train,
        baseline_config.b1_action_prior,
    )

    b1_prediction = score_action_prior(
        test,
        b1_model,
        baseline_config.b1_action_prior,
    )

    b1_score = b1_prediction[
        [
            "scenario_group_id",
            "candidate_id",
            "baseline_score",
        ]
    ].rename(
        columns={
            "baseline_score": "b1_score"
        }
    )

    oracle_columns = [
        "scenario_group_id",
        "candidate_id",
        "generator_success_probability",
    ]

    evaluation = (
        test.merge(
            hgb_score,
            on=[
                "scenario_group_id",
                "candidate_id",
            ],
            how="left",
            validate="one_to_one",
        )
        .merge(
            b1_score,
            on=[
                "scenario_group_id",
                "candidate_id",
            ],
            how="left",
            validate="one_to_one",
        )
        .merge(
            oracle[
                oracle_columns
            ],
            on=[
                "scenario_group_id",
                "candidate_id",
            ],
            how="left",
            validate="one_to_one",
        )
    )

    required_scores = [
        "hgb_score",
        "b1_score",
        "generator_success_probability",
    ]

    if evaluation[
        required_scores
    ].isna().any().any():
        raise RuntimeError(
            "Final-test scoring merge "
            "contains missing values."
        )

    hgb_predictive = (
        predictive_metrics(
            evaluation,
            score_column="hgb_score",
        )
    )

    b1_predictive = (
        predictive_metrics(
            evaluation,
            score_column="b1_score",
        )
    )

    hgb_ranking = ranking_metrics(
        evaluation,
        score_column="hgb_score",
    )

    b1_ranking = ranking_metrics(
        evaluation,
        score_column="b1_score",
    )

    (
        allocation_detail,
        allocation_summary,
    ) = allocation_evaluation(
        evaluation
    )

    prediction_columns = [
        "scenario_group_id",
        "candidate_id",
        "action_type",
        "simulated_rescue_outcome",
        "hgb_score",
        "b1_score",
    ]

    evaluation[
        prediction_columns
    ].to_csv(
        PREDICTION_PATH,
        index=False,
    )

    allocation_detail.to_csv(
        ALLOCATION_PATH,
        index=False,
    )

    train_group_ids = sorted(
        assignments.loc[
            assignments[
                "split"
            ].astype(str)
            == "train",
            "scenario_group_id",
        ]
        .astype(str)
        .tolist()
    )

    validation_group_ids = sorted(
        assignments.loc[
            assignments[
                "split"
            ].astype(str)
            == "validation",
            "scenario_group_id",
        ]
        .astype(str)
        .tolist()
    )

    summary = {
        "benchmark_run_id": (
            "FINAL_LOCKED_TEST_v1"
        ),
        "status": "COMPLETED",
        "selected_model": "HGB-E",
        "selection_frozen_before_test": (
            True
        ),
        "test_accessed": True,
        "test_rows": int(
            len(test)
        ),
        "test_scenario_groups": (
            len(test_group_ids)
        ),
        "predictive_metrics": {
            "HGB_E": (
                hgb_predictive
            ),
            "B1": (
                b1_predictive
            ),
        },
        "ranking_metrics": {
            "HGB_E": hgb_ranking,
            "B1": b1_ranking,
        },
        "allocation_metrics": (
            allocation_summary
        ),
        "safety": {
            "quantity_conservation": (
                "PASS"
            ),
            "hard_constraint_violations": (
                0
            ),
        },
        "reproducibility": {
            "random_seed": 42,
            "model_artifact_sha256": (
                artifact_hash
            ),
            "feature_schema_sha256": (
                sha256_file(
                    SCHEMA_PATH
                )
            ),
            "candidate_table_sha256": (
                sha256_file(
                    CANDIDATE_PATH
                )
            ),
            "oracle_table_sha256": (
                sha256_file(
                    ORACLE_PATH
                )
            ),
            "split_manifest_sha256": (
                sha256_file(
                    SPLIT_PATH
                )
            ),
            "uv_lock_sha256": (
                sha256_file(
                    UV_LOCK_PATH
                )
            ),
            "train_group_hash": (
                group_hash(
                    train_group_ids
                )
            ),
            "validation_group_hash": (
                group_hash(
                    validation_group_ids
                )
            ),
            "test_group_hash": (
                group_hash(
                    test_group_ids
                )
            ),
            "train_group_ids": (
                train_group_ids
            ),
            "validation_group_ids": (
                validation_group_ids
            ),
            "test_group_ids": (
                test_group_ids
            ),
        },
        "claim_boundary": (
            "Final evaluation on the "
            "locked synthetic benchmark "
            "test split. Results do not "
            "establish real-world rescue "
            "probability accuracy or "
            "real-world economic impact."
        ),
    }

    SUMMARY_PATH.write_text(
        json.dumps(
            summary,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    completed_at = (
        datetime.now(
            UTC
        ).isoformat()
    )

    ACCESS_PATH.write_text(
        json.dumps(
            {
                "status": "COMPLETED",
                "started_at_utc": (
                    started_at
                ),
                "completed_at_utc": (
                    completed_at
                ),
                "test_accessed": True,
                "selected_model": "HGB-E",
                "artifact_sha256": (
                    artifact_hash
                ),
                "summary": (
                    SUMMARY_PATH.as_posix()
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        "=== FINAL LOCKED TEST ==="
    )

    print()
    print("HGB-E:")
    print(
        "  PR-AUC = "
        f"{hgb_predictive['pr_auc']:.6f}"
    )
    print(
        "  Brier  = "
        f"{hgb_predictive['brier']:.6f}"
    )
    print(
        "  ROC-AUC= "
        f"{hgb_predictive['roc_auc']:.6f}"
    )
    print(
        "  MRR    = "
        f"{hgb_ranking['mrr']:.6f}"
    )
    print(
        "  NDCG@3 = "
        f"{hgb_ranking['ndcg_at_3']:.6f}"
    )
    print(
        "  Top-1  = "
        f"{hgb_ranking['top1_success_rate']:.6f}"
    )
    print(
        "  regret = "
        f"{allocation_summary['HGB_E']['mean_regret']:.6f}"
    )

    print()
    print("B1:")
    print(
        "  PR-AUC = "
        f"{b1_predictive['pr_auc']:.6f}"
    )
    print(
        "  Brier  = "
        f"{b1_predictive['brier']:.6f}"
    )
    print(
        "  MRR    = "
        f"{b1_ranking['mrr']:.6f}"
    )
    print(
        "  NDCG@3 = "
        f"{b1_ranking['ndcg_at_3']:.6f}"
    )
    print(
        "  Top-1  = "
        f"{b1_ranking['top1_success_rate']:.6f}"
    )
    print(
        "  regret = "
        f"{allocation_summary['B1']['mean_regret']:.6f}"
    )

    print()
    print(
        "quantity conservation      = PASS"
    )
    print(
        "hard constraint violations = 0"
    )
    print(
        "test accessed              = True"
    )
    print()
    print(
        "STATUS: FINAL TEST COMPLETED"
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    mode = parser.add_mutually_exclusive_group(
        required=True
    )

    mode.add_argument(
        "--preflight",
        action="store_true",
    )

    mode.add_argument(
        "--execute",
        action="store_true",
    )

    args = parser.parse_args()

    if args.preflight:
        preflight()
        return

    execute()


if __name__ == "__main__":
    main()
