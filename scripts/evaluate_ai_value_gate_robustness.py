"""Evaluate frozen HGB-E against B1 across robustness splits."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean, stdev

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
)

from afterlife_ai.modeling.baselines import (
    attach_split_assignments,
    fit_action_prior,
    load_baseline_config,
    score_action_prior,
    select_modeling_split,
)
from afterlife_ai.modeling.hist_gradient import (
    HistGradientBoostingConfig,
    fit_hist_gradient_boosting,
    load_hist_gradient_config,
    predict_hist_gradient_probabilities,
)
from afterlife_ai.modeling.robustness import (
    build_locked_test_robustness_assignments,
)
from afterlife_ai.synthetic.schema_contract import (
    load_model_feature_contract,
)

MODELING_CONFIG_PATH = Path(
    "configs/modeling_v1.yaml"
)
BASELINE_CONFIG_PATH = Path(
    "configs/baseline_v1.yaml"
)
SCHEMA_PATH = Path(
    "docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml"
)
CANDIDATE_PATH = Path(
    "data/generated/synthetic_candidates_v2.csv"
)
CANONICAL_SPLIT_PATH = Path(
    "reports/evidence/synthetic_dataset/"
    "SPLIT_GROUPS_v2.csv"
)

OUTPUT_DIR = Path(
    "reports/evidence/modeling"
)
SPLIT_OUTPUT_DIR = (
    OUTPUT_DIR / "robustness_splits"
)

METRICS_PATH = (
    OUTPUT_DIR
    / "AI_VALUE_GATE_ROBUSTNESS_v1.csv"
)
PREDICTIONS_PATH = (
    OUTPUT_DIR
    / "AI_VALUE_GATE_ROBUSTNESS_PREDICTIONS_v1.csv"
)
SUMMARY_PATH = (
    OUTPUT_DIR
    / "AI_VALUE_GATE_ROBUSTNESS_v1.json"
)

ROBUSTNESS_SEEDS = (
    42,
    137,
    2026,
)
PRIMARY_SEED = 42

BOOTSTRAP_ITERATIONS = 5000
BOOTSTRAP_SEED = 42001

BRIER_TOLERANCE = 0.01

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


@dataclass(frozen=True)
class BootstrapSummary:
    """Grouped bootstrap summary for one robustness seed."""

    observed_delta_pr_auc: float
    ci_95_low: float
    ci_95_high: float
    probability_positive: float


@dataclass(frozen=True)
class SeedMetrics:
    """Validation metrics for one locked-test robustness split."""

    robustness_seed: int
    train_groups: int
    validation_groups: int
    train_rows: int
    validation_rows: int
    hgb_e_pr_auc: float
    b1_pr_auc: float
    delta_pr_auc: float
    hgb_e_brier: float
    b1_brier: float
    delta_brier: float
    bootstrap_ci_95_low: float
    bootstrap_ci_95_high: float
    bootstrap_probability_positive: float
    seed_consistent: bool
    test_accessed: bool


def build_hgb_e_config() -> HistGradientBoostingConfig:
    """Build the validation-selected frozen HGB-E configuration."""

    base = load_hist_gradient_config(
        MODELING_CONFIG_PATH
    )

    payload = base.model_dump()

    payload.update(
        {
            "learning_rate": 0.05,
            "max_iter": 150,
            "max_leaf_nodes": 7,
            "min_samples_leaf": 40,
            "l2_regularization": 2.0,
            "max_bins": 255,
            "early_stopping": False,
            "random_state": 42,
        }
    )

    return (
        HistGradientBoostingConfig
        .model_validate(payload)
    )


def hash_group_ids(
    group_ids: set[str],
) -> str:
    """Hash a sorted set of scenario-group IDs."""

    payload = "\n".join(
        sorted(group_ids)
    ).encode("utf-8")

    return hashlib.sha256(
        payload
    ).hexdigest()


def build_comparison_frame(
    validation: pd.DataFrame,
    hgb_scores: pd.DataFrame,
    b1_scores: pd.DataFrame,
) -> pd.DataFrame:
    """Join frozen-model and B1 validation scores by candidate."""

    base = validation[
        [
            "scenario_group_id",
            "candidate_id",
            "action_type",
            "simulated_rescue_outcome",
        ]
    ].copy()

    hgb = hgb_scores[
        [
            "scenario_group_id",
            "candidate_id",
            "model_score",
        ]
    ].rename(
        columns={
            "model_score": "hgb_e_score",
        }
    )

    b1 = b1_scores[
        [
            "scenario_group_id",
            "candidate_id",
            "baseline_score",
        ]
    ].rename(
        columns={
            "baseline_score": "b1_score",
        }
    )

    result = base.merge(
        hgb,
        on=[
            "scenario_group_id",
            "candidate_id",
        ],
        how="inner",
        validate="one_to_one",
    ).merge(
        b1,
        on=[
            "scenario_group_id",
            "candidate_id",
        ],
        how="inner",
        validate="one_to_one",
    )

    if len(result) != len(validation):
        raise RuntimeError(
            "Prediction join kehilangan validation rows."
        )

    if result[
        [
            "hgb_e_score",
            "b1_score",
        ]
    ].isna().any().any():
        raise RuntimeError(
            "Prediction join menghasilkan missing score."
        )

    return result


def metric_pair(
    frame: pd.DataFrame,
) -> tuple[
    float,
    float,
    float,
    float,
]:
    """Return HGB PR, B1 PR, HGB Brier, and B1 Brier."""

    y_true = frame[
        "simulated_rescue_outcome"
    ].to_numpy(dtype=int)

    hgb_score = frame[
        "hgb_e_score"
    ].to_numpy(dtype=float)

    b1_score = frame[
        "b1_score"
    ].to_numpy(dtype=float)

    hgb_pr = float(
        average_precision_score(
            y_true,
            hgb_score,
        )
    )

    b1_pr = float(
        average_precision_score(
            y_true,
            b1_score,
        )
    )

    hgb_brier = float(
        brier_score_loss(
            y_true,
            hgb_score,
        )
    )

    b1_brier = float(
        brier_score_loss(
            y_true,
            b1_score,
        )
    )

    return (
        hgb_pr,
        b1_pr,
        hgb_brier,
        b1_brier,
    )


def grouped_bootstrap_delta_pr_auc(
    frame: pd.DataFrame,
    *,
    iterations: int,
    seed: int,
) -> tuple[
    BootstrapSummary,
    FloatArray,
]:
    """Bootstrap HGB-E minus B1 PR-AUC by scenario group."""

    groups = sorted(
        frame[
            "scenario_group_id"
        ].astype(str).unique()
    )

    if not groups:
        raise ValueError(
            "Validation frame tidak memiliki groups."
        )

    grouped_arrays: list[
        tuple[
            IntArray,
            FloatArray,
            FloatArray,
        ]
    ] = []

    for group_id in groups:
        group = frame.loc[
            frame[
                "scenario_group_id"
            ].astype(str)
            == group_id
        ]

        y_true: IntArray = np.asarray(
            group[
                "simulated_rescue_outcome"
            ].to_numpy(),
            dtype=np.int64,
        )

        hgb_score: FloatArray = np.asarray(
            group[
                "hgb_e_score"
            ].to_numpy(),
            dtype=np.float64,
        )

        b1_score: FloatArray = np.asarray(
            group[
                "b1_score"
            ].to_numpy(),
            dtype=np.float64,
        )

        grouped_arrays.append(
            (
                y_true,
                hgb_score,
                b1_score,
            )
        )

    rng = np.random.default_rng(
        seed
    )

    estimates: FloatArray = np.empty(
        iterations,
        dtype=np.float64,
    )

    group_count = len(
        grouped_arrays
    )

    for iteration in range(
        iterations
    ):
        sampled_indices = rng.integers(
            0,
            group_count,
            size=group_count,
        )

        sampled_y: IntArray = np.concatenate(
            [
                grouped_arrays[
                    int(index)
                ][0]
                for index
                in sampled_indices
            ]
        )

        sampled_hgb: FloatArray = (
            np.concatenate(
                [
                    grouped_arrays[
                        int(index)
                    ][1]
                    for index
                    in sampled_indices
                ]
            )
        )

        sampled_b1: FloatArray = (
            np.concatenate(
                [
                    grouped_arrays[
                        int(index)
                    ][2]
                    for index
                    in sampled_indices
                ]
            )
        )

        hgb_pr = float(
            average_precision_score(
                sampled_y,
                sampled_hgb,
            )
        )

        b1_pr = float(
            average_precision_score(
                sampled_y,
                sampled_b1,
            )
        )

        estimates[
            iteration
        ] = hgb_pr - b1_pr

    hgb_pr, b1_pr, _, _ = (
        metric_pair(frame)
    )

    quantiles: FloatArray = np.asarray(
        np.quantile(
            estimates,
            [
                0.025,
                0.975,
            ],
        ),
        dtype=np.float64,
    )

    summary = BootstrapSummary(
        observed_delta_pr_auc=(
            hgb_pr - b1_pr
        ),
        ci_95_low=float(
            quantiles[0]
        ),
        ci_95_high=float(
            quantiles[1]
        ),
        probability_positive=float(
            np.mean(
                estimates > 0.0
            )
        ),
    )

    return (
        summary,
        estimates,
    )


def main() -> None:
    """Run frozen HGB-E versus B1 AI Value Gate evaluation."""

    baseline_config = (
        load_baseline_config(
            BASELINE_CONFIG_PATH
        )
    )

    feature_contract = (
        load_model_feature_contract(
            SCHEMA_PATH
        )
    )

    hgb_e_config = (
        build_hgb_e_config()
    )

    candidate = pd.read_csv(
        CANDIDATE_PATH
    )

    canonical = pd.read_csv(
        CANONICAL_SPLIT_PATH
    )

    canonical_test_groups = set(
        canonical.loc[
            canonical["split"] == "test",
            "scenario_group_id",
        ].astype(str)
    )

    if len(
        canonical_test_groups
    ) != 360:
        raise RuntimeError(
            "Expected 360 locked test groups."
        )

    locked_test_hash = hash_group_ids(
        canonical_test_groups
    )

    seed_results: list[
        SeedMetrics
    ] = []

    prediction_frames: list[
        pd.DataFrame
    ] = []

    bootstrap_distributions: list[
        FloatArray
    ] = []

    SPLIT_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "=== AI VALUE GATE ROBUSTNESS ==="
    )
    print(
        "Selected model : HGB-E"
    )
    print(
        f"Seeds          : {ROBUSTNESS_SEEDS}"
    )
    print(
        "Test groups    : LOCKED"
    )
    print(
        f"Test hash      : {locked_test_hash}"
    )
    print(
        f"Bootstrap      : {BOOTSTRAP_ITERATIONS}"
    )

    for robustness_seed in ROBUSTNESS_SEEDS:
        assignments = (
            build_locked_test_robustness_assignments(
                canonical,
                seed=robustness_seed,
                primary_seed=PRIMARY_SEED,
            )
        )

        seed_test_groups = set(
            assignments.loc[
                assignments["split"]
                == "test",
                "scenario_group_id",
            ].astype(str)
        )

        if (
            seed_test_groups
            != canonical_test_groups
        ):
            raise RuntimeError(
                "Locked test groups changed "
                f"for seed {robustness_seed}."
            )

        if (
            hash_group_ids(
                seed_test_groups
            )
            != locked_test_hash
        ):
            raise RuntimeError(
                "Locked test-group hash changed."
            )

        split_path = (
            SPLIT_OUTPUT_DIR
            / (
                "ROBUSTNESS_SPLIT_"
                f"seed_{robustness_seed}_v1.csv"
            )
        )

        assignments.to_csv(
            split_path,
            index=False,
        )

        development_assignments = (
            assignments.loc[
                assignments["split"]
                != "test"
            ].copy()
        )

        development_groups = set(
            development_assignments[
                "scenario_group_id"
            ].astype(str)
        )

        if (
            development_groups
            & canonical_test_groups
        ):
            raise RuntimeError(
                "Locked test group entered "
                "development assignments."
            )

        development_candidate = (
            candidate.loc[
                candidate[
                    "scenario_group_id"
                ].astype(str).isin(
                    development_groups
                )
            ].copy()
        )

        if development_candidate[
            "scenario_group_id"
        ].astype(str).isin(
            canonical_test_groups
        ).any():
            raise RuntimeError(
                "Locked test row entered "
                "development candidate frame."
            )

        modeling = (
            attach_split_assignments(
                development_candidate,
                development_assignments,
            )
        )

        train = select_modeling_split(
            modeling,
            "train",
        )

        validation = (
            select_modeling_split(
                modeling,
                "validation",
            )
        )

        train_groups = int(
            train[
                "scenario_group_id"
            ].nunique()
        )

        validation_groups = int(
            validation[
                "scenario_group_id"
            ].nunique()
        )

        if train_groups != 1680:
            raise RuntimeError(
                "Expected 1680 train groups, "
                f"got {train_groups}."
            )

        if validation_groups != 360:
            raise RuntimeError(
                "Expected 360 validation groups, "
                f"got {validation_groups}."
            )

        hgb_model = (
            fit_hist_gradient_boosting(
                train,
                contract=feature_contract,
                config=hgb_e_config,
            )
        )

        hgb_scores = (
            predict_hist_gradient_probabilities(
                hgb_model,
                validation,
                contract=feature_contract,
            )
        )

        b1_model = fit_action_prior(
            train,
            baseline_config.b1_action_prior,
        )

        b1_scores = score_action_prior(
            validation,
            b1_model,
            baseline_config.b1_action_prior,
        )

        comparison = (
            build_comparison_frame(
                validation,
                hgb_scores,
                b1_scores,
            )
        )

        (
            hgb_pr,
            b1_pr,
            hgb_brier,
            b1_brier,
        ) = metric_pair(
            comparison
        )

        delta_pr = (
            hgb_pr - b1_pr
        )

        delta_brier = (
            hgb_brier - b1_brier
        )

        (
            bootstrap,
            bootstrap_distribution,
        ) = (
            grouped_bootstrap_delta_pr_auc(
                comparison,
                iterations=BOOTSTRAP_ITERATIONS,
                seed=(
                    BOOTSTRAP_SEED
                    + robustness_seed
                ),
            )
        )

        bootstrap_distributions.append(
            bootstrap_distribution
        )

        seed_consistent = (
            delta_pr > 0.0
            and delta_brier
            <= BRIER_TOLERANCE
        )

        seed_result = SeedMetrics(
            robustness_seed=(
                robustness_seed
            ),
            train_groups=train_groups,
            validation_groups=(
                validation_groups
            ),
            train_rows=len(train),
            validation_rows=(
                len(validation)
            ),
            hgb_e_pr_auc=hgb_pr,
            b1_pr_auc=b1_pr,
            delta_pr_auc=delta_pr,
            hgb_e_brier=hgb_brier,
            b1_brier=b1_brier,
            delta_brier=delta_brier,
            bootstrap_ci_95_low=(
                bootstrap.ci_95_low
            ),
            bootstrap_ci_95_high=(
                bootstrap.ci_95_high
            ),
            bootstrap_probability_positive=(
                bootstrap
                .probability_positive
            ),
            seed_consistent=(
                seed_consistent
            ),
            test_accessed=False,
        )

        seed_results.append(
            seed_result
        )

        comparison.insert(
            0,
            "robustness_seed",
            robustness_seed,
        )

        prediction_frames.append(
            comparison
        )

        print()
        print(
            f"--- SEED {robustness_seed} ---"
        )
        print(
            "HGB-E PR-AUC : "
            f"{hgb_pr:.6f}"
        )
        print(
            "B1 PR-AUC    : "
            f"{b1_pr:.6f}"
        )
        print(
            "Delta PR-AUC : "
            f"{delta_pr:+.6f}"
        )
        print(
            "HGB-E Brier  : "
            f"{hgb_brier:.6f}"
        )
        print(
            "B1 Brier     : "
            f"{b1_brier:.6f}"
        )
        print(
            "Delta Brier  : "
            f"{delta_brier:+.6f}"
        )
        print(
            "PR delta CI  : "
            f"[{bootstrap.ci_95_low:+.6f}, "
            f"{bootstrap.ci_95_high:+.6f}]"
        )
        print(
            "P(delta > 0) : "
            f"{bootstrap.probability_positive:.2%}"
        )
        print(
            "Seed status  : "
            + (
                "CONSISTENT"
                if seed_consistent
                else "NOT_CONSISTENT"
            )
        )

    hgb_pr_values = [
        result.hgb_e_pr_auc
        for result in seed_results
    ]

    b1_pr_values = [
        result.b1_pr_auc
        for result in seed_results
    ]

    hgb_brier_values = [
        result.hgb_e_brier
        for result in seed_results
    ]

    b1_brier_values = [
        result.b1_brier
        for result in seed_results
    ]

    hgb_mean_pr = mean(
        hgb_pr_values
    )

    b1_mean_pr = mean(
        b1_pr_values
    )

    hgb_mean_brier = mean(
        hgb_brier_values
    )

    b1_mean_brier = mean(
        b1_brier_values
    )

    mean_delta_pr = (
        hgb_mean_pr
        - b1_mean_pr
    )

    mean_delta_brier = (
        hgb_mean_brier
        - b1_mean_brier
    )

    stacked_bootstrap: FloatArray = (
        np.vstack(
            bootstrap_distributions
        )
    )

    aggregate_bootstrap: FloatArray = (
        np.asarray(
            np.mean(
                stacked_bootstrap,
                axis=0,
            ),
            dtype=np.float64,
        )
    )

    aggregate_quantiles: FloatArray = (
        np.asarray(
            np.quantile(
                aggregate_bootstrap,
                [
                    0.025,
                    0.975,
                ],
            ),
            dtype=np.float64,
        )
    )

    aggregate_ci_low = float(
        aggregate_quantiles[0]
    )

    aggregate_ci_high = float(
        aggregate_quantiles[1]
    )

    aggregate_probability_positive = (
        float(
            np.mean(
                aggregate_bootstrap
                > 0.0
            )
        )
    )

    consistent_seed_count = sum(
        result.seed_consistent
        for result in seed_results
    )

    gate_pr_auc = (
        hgb_mean_pr
        > b1_mean_pr
    )

    gate_brier = (
        mean_delta_brier
        <= BRIER_TOLERANCE
    )

    gate_bootstrap = (
        aggregate_ci_low
        > 0.0
    )

    gate_seed_consistency = (
        consistent_seed_count >= 2
    )

    gate_passed = all(
        (
            gate_pr_auc,
            gate_brier,
            gate_bootstrap,
            gate_seed_consistency,
        )
    )

    metrics_frame = pd.DataFrame(
        [
            asdict(result)
            for result in seed_results
        ]
    )

    predictions_frame = pd.concat(
        prediction_frames,
        ignore_index=True,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_frame.to_csv(
        METRICS_PATH,
        index=False,
    )

    predictions_frame.to_csv(
        PREDICTIONS_PATH,
        index=False,
    )

    summary = {
        "evaluation_version": "1.0.0",
        "selected_model": "HGB_E",
        "selected_model_config": (
            hgb_e_config.model_dump()
        ),
        "baseline": "B1",
        "robustness_seeds": list(
            ROBUSTNESS_SEEDS
        ),
        "primary_seed": PRIMARY_SEED,
        "locked_test_group_count": len(
            canonical_test_groups
        ),
        "locked_test_group_sha256": (
            locked_test_hash
        ),
        "test_accessed": False,
        "bootstrap": {
            "unit": "scenario_group_id",
            "iterations": (
                BOOTSTRAP_ITERATIONS
            ),
            "base_seed": (
                BOOTSTRAP_SEED
            ),
            "aggregate_method": (
                "mean of independently "
                "group-bootstrapped seed-level "
                "PR-AUC deltas"
            ),
        },
        "aggregate_metrics": {
            "hgb_e_pr_auc_mean": (
                hgb_mean_pr
            ),
            "hgb_e_pr_auc_std": stdev(
                hgb_pr_values
            ),
            "b1_pr_auc_mean": (
                b1_mean_pr
            ),
            "b1_pr_auc_std": stdev(
                b1_pr_values
            ),
            "mean_delta_pr_auc": (
                mean_delta_pr
            ),
            "hgb_e_brier_mean": (
                hgb_mean_brier
            ),
            "hgb_e_brier_std": stdev(
                hgb_brier_values
            ),
            "b1_brier_mean": (
                b1_mean_brier
            ),
            "b1_brier_std": stdev(
                b1_brier_values
            ),
            "mean_delta_brier": (
                mean_delta_brier
            ),
            "aggregate_delta_pr_auc_ci_95": {
                "low": aggregate_ci_low,
                "high": aggregate_ci_high,
            },
            "aggregate_probability_delta_positive": (
                aggregate_probability_positive
            ),
            "consistent_seed_count": (
                consistent_seed_count
            ),
        },
        "gate": {
            "criterion_1_mean_pr_auc_higher": (
                gate_pr_auc
            ),
            "criterion_2_mean_brier_not_worse_by_more_than_0_01": (
                gate_brier
            ),
            "criterion_3_bootstrap_lower_bound_above_zero": (
                gate_bootstrap
            ),
            "criterion_4_consistent_at_least_2_of_3_seeds": (
                gate_seed_consistency
            ),
            "passed": gate_passed,
        },
        "seed_results": [
            asdict(result)
            for result in seed_results
        ],
        "claim_boundary": (
            "Metrics quantify performance only "
            "against the frozen synthetic "
            "benchmark generation process."
        ),
    }

    SUMMARY_PATH.write_text(
        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        "=== AGGREGATE ==="
    )
    print(
        "HGB-E PR-AUC : "
        f"{hgb_mean_pr:.6f} "
        f"+/- {stdev(hgb_pr_values):.6f}"
    )
    print(
        "B1 PR-AUC    : "
        f"{b1_mean_pr:.6f} "
        f"+/- {stdev(b1_pr_values):.6f}"
    )
    print(
        "Mean delta   : "
        f"{mean_delta_pr:+.6f}"
    )
    print(
        "HGB-E Brier  : "
        f"{hgb_mean_brier:.6f} "
        f"+/- {stdev(hgb_brier_values):.6f}"
    )
    print(
        "B1 Brier     : "
        f"{b1_mean_brier:.6f} "
        f"+/- {stdev(b1_brier_values):.6f}"
    )
    print(
        "Mean delta   : "
        f"{mean_delta_brier:+.6f}"
    )
    print(
        "Aggregate PR delta 95% CI: "
        f"[{aggregate_ci_low:+.6f}, "
        f"{aggregate_ci_high:+.6f}]"
    )
    print(
        "Consistent seeds: "
        f"{consistent_seed_count}/3"
    )

    print()
    print(
        "=== AI VALUE GATE ==="
    )
    print(
        "1 mean PR-AUC higher : "
        f"{gate_pr_auc}"
    )
    print(
        "2 Brier tolerance    : "
        f"{gate_brier}"
    )
    print(
        "3 bootstrap CI > 0   : "
        f"{gate_bootstrap}"
    )
    print(
        "4 consistency >=2/3  : "
        f"{gate_seed_consistency}"
    )
    print(
        "AI VALUE GATE        : "
        + (
            "PASS"
            if gate_passed
            else "FAIL"
        )
    )

    print()
    print(
        f"Metrics     : {METRICS_PATH}"
    )
    print(
        f"Predictions : {PREDICTIONS_PATH}"
    )
    print(
        f"Summary     : {SUMMARY_PATH}"
    )
    print(
        "Test accessed: False"
    )


if __name__ == "__main__":
    main()
