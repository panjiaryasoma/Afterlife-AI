"""Audit frozen benchmark context and effective nonlinear structure."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from afterlife_ai.synthetic.outcome import load_outcome_recipe

RECIPE_PATH = Path("configs/synthetic_outcome_v1.yaml")
CANDIDATE_PATH = Path(
    "data/generated/synthetic_candidates_v2.csv"
)
ORACLE_PATH = Path(
    "data/generated/synthetic_oracle_v2.csv"
)
SPLIT_PATH = Path(
    "reports/evidence/synthetic_dataset/SPLIT_GROUPS_v2.csv"
)

BASELINE_METRICS_PATH = Path(
    "reports/evidence/modeling/"
    "BASELINE_VALIDATION_METRICS_v1.json"
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
    "BENCHMARK_CONTEXT_AUDIT_v1.json"
)


def _sigmoid(values: pd.Series) -> pd.Series:
    array = values.to_numpy(dtype=float)

    result = np.empty_like(array)

    nonnegative = array >= 0

    result[nonnegative] = (
        1.0 / (1.0 + np.exp(-array[nonnegative]))
    )

    exp_values = np.exp(array[~nonnegative])

    result[~nonnegative] = (
        exp_values / (1.0 + exp_values)
    )

    return pd.Series(
        result,
        index=values.index,
        dtype=float,
    )


def _rank_correlation(
    left: pd.Series,
    right: pd.Series,
) -> float:
    left_rank = left.rank(method="average")
    right_rank = right.rank(method="average")

    value = left_rank.corr(right_rank)

    if pd.isna(value):
        return 0.0

    return float(value)


def _uniform_random_top1_expectation(
    frame: pd.DataFrame,
) -> float:
    """Expected success if one candidate is chosen uniformly per group."""

    group_positive_rates = frame.groupby(
        "scenario_group_id",
        sort=True,
    )["simulated_rescue_outcome"].mean()

    return float(group_positive_rates.mean())


def _top_candidate_ids(
    frame: pd.DataFrame,
    score_column: str,
) -> pd.Series:
    ordered = frame.sort_values(
        [
            "scenario_group_id",
            score_column,
            "candidate_id",
        ],
        ascending=[True, False, True],
        kind="stable",
    )

    return (
        ordered.groupby(
            "scenario_group_id",
            sort=True,
        )
        .head(1)
        .set_index("scenario_group_id")[
            "candidate_id"
        ]
    )


def main() -> None:
    recipe = load_outcome_recipe(RECIPE_PATH)

    candidate = pd.read_csv(CANDIDATE_PATH)
    oracle = pd.read_csv(ORACLE_PATH)
    assignments = pd.read_csv(SPLIT_PATH)

    frame = candidate.merge(
        assignments[
            [
                "scenario_group_id",
                "split",
            ]
        ],
        on="scenario_group_id",
        how="left",
        validate="many_to_one",
    )

    frame = frame.merge(
        oracle[
            [
                "candidate_id",
                "generator_success_probability",
            ]
        ],
        on="candidate_id",
        how="left",
        validate="one_to_one",
    )

    if frame["split"].isna().any():
        raise RuntimeError(
            "Candidate tanpa split assignment ditemukan."
        )

    if frame[
        "generator_success_probability"
    ].isna().any():
        raise RuntimeError(
            "Candidate tanpa oracle probability ditemukan."
        )

    # --------------------------------------------------------
    # Reconstruct engineered latent terms from frozen outcome.py
    # --------------------------------------------------------

    normal_price = frame[
        "normal_selling_price"
    ].clip(lower=1.0)

    offered_price = frame[
        "offered_or_selling_price_per_unit"
    ]

    unit_cost = frame["unit_cost"].clip(lower=1.0)

    planning_quantity = frame[
        "planning_quantity"
    ].clip(lower=1.0)

    price_recovery_ratio = (
        offered_price / normal_price
    )

    shelf_life_days = frame[
        "remaining_shelf_life_days"
    ].clip(lower=0.0)

    shelf_life_log = (
        np.log1p(shelf_life_days)
        / np.log1p(365.0)
    )

    demand_quantity = frame[
        "active_demand_quantity"
    ].clip(lower=0.0)

    demand_fit = (
        (demand_quantity / planning_quantity)
        .clip(upper=2.0)
        / 2.0
    )

    capability_fit = (
        frame["capability_resource_ratio"]
        .clip(lower=0.0, upper=1.5)
        / 1.5
    )

    completion_hours = frame[
        "estimated_completion_hours"
    ].clip(lower=0.0)

    safe_window_hours = frame[
        "remaining_safe_window_hours"
    ].clip(lower=1.0)

    completion_ratio = (
        completion_hours / safe_window_hours
    )

    completion_pressure = (
        completion_ratio
        .clip(upper=3.0)
        / 3.0
    )

    logistics_cost = frame[
        "logistics_cost"
    ].clip(lower=0.0)

    logistics_pressure = (
        (
            logistics_cost
            / (
                unit_cost
                * planning_quantity
            ).clip(lower=1.0)
        )
        .clip(upper=2.0)
        / 2.0
    )

    distance_km = frame[
        "distance_km"
    ].clip(lower=0.0)

    distance_log = (
        np.log1p(distance_km)
        / np.log1p(40.0)
    )

    # --------------------------------------------------------
    # Additive logistic core
    # --------------------------------------------------------

    weights = recipe.weights

    additive_score = pd.Series(
        recipe.intercept,
        index=frame.index,
        dtype=float,
    )

    additive_score += (
        weights["price_recovery_ratio"]
        * price_recovery_ratio
    )

    additive_score += (
        weights["shelf_life_log"]
        * shelf_life_log
    )

    additive_score += (
        weights["demand_fit"]
        * demand_fit
    )

    additive_score += (
        weights["capability_fit"]
        * capability_fit
    )

    additive_score += (
        weights["completion_pressure"]
        * completion_pressure
    )

    additive_score += (
        weights["logistics_pressure"]
        * logistics_pressure
    )

    additive_score += (
        weights["distance_log"]
        * distance_log
    )

    additive_score += np.where(
        frame["urgency_level"] == "HIGH",
        weights["urgency_high"],
        0.0,
    )

    additive_score += np.where(
        frame["urgency_level"] == "CRITICAL",
        weights["urgency_critical"],
        0.0,
    )

    additive_score += np.where(
        frame["seasonality_status"] == "POST_SEASON",
        weights["post_season"],
        0.0,
    )

    action_offsets = (
        frame["action_type"]
        .map(recipe.action_offsets)
        .fillna(0.0)
        .astype(float)
    )

    additive_score += action_offsets

    # --------------------------------------------------------
    # Frozen nonlinear thresholds from outcome.py v1.0
    #
    # Coefficients are NOT duplicated here. They are loaded
    # from the canonical recipe configuration.
    # --------------------------------------------------------

    strong_demand = (
        (demand_fit >= 0.80)
        & (capability_fit >= 0.65)
    )

    weak_demand = (
        demand_fit <= 0.30
    )

    urgent_short_window = (
        frame["urgency_level"].isin(
            ["HIGH", "CRITICAL"]
        )
        & (completion_pressure >= 0.60)
    )

    long_distance_fragile = (
        (distance_km >= 20.0)
        & frame["storage_requirement_mode"].isin(
            [
                "COLD_REQUIRED_FOR_QUALITY_WINDOW",
                "SAFETY_CRITICAL_COLD_CHAIN",
            ]
        )
    )

    nonlinear = recipe.nonlinear

    nonlinear_contribution = (
        strong_demand.astype(float)
        * nonlinear["strong_demand_bonus"]
        + weak_demand.astype(float)
        * nonlinear["weak_demand_penalty"]
        + urgent_short_window.astype(float)
        * nonlinear[
            "urgent_short_window_penalty"
        ]
        + long_distance_fragile.astype(float)
        * nonlinear[
            "long_distance_fragile_penalty"
        ]
    )

    full_score = (
        additive_score
        + nonlinear_contribution
    )

    reconstructed_probability = (
        _sigmoid(full_score)
        .clip(
            lower=recipe.probability_bounds.minimum,
            upper=recipe.probability_bounds.maximum,
        )
    )

    oracle_probability = frame[
        "generator_success_probability"
    ].astype(float)

    reconstruction_error = (
        reconstructed_probability
        - oracle_probability
    ).abs()

    max_reconstruction_error = float(
        reconstruction_error.max()
    )

    if max_reconstruction_error > 1e-10:
        raise RuntimeError(
            "Diagnostic reconstruction does not match "
            "the frozen oracle. "
            f"Max abs error={max_reconstruction_error}"
        )

    # --------------------------------------------------------
    # Empirical frozen-dataset invariants
    # --------------------------------------------------------

    completion_safe_violations = int(
        (
            frame["estimated_completion_hours"]
            > frame["remaining_safe_window_hours"]
        ).sum()
    )

    max_completion_ratio = float(
        completion_ratio.max()
    )

    max_completion_pressure = float(
        completion_pressure.max()
    )

    # --------------------------------------------------------
    # Context by split
    # --------------------------------------------------------

    trigger_masks = {
        "strong_demand_bonus": strong_demand,
        "weak_demand_penalty": weak_demand,
        "urgent_short_window_penalty": (
            urgent_short_window
        ),
        "long_distance_fragile_penalty": (
            long_distance_fragile
        ),
    }

    split_results: dict[str, object] = {}

    for split_name in (
        "train",
        "validation",
    ):
        mask = frame["split"] == split_name
        split_frame = frame.loc[mask].copy()

        split_nonlinear = (
            nonlinear_contribution.loc[mask]
        )

        split_additive = (
            additive_score.loc[mask]
        )

        split_full = full_score.loc[mask]

        positive_prevalence = float(
            split_frame[
                "simulated_rescue_outcome"
            ].mean()
        )

        trigger_results: dict[
            str,
            dict[str, float | int],
        ] = {}

        for name, trigger_mask in (
            trigger_masks.items()
        ):
            local = trigger_mask.loc[mask]

            trigger_results[name] = {
                "rows": int(local.sum()),
                "rate": float(local.mean()),
                "coefficient": float(
                    nonlinear[name]
                ),
            }

        any_nonlinear = (
            split_nonlinear != 0.0
        )

        additive_top = _top_candidate_ids(
            split_frame.assign(
                additive_score=split_additive,
            ),
            "additive_score",
        )

        full_top = _top_candidate_ids(
            split_frame.assign(
                full_score=split_full,
            ),
            "full_score",
        )

        common_groups = additive_top.index.intersection(
            full_top.index
        )

        top1_flip_rate = float(
            (
                additive_top.loc[common_groups]
                != full_top.loc[common_groups]
            ).mean()
        )

        split_results[split_name] = {
            "rows": int(len(split_frame)),
            "scenario_groups": int(
                split_frame[
                    "scenario_group_id"
                ].nunique()
            ),
            "positive_prevalence": (
                positive_prevalence
            ),
            "uninformative_pr_auc_baseline": (
                positive_prevalence
            ),
            "uniform_random_top1_expectation": (
                _uniform_random_top1_expectation(
                    split_frame
                )
            ),
            "nonlinear_triggers": trigger_results,
            "rows_with_nonzero_nonlinear_term": int(
                any_nonlinear.sum()
            ),
            "nonlinear_row_rate": float(
                any_nonlinear.mean()
            ),
            "mean_nonlinear_contribution": float(
                split_nonlinear.mean()
            ),
            "mean_abs_nonlinear_contribution": float(
                split_nonlinear.abs().mean()
            ),
            "p95_abs_nonlinear_contribution": float(
                split_nonlinear.abs().quantile(
                    0.95
                )
            ),
            "nonlinear_contribution_std": float(
                split_nonlinear.std(ddof=0)
            ),
            "additive_score_std": float(
                split_additive.std(ddof=0)
            ),
            "additive_vs_full_rank_correlation": (
                _rank_correlation(
                    split_additive,
                    split_full,
                )
            ),
            "top1_changed_by_nonlinear_terms_rate": (
                top1_flip_rate
            ),
        }

    # --------------------------------------------------------
    # Existing model/baseline context from evidence artifacts
    # --------------------------------------------------------

    baseline_metrics = json.loads(
        BASELINE_METRICS_PATH.read_text(
            encoding="utf-8"
        )
    )

    lr_metrics = json.loads(
        LR_METRICS_PATH.read_text(
            encoding="utf-8"
        )
    )

    hgb_metrics = json.loads(
        HGB_METRICS_PATH.read_text(
            encoding="utf-8"
        )
    )

    report = {
        "report_version": "1.0.0",
        "benchmark_scope": (
            "Frozen synthetic benchmark diagnostic only."
        ),
        "test_accessed": False,
        "recipe_version": recipe.recipe_version,
        "oracle_reconstruction": {
            "max_absolute_probability_error": (
                max_reconstruction_error
            ),
            "status": "PASS",
        },
        "empirical_invariants": {
            "completion_exceeds_safe_window_rows": (
                completion_safe_violations
            ),
            "maximum_completion_to_safe_window_ratio": (
                max_completion_ratio
            ),
            "maximum_completion_pressure": (
                max_completion_pressure
            ),
            "urgent_short_window_rule_reachable": bool(
                urgent_short_window.any()
            ),
        },
        "splits": split_results,
        "validation_model_context": {
            "B0": baseline_metrics[
                "baselines"
            ]["B0"],
            "B1": baseline_metrics[
                "baselines"
            ]["B1"],
            "LR": lr_metrics,
            "HGB": hgb_metrics,
        },
        "epistemic_boundary": {
            "confirmed": [
                "Additive logistic core exists.",
                "Sparse threshold nonlinearities exist.",
                "Bernoulli outcome sampling exists.",
                (
                    "Oracle reconstruction matches the "
                    "frozen generator output."
                ),
            ],
            "not_yet_proven": [
                (
                    "HGB overfit is primarily caused by "
                    "Bernoulli realization noise."
                ),
                (
                    "Additive generator structure is the "
                    "primary causal reason LR ranks better."
                ),
            ],
        },
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print("=== Frozen Benchmark Context Audit ===")
    print(
        "Oracle reconstruction error : "
        f"{max_reconstruction_error:.12f}"
    )
    print(
        "Completion > safe window    : "
        f"{completion_safe_violations}"
    )
    print(
        "Max completion ratio        : "
        f"{max_completion_ratio:.6f}"
    )
    print(
        "Max completion pressure     : "
        f"{max_completion_pressure:.6f}"
    )
    print(
        "Urgent-short rule reachable : "
        f"{bool(urgent_short_window.any())}"
    )

    for split_name in (
        "train",
        "validation",
    ):
        result = split_results[split_name]
        assert isinstance(result, dict)

        print()
        print(
            f"=== {split_name.upper()} ==="
        )
        print(
            "Positive prevalence        : "
            f"{result['positive_prevalence']:.6f}"
        )
        print(
            "Uninformative PR baseline  : "
            f"{result['uninformative_pr_auc_baseline']:.6f}"
        )
        print(
            "Uniform random Top-1       : "
            f"{result['uniform_random_top1_expectation']:.6f}"
        )
        print(
            "Rows with nonlinear term   : "
            f"{result['nonlinear_row_rate']:.4%}"
        )
        print(
            "Mean |nonlinear|           : "
            f"{result['mean_abs_nonlinear_contribution']:.6f}"
        )
        print(
            "Additive/full rank corr    : "
            f"{result['additive_vs_full_rank_correlation']:.6f}"
        )
        print(
            "Top-1 changed by nonlinear : "
            f"{result['top1_changed_by_nonlinear_terms_rate']:.4%}"
        )

        trigger_results = result[
            "nonlinear_triggers"
        ]
        assert isinstance(
            trigger_results,
            dict,
        )

        print("Nonlinear triggers:")

        for name, payload in (
            trigger_results.items()
        ):
            assert isinstance(
                payload,
                dict,
            )

            print(
                f"  {name:<34}"
                f"{payload['rows']:>5} rows "
                f"({payload['rate']:.4%}) "
                f"coef={payload['coefficient']:+.2f}"
            )

    print()
    print(f"Evidence: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
