"""Generate B0/B1 validation predictions without touching test."""

from pathlib import Path

import pandas as pd

from afterlife_ai.modeling.baselines import (
    attach_split_assignments,
    fit_action_prior,
    load_baseline_config,
    score_action_prior,
    score_rule_priority,
    select_modeling_split,
)

BASELINE_CONFIG_PATH = Path("configs/baseline_v1.yaml")
CANDIDATE_PATH = Path(
    "data/generated/synthetic_candidates_v2.csv"
)
SPLIT_GROUPS_PATH = Path(
    "reports/evidence/synthetic_dataset/SPLIT_GROUPS_v2.csv"
)
OUTPUT_PATH = Path(
    "reports/evidence/modeling/"
    "BASELINE_VALIDATION_PREDICTIONS_v1.csv"
)


def main() -> None:
    """Fit B1 on train and score validation with B0/B1."""

    config = load_baseline_config(BASELINE_CONFIG_PATH)

    candidate = pd.read_csv(CANDIDATE_PATH)
    assignments = pd.read_csv(SPLIT_GROUPS_PATH)

    modeling = attach_split_assignments(
        candidate,
        assignments,
    )

    train = select_modeling_split(
        modeling,
        config.split_policy.fit_split,
    )
    validation = select_modeling_split(
        modeling,
        config.split_policy.selection_split,
    )

    b1_model = fit_action_prior(
        train,
        config.b1_action_prior,
    )

    b0 = score_rule_priority(
        validation,
        config.b0_rule_priority,
    )
    b1 = score_action_prior(
        validation,
        b1_model,
        config.b1_action_prior,
    )

    predictions = pd.concat(
        [b0, b1],
        ignore_index=True,
    )

    predictions = predictions.sort_values(
        [
            "baseline_id",
            "scenario_group_id",
            "candidate_id",
        ],
        kind="stable",
    ).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    predictions.to_csv(
        OUTPUT_PATH,
        index=False,
        lineterminator="\n",
    )

    print("Baseline validation scoring complete")
    print(f"Train rows      : {len(train)}")
    print(f"Validation rows : {len(validation)}")
    print(f"B0 rows         : {len(b0)}")
    print(f"B1 rows         : {len(b1)}")
    print(f"B1 global prior : {b1_model.global_prior:.6f}")

    print()
    print("B1 action priors:")

    for action, prior in sorted(
        b1_model.action_priors.items()
    ):
        print(f"  {action:<22} {prior:.6f}")

    print()
    print(f"Evidence: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
