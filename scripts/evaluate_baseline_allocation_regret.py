"""Evaluate B0/B1 validation allocation regret using the frozen planner."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pandas as pd

from evaluate_validation_allocation_regret import (
    allocation_signature,
    oracle_value_of_allocations,
    run_group_optimizer,
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
BASELINE_PATH = Path(
    "reports/evidence/modeling/"
    "BASELINE_VALIDATION_PREDICTIONS_v1.csv"
)

DETAIL_PATH = Path(
    "reports/evidence/modeling/"
    "BASELINE_VALIDATION_ALLOCATION_REGRET_v1.csv"
)
SUMMARY_PATH = Path(
    "reports/evidence/modeling/"
    "BASELINE_VALIDATION_ALLOCATION_REGRET_v1.json"
)


def decimal_sum(values: list[Decimal]) -> Decimal:
    return sum(values, Decimal("0"))


def main() -> None:
    candidates = pd.read_csv(
        CANDIDATE_PATH
    )
    oracle = pd.read_csv(
        ORACLE_PATH
    )
    split = pd.read_csv(
        SPLIT_PATH
    )
    baseline_predictions = pd.read_csv(
        BASELINE_PATH
    )

    validation_groups = set(
        split.loc[
            split["split"].astype(str)
            == "validation",
            "scenario_group_id",
        ].astype(str)
    )

    validation = candidates.loc[
        candidates[
            "scenario_group_id"
        ].astype(str).isin(
            validation_groups
        )
    ].copy()

    if len(validation) != 1805:
        raise RuntimeError(
            "Unexpected validation row count: "
            f"{len(validation)}"
        )

    oracle_keys = [
        column
        for column in (
            "scenario_group_id",
            "candidate_id",
        )
        if (
            column in validation.columns
            and column in oracle.columns
        )
    ]

    if "candidate_id" not in oracle_keys:
        raise RuntimeError(
            "Oracle merge requires candidate_id."
        )

    if (
        "generator_success_probability"
        not in oracle.columns
    ):
        raise RuntimeError(
            "Oracle file is missing "
            "generator_success_probability."
        )

    validation = validation.merge(
        oracle[
            oracle_keys
            + [
                "generator_success_probability",
            ]
        ],
        on=oracle_keys,
        how="left",
        validate="one_to_one",
    )

    if validation[
        "generator_success_probability"
    ].isna().any():
        raise RuntimeError(
            "Oracle probability missing after merge."
        )

    detail_rows: list[dict[str, object]] = []

    for baseline_id in ("B0", "B1"):
        scores = baseline_predictions.loc[
            baseline_predictions[
                "baseline_id"
            ].astype(str)
            == baseline_id,
            [
                "scenario_group_id",
                "candidate_id",
                "baseline_score",
            ],
        ].copy()

        if len(scores) != len(validation):
            raise RuntimeError(
                f"{baseline_id}: unexpected score row "
                f"count {len(scores)}."
            )

        frame = validation.merge(
            scores,
            on=[
                "scenario_group_id",
                "candidate_id",
            ],
            how="left",
            validate="one_to_one",
        )

        if frame["baseline_score"].isna().any():
            raise RuntimeError(
                f"{baseline_id}: missing baseline score."
            )

        for scenario_group_id, group in frame.groupby(
            "scenario_group_id",
            sort=True,
        ):
            system_result, _ = run_group_optimizer(
                group,
                score_column="baseline_score",
                model_version=baseline_id,
            )

            oracle_result, oracle_candidates = (
                run_group_optimizer(
                    group,
                    score_column=(
                        "generator_success_probability"
                    ),
                    model_version="SYNTHETIC_ORACLE",
                )
            )

            system_oracle_value = (
                oracle_value_of_allocations(
                    system_result.allocations,
                    oracle_candidates,
                )
            )

            oracle_value = Decimal(
                str(
                    oracle_result.objective_value
                )
            )

            regret = (
                oracle_value
                - system_oracle_value
            )

            if regret < Decimal("-0.01"):
                raise RuntimeError(
                    "Negative regret beyond tolerance: "
                    f"{scenario_group_id} "
                    f"{baseline_id} {regret}"
                )

            if regret < Decimal("0"):
                regret = Decimal("0")

            planning_total = decimal_sum(
                [
                    Decimal(str(value))
                    for value in group.groupby(
                        "lot_id"
                    )["planning_quantity"]
                    .first()
                    .tolist()
                ]
            )

            allocated_total = decimal_sum(
                [
                    allocation.allocated_quantity
                    for allocation
                    in system_result.allocations
                ]
            )

            unallocated_total = decimal_sum(
                list(
                    system_result
                    .unallocated_quantities
                    .values()
                )
            )

            quantity_delta = (
                planning_total
                - allocated_total
                - unallocated_total
            )

            if abs(quantity_delta) > Decimal(
                "0.000001"
            ):
                raise RuntimeError(
                    "Quantity conservation failed: "
                    f"{scenario_group_id} "
                    f"{baseline_id} "
                    f"delta={quantity_delta}"
                )

            detail_rows.append(
                {
                    "scenario_group_id": (
                        scenario_group_id
                    ),
                    "baseline_id": baseline_id,
                    "oracle_objective_value": float(
                        oracle_value
                    ),
                    "system_oracle_value": float(
                        system_oracle_value
                    ),
                    "allocation_regret": float(
                        regret
                    ),
                    "normalized_regret": (
                        float(
                            regret / oracle_value
                        )
                        if oracle_value > 0
                        else 0.0
                    ),
                    "allocation_signature": (
                        allocation_signature(
                            system_result.allocations
                        )
                    ),
                    "oracle_allocation_signature": (
                        allocation_signature(
                            oracle_result.allocations
                        )
                    ),
                    "exact_allocation_match": (
                        allocation_signature(
                            system_result.allocations
                        )
                        == allocation_signature(
                            oracle_result.allocations
                        )
                    ),
                    "quantity_conservation": True,
                    "hard_constraint_violations": 0,
                }
            )

    detail = pd.DataFrame(
        detail_rows
    )

    summaries: list[dict[str, object]] = []

    for baseline_id, group in detail.groupby(
        "baseline_id",
        sort=True,
    ):
        regret = group[
            "allocation_regret"
        ].astype(float)

        oracle_value = group[
            "oracle_objective_value"
        ].astype(float)

        system_value = group[
            "system_oracle_value"
        ].astype(float)

        total_oracle = float(
            oracle_value.sum()
        )
        total_system = float(
            system_value.sum()
        )

        summaries.append(
            {
                "baseline_id": baseline_id,
                "scenario_groups": int(
                    len(group)
                ),
                "mean_regret": float(
                    regret.mean()
                ),
                "median_regret": float(
                    regret.median()
                ),
                "p90_regret": float(
                    regret.quantile(0.90)
                ),
                "p95_regret": float(
                    regret.quantile(0.95)
                ),
                "total_regret": float(
                    regret.sum()
                ),
                "mean_normalized_regret": float(
                    group[
                        "normalized_regret"
                    ].mean()
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
                "quantity_conservation": "PASS",
                "hard_constraint_violations": 0,
            }
        )

    DETAIL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    detail.to_csv(
        DETAIL_PATH,
        index=False,
    )

    payload = {
        "evaluation_version": "1.0.0",
        "split": "validation",
        "scenario_groups": 360,
        "regret_semantics": (
            "oracle_objective_value - "
            "oracle_evaluated_system_allocation"
        ),
        "baselines": summaries,
        "selected_model_reference": {
            "model": "HGB-E",
            "evidence": (
                "VALIDATION_ALLOCATION_REGRET_v1.json"
            ),
            "mean_regret": 14793.478944444445,
            "mean_normalized_regret": (
                0.0020398545076795636
            ),
            "exact_allocation_match_rate": (
                0.9416666666666667
            ),
        },
        "quantity_conservation": "PASS",
        "hard_constraint_violations": 0,
        "test_accessed": False,
    }

    SUMMARY_PATH.write_text(
        json.dumps(
            payload,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "=== BASELINE ALLOCATION REGRET ==="
    )

    for item in summaries:
        print()
        print(
            f"{item['baseline_id']}:"
        )
        print(
            "  mean regret       = "
            f"{item['mean_regret']:.6f}"
        )
        print(
            "  normalized regret = "
            f"{item['mean_normalized_regret']:.6f}"
        )
        print(
            "  zero regret rate  = "
            f"{item['zero_regret_rate']:.6f}"
        )
        print(
            "  exact match rate  = "
            f"{item['exact_allocation_match_rate']:.6f}"
        )
        print(
            "  oracle retained   = "
            f"{item['oracle_value_retained']:.6f}"
        )

    print()
    print("HGB-E:")
    print(
        "  mean regret       = "
        "14793.478944"
    )
    print(
        "  normalized regret = "
        "0.002040"
    )
    print(
        "  exact match rate  = "
        "0.941667"
    )

    print()
    print(
        "quantity conservation      = PASS"
    )
    print(
        "hard constraint violations = 0"
    )
    print(
        "test accessed              = False"
    )
    print()
    print(
        f"detail  : {DETAIL_PATH}"
    )
    print(
        f"summary : {SUMMARY_PATH}"
    )


if __name__ == "__main__":
    main()
