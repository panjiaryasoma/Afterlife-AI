"""Validation-only allocation regret for selected model challengers."""

from __future__ import annotations

import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    CoverageStatus,
    FeasibilityStatus,
    MatchStatus,
    ModelScoringStatus,
    SafetyStatus,
    SolverStatus,
    ValidationStatus,
    VerificationStatus,
)
from afterlife_ai.modeling.hist_gradient import (
    fit_hist_gradient_boosting,
    load_hist_gradient_config,
)
from afterlife_ai.modeling.training import (
    fit_logistic_regression,
    load_modeling_config,
)
from afterlife_ai.planner.optimizer import (
    MONEY_QUANTUM,
    OPTIMIZER_VALUE_QUANTUM,
    OptimizationAllocation,
    OptimizationResult,
    optimize_with_cp_sat,
)
from afterlife_ai.planner.value import (
    ExpectedValueInput,
    calculate_expected_value,
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
ORACLE_PATH = Path(
    "data/generated/synthetic_oracle_v2.csv"
)
SPLIT_PATH = Path(
    "reports/evidence/synthetic_dataset/"
    "SPLIT_GROUPS_v2.csv"
)
ABLATION_PATH = Path(
    "reports/evidence/modeling/"
    "HGB_ABLATION_VALIDATION_v1.csv"
)
LR_ARTIFACT_PATH = Path(
    "reports/evidence/modeling/"
    "LOGISTIC_VALIDATION_PREDICTIONS_v1.csv"
)

OUTPUT_DIR = Path(
    "reports/evidence/modeling"
)
DETAIL_PATH = (
    OUTPUT_DIR
    / "VALIDATION_ALLOCATION_REGRET_v1.csv"
)
SUMMARY_PATH = (
    OUTPUT_DIR
    / "VALIDATION_ALLOCATION_REGRET_v1.json"
)
SCORE_PATH = (
    OUTPUT_DIR
    / "VALIDATION_MODEL_SELECTION_SCORES_v1.csv"
)

ZERO = Decimal("0")
ONE = Decimal("1")


def decimal_value(value: object) -> Decimal:
    """Convert scalar data to Decimal without binary-float inheritance."""

    return Decimal(str(value))


def maximum_feasible_quantity(
    row: pd.Series,
) -> Decimal:
    """Recover the frozen synthetic candidate quantity contract."""

    return min(
        decimal_value(row["planning_quantity"]),
        decimal_value(row["active_demand_quantity"]),
        decimal_value(row["available_capacity"]),
    )


def build_valued_candidate(
    row: pd.Series,
    *,
    probability: Decimal,
    model_version: str,
) -> CandidateAction:
    """Adapt one frozen synthetic row to the production optimizer contract."""

    quantity = maximum_feasible_quantity(row)

    if quantity <= ZERO:
        raise ValueError(
            "Synthetic model-eligible candidate harus "
            "memiliki positive feasible quantity."
        )

    direct_cost = decimal_value(
        row["direct_action_cost"]
    )
    logistics_cost = decimal_value(
        row["logistics_cost"]
    )
    handling_cost = decimal_value(
        row["handling_cost"]
    )

    value_result = calculate_expected_value(
        ExpectedValueInput(
            rescue_probability=probability,
            quantity=quantity,
            cash_recovery_per_unit=decimal_value(
                row[
                    "offered_or_selling_price_per_unit"
                ]
            ),
            future_branch_recovery_per_unit=ZERO,
            avoided_purchase_cost_per_unit=ZERO,
            direct_action_cost_per_unit=(
                direct_cost / quantity
            ),
            logistics_cost_per_unit=(
                logistics_cost / quantity
            ),
            handling_cost_per_unit=(
                handling_cost / quantity
            ),
            failure_penalty_per_unit=ZERO,
        )
    )

    return CandidateAction(
        candidate_id=str(row["candidate_id"]),
        planning_lot_id=str(row["lot_id"]),
        action_type=ActionType(
            str(row["action_type"])
        ),
        destination_id=None,
        destination_type=str(
            row["destination_type"]
        ),
        maximum_feasible_quantity=quantity,
        offered_or_selling_price_per_unit=(
            decimal_value(
                row[
                    "offered_or_selling_price_per_unit"
                ]
            )
        ),
        direct_action_cost=direct_cost,
        logistics_cost=logistics_cost,
        handling_cost=handling_cost,
        estimated_completion_hours=decimal_value(
            row["estimated_completion_hours"]
        ),
        active_demand_quantity=decimal_value(
            row["active_demand_quantity"]
        ),
        available_capacity=decimal_value(
            row["available_capacity"]
        ),
        minimum_order_quantity=decimal_value(
            row["minimum_order_quantity"]
        ),
        capability_resource_ratio=decimal_value(
            row["capability_resource_ratio"]
        ),
        demand_coverage_ratio=decimal_value(
            row["demand_coverage_ratio"]
        ),
        demand_freshness_hours=decimal_value(
            row["demand_freshness_hours"]
        ),
        distance_km=decimal_value(
            row["distance_km"]
        ),
        category_match_status=MatchStatus.MATCH,
        package_size_match_status=MatchStatus.MATCH,
        customer_segment_match_status=MatchStatus.MATCH,
        storage_compatibility_status=MatchStatus.MATCH,
        validation_status=ValidationStatus.PASSED,
        coverage_status=CoverageStatus.SUPPORTED,
        safety_status=SafetyStatus.ACCEPTABLE,
        verification_status=VerificationStatus.VERIFIED,
        feasibility_status=FeasibilityStatus.FEASIBLE,
        model_scoring_status=ModelScoringStatus.ALLOWED,
        rejection_reason_codes=[],
        fixture_rescue_success_score=None,
        estimated_rescue_success_score=probability,
        model_version=model_version,
        expected_cash_recovery=(
            value_result.expected_cash_recovery
        ),
        expected_future_branch_recovery=(
            value_result.expected_future_branch_recovery
        ),
        expected_avoided_purchase_cost=(
            value_result.expected_avoided_purchase_cost
        ),
        expected_physical_rescue_quantity=(
            value_result.expected_physical_rescue_quantity
        ),
        expected_waste_quantity=(
            value_result.expected_waste_quantity
        ),
        expected_net_recovery=(
            value_result.expected_net_recovery
        ),
    )


def run_group_optimizer(
    group: pd.DataFrame,
    *,
    score_column: str,
    model_version: str,
) -> tuple[
    OptimizationResult,
    list[CandidateAction],
]:
    """Run the production CP-SAT contract for one synthetic scenario."""

    candidates: list[CandidateAction] = []

    action_minimums: dict[
        ActionType,
        Decimal,
    ] = {}

    for _, row in group.iterrows():
        probability = decimal_value(
            row[score_column]
        )

        candidate = build_valued_candidate(
            row,
            probability=probability,
            model_version=model_version,
        )

        candidates.append(candidate)

        action_type = candidate.action_type

        if action_type in action_minimums:
            raise RuntimeError(
                "Duplicate action type ditemukan dalam "
                "scenario group; MOQ adapter tidak valid."
            )

        action_minimums[action_type] = (
            decimal_value(
                row["minimum_order_quantity"]
            )
        )

    lot_ids = {
        str(value)
        for value in group["lot_id"]
    }

    if len(lot_ids) != 1:
        raise RuntimeError(
            "Validation benchmark mengharapkan "
            "tepat satu lot per scenario group."
        )

    planning_quantities = {
        next(iter(lot_ids)): decimal_value(
            group["planning_quantity"].iloc[0]
        )
    }

    result = optimize_with_cp_sat(
        candidates=candidates,
        planning_quantities=planning_quantities,
        shared_action_minimum_quantities=(
            action_minimums
        ),
    )

    if result.solver_status not in {
        SolverStatus.OPTIMAL,
        SolverStatus.FEASIBLE,
    }:
        raise RuntimeError(
            "Optimizer gagal pada "
            f"{group['scenario_group_id'].iloc[0]}: "
            f"{result.solver_status}"
        )

    return result, candidates


def oracle_value_of_allocations(
    allocations: list[OptimizationAllocation],
    oracle_candidates: list[CandidateAction],
) -> Decimal:
    """Evaluate a fixed system allocation with oracle probabilities."""

    candidate_map = {
        candidate.candidate_id: candidate
        for candidate in oracle_candidates
    }

    total = ZERO

    for allocation in allocations:
        candidate = candidate_map[
            allocation.candidate_id
        ]

        oracle_per_unit = (
            candidate.expected_net_recovery
            / candidate.maximum_feasible_quantity
        ).quantize(
            OPTIMIZER_VALUE_QUANTUM,
            rounding=ROUND_HALF_UP,
        )

        allocation_value = (
            allocation.allocated_quantity
            * oracle_per_unit
        ).quantize(
            MONEY_QUANTUM,
            rounding=ROUND_HALF_UP,
        )

        total += allocation_value

    return total.quantize(
        MONEY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def allocation_signature(
    allocations: list[OptimizationAllocation],
) -> tuple[tuple[str, str], ...]:
    """Canonical candidate/quantity allocation signature."""

    return tuple(
        sorted(
            (
                allocation.candidate_id,
                str(allocation.allocated_quantity),
            )
            for allocation in allocations
        )
    )


def verify_reproduced_metrics(
    validation: pd.DataFrame,
    *,
    score_columns: dict[str, str],
) -> None:
    """Guard against accidentally changing Step-D model definitions."""

    ablation = pd.read_csv(ABLATION_PATH)

    target = validation[
        "simulated_rescue_outcome"
    ].astype(int)

    for model_name, score_column in (
        score_columns.items()
    ):
        scores = validation[
            score_column
        ].astype(float)

        observed_pr = average_precision_score(
            target,
            scores,
        )
        observed_brier = brier_score_loss(
            target,
            scores,
        )

        evidence_row = ablation.loc[
            ablation["model"] == model_name
        ]

        if len(evidence_row) != 1:
            raise RuntimeError(
                f"Step-D evidence untuk {model_name} "
                "tidak unik."
            )

        expected_pr = float(
            evidence_row[
                "validation_pr_auc"
            ].iloc[0]
        )
        expected_brier = float(
            evidence_row[
                "validation_brier"
            ].iloc[0]
        )

        if abs(observed_pr - expected_pr) > 5e-6:
            raise RuntimeError(
                f"{model_name} PR-AUC tidak mereproduksi "
                "Step D: "
                f"{observed_pr:.9f} != {expected_pr:.9f}"
            )

        if (
            abs(observed_brier - expected_brier)
            > 5e-6
        ):
            raise RuntimeError(
                f"{model_name} Brier tidak mereproduksi "
                "Step D: "
                f"{observed_brier:.9f} "
                f"!= {expected_brier:.9f}"
            )

        print(
            f"{model_name:<6} "
            f"PR-AUC={observed_pr:.6f} "
            f"Brier={observed_brier:.6f}"
        )


def summarize_regret(
    detail: pd.DataFrame,
) -> dict[str, object]:
    """Create model-level regret evidence."""

    summary_rows: list[dict[str, object]] = []

    for model_name, frame in detail.groupby(
        "model",
        sort=True,
    ):
        regret = frame["regret"].astype(float)

        normalized = frame[
            "normalized_regret"
        ].dropna().astype(float)

        oracle_total = float(
            frame["oracle_objective_value"].sum()
        )
        system_total = float(
            frame["system_oracle_value"].sum()
        )

        value_retained = (
            system_total / oracle_total
            if oracle_total > 0
            else None
        )

        summary_rows.append(
            {
                "model": model_name,
                "scenario_groups": int(len(frame)),
                "mean_regret": float(
                    regret.mean()
                ),
                "median_regret": float(
                    regret.median()
                ),
                "p90_regret": float(
                    np.quantile(regret, 0.90)
                ),
                "p95_regret": float(
                    np.quantile(regret, 0.95)
                ),
                "total_regret": float(
                    regret.sum()
                ),
                "mean_normalized_regret": (
                    float(normalized.mean())
                    if len(normalized)
                    else None
                ),
                "zero_regret_rate": float(
                    (regret <= 0.01).mean()
                ),
                "exact_allocation_match_rate": float(
                    frame[
                        "exact_allocation_match"
                    ].mean()
                ),
                "oracle_value_total": oracle_total,
                "system_oracle_value_total": (
                    system_total
                ),
                "economic_value_retained_ratio": (
                    value_retained
                ),
                "negative_true_value_groups": int(
                    (
                        frame["system_oracle_value"]
                        < 0
                    ).sum()
                ),
            }
        )

    summary_rows.sort(
        key=lambda row: cast(
            float,
            row["mean_regret"],
        )
    )

    return {
        "evaluation_version": "1.0.0",
        "split": "validation",
        "test_accessed": False,
        "regret_semantics": (
            "oracle_objective_value "
            "- oracle_evaluated_system_allocation"
        ),
        "optimizer": "production_cp_sat",
        "cost_semantics": (
            "candidate total costs amortized across "
            "maximum feasible quantity before "
            "expected-value calculation"
        ),
        "models": summary_rows,
    }


def main() -> None:
    """Run validation allocation-regret evaluation."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    modeling_config = load_modeling_config(
        MODELING_CONFIG_PATH
    )
    base_hgb_config = load_hist_gradient_config(
        MODELING_CONFIG_PATH
    )
    contract = load_model_feature_contract(
        SCHEMA_PATH
    )

    candidate = pd.read_csv(
        CANDIDATE_PATH
    )
    oracle = pd.read_csv(
        ORACLE_PATH
    )
    assignments = pd.read_csv(
        SPLIT_PATH
    )

    modeling = candidate.merge(
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

    if modeling["split"].isna().any():
        raise RuntimeError(
            "Ada candidate tanpa split assignment."
        )

    train = modeling.loc[
        modeling["split"] == "train"
    ].copy()

    validation = modeling.loc[
        modeling["split"] == "validation"
    ].copy()

    if set(train["split"].astype(str)) != {
        "train"
    }:
        raise RuntimeError(
            "Train isolation gagal."
        )

    if set(validation["split"].astype(str)) != {
        "validation"
    }:
        raise RuntimeError(
            "Validation isolation gagal."
        )

    if len(train) != 8435:
        raise RuntimeError(
            f"Unexpected train rows: {len(train)}"
        )

    if len(validation) != 1805:
        raise RuntimeError(
            "Unexpected validation rows: "
            f"{len(validation)}"
        )

    if (
        validation["scenario_group_id"].nunique()
        != 360
    ):
        raise RuntimeError(
            "Unexpected validation group count."
        )

    validation = validation.merge(
        oracle[
            [
                "scenario_group_id",
                "candidate_id",
                "generator_success_probability",
            ]
        ],
        on=[
            "scenario_group_id",
            "candidate_id",
        ],
        how="left",
        validate="one_to_one",
    )

    if (
        validation[
            "generator_success_probability"
        ].isna().any()
    ):
        raise RuntimeError(
            "Oracle probability tidak lengkap."
        )

    print("=== FIT MODELS ===")

    lr_model = fit_logistic_regression(
        train,
        contract=contract,
        config=(
            modeling_config.logistic_regression
        ),
    )

    hgb_b_config = (
        base_hgb_config.model_copy(
            update={
                "max_iter": 100,
                "max_leaf_nodes": 15,
                "min_samples_leaf": 20,
                "l2_regularization": 1.0,
            }
        )
    )

    hgb_e_config = (
        base_hgb_config.model_copy(
            update={
                "max_iter": 150,
                "max_leaf_nodes": 7,
                "min_samples_leaf": 40,
                "l2_regularization": 2.0,
            }
        )
    )

    hgb_b_model = fit_hist_gradient_boosting(
        train,
        contract=contract,
        config=hgb_b_config,
    )

    hgb_e_model = fit_hist_gradient_boosting(
        train,
        contract=contract,
        config=hgb_e_config,
    )

    features = validation[
        contract.model_features
    ]

    validation["LR"] = (
        lr_model.pipeline.predict_proba(
            features
        )[:, 1]
    )

    validation["HGB_B"] = (
        hgb_b_model.pipeline.predict_proba(
            features
        )[:, 1]
    )

    validation["HGB_E"] = (
        hgb_e_model.pipeline.predict_proba(
            features
        )[:, 1]
    )

    print()
    print("=== REPRODUCTION CHECK ===")

    verify_reproduced_metrics(
        validation,
        score_columns={
            "LR": "LR",
            "HGB_B": "HGB_B",
            "HGB_E": "HGB_E",
        },
    )

    lr_artifact = pd.read_csv(
        LR_ARTIFACT_PATH
    )

    lr_check = validation[
        [
            "candidate_id",
            "LR",
        ]
    ].merge(
        lr_artifact[
            [
                "candidate_id",
                "model_score",
            ]
        ],
        on="candidate_id",
        how="inner",
        validate="one_to_one",
    )

    lr_max_abs_diff = float(
        (
            lr_check["LR"]
            - lr_check["model_score"]
        )
        .abs()
        .max()
    )

    print(
        "LR artifact max abs diff: "
        f"{lr_max_abs_diff:.12g}"
    )

    if lr_max_abs_diff > 1e-10:
        raise RuntimeError(
            "LR scoring tidak identik dengan "
            "validation artifact."
        )

    validation[
        [
            "scenario_group_id",
            "candidate_id",
            "action_type",
            "simulated_rescue_outcome",
            "LR",
            "HGB_B",
            "HGB_E",
            "generator_success_probability",
        ]
    ].to_csv(
        SCORE_PATH,
        index=False,
    )

    print()
    print("=== ALLOCATION REGRET ===")

    detail_rows: list[
        dict[str, object]
    ] = []

    grouped = validation.groupby(
        "scenario_group_id",
        sort=True,
    )

    for group_index, (
        scenario_group_id,
        group,
    ) in enumerate(grouped, start=1):
        oracle_result, oracle_candidates = (
            run_group_optimizer(
                group,
                score_column=(
                    "generator_success_probability"
                ),
                model_version="SYNTHETIC_ORACLE_v2",
            )
        )

        oracle_objective = (
            oracle_result.objective_value
        )

        oracle_signature = allocation_signature(
            oracle_result.allocations
        )

        for model_name in [
            "HGB_E",
            "HGB_B",
            "LR",
        ]:
            model_result, _ = (
                run_group_optimizer(
                    group,
                    score_column=model_name,
                    model_version=model_name,
                )
            )

            system_oracle_value = (
                oracle_value_of_allocations(
                    model_result.allocations,
                    oracle_candidates,
                )
            )

            raw_regret = (
                oracle_objective
                - system_oracle_value
            )

            if raw_regret < Decimal("-0.01"):
                raise RuntimeError(
                    "System allocation melampaui oracle "
                    f"pada {scenario_group_id}: "
                    f"{raw_regret}"
                )

            regret = max(
                ZERO,
                raw_regret,
            ).quantize(
                MONEY_QUANTUM,
                rounding=ROUND_HALF_UP,
            )

            normalized_regret: float | None

            if oracle_objective > ZERO:
                normalized_regret = float(
                    regret / oracle_objective
                )
            elif regret == ZERO:
                normalized_regret = 0.0
            else:
                normalized_regret = None

            detail_rows.append(
                {
                    "scenario_group_id": (
                        scenario_group_id
                    ),
                    "model": model_name,
                    "candidate_rows": len(group),
                    "planning_quantity": float(
                        group[
                            "planning_quantity"
                        ].iloc[0]
                    ),
                    "model_objective_value": float(
                        model_result.objective_value
                    ),
                    "oracle_objective_value": float(
                        oracle_objective
                    ),
                    "system_oracle_value": float(
                        system_oracle_value
                    ),
                    "regret": float(regret),
                    "normalized_regret": (
                        normalized_regret
                    ),
                    "exact_allocation_match": (
                        allocation_signature(
                            model_result.allocations
                        )
                        == oracle_signature
                    ),
                    "system_allocation_count": len(
                        model_result.allocations
                    ),
                    "oracle_allocation_count": len(
                        oracle_result.allocations
                    ),
                }
            )

        if (
            group_index % 60 == 0
            or group_index == 360
        ):
            print(
                f"processed {group_index}/360 groups"
            )

    detail = pd.DataFrame(
        detail_rows
    )

    detail.to_csv(
        DETAIL_PATH,
        index=False,
    )

    summary = summarize_regret(
        detail
    )

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
    print("=== RESULT ===")

    result_table = pd.DataFrame(
        summary["models"]
    )

    columns = [
        "model",
        "mean_regret",
        "median_regret",
        "p95_regret",
        "mean_normalized_regret",
        "exact_allocation_match_rate",
        "economic_value_retained_ratio",
    ]

    print(
        result_table[columns]
        .to_string(index=False)
    )

    print()
    print(f"Scores : {SCORE_PATH}")
    print(f"Detail : {DETAIL_PATH}")
    print(f"Summary: {SUMMARY_PATH}")
    print("Test accessed: False")


if __name__ == "__main__":
    main()
