"""Robustness split helpers that preserve the locked test set."""

from random import Random

import pandas as pd

_ALLOWED_SPLITS = {
    "train",
    "validation",
    "test",
}


def build_locked_test_robustness_assignments(
    canonical_assignments: pd.DataFrame,
    *,
    seed: int,
    primary_seed: int = 42,
) -> pd.DataFrame:
    """Reshuffle train/validation while preserving canonical test groups."""

    required = {
        "scenario_group_id",
        "split",
    }

    missing = required - set(
        canonical_assignments.columns
    )

    if missing:
        raise ValueError(
            "Canonical assignments kehilangan "
            f"columns: {sorted(missing)}"
        )

    canonical = canonical_assignments[
        [
            "scenario_group_id",
            "split",
        ]
    ].copy()

    canonical["scenario_group_id"] = (
        canonical[
            "scenario_group_id"
        ].astype(str)
    )

    if (
        canonical[
            "scenario_group_id"
        ].duplicated().any()
    ):
        raise ValueError(
            "scenario_group_id harus unik "
            "pada split manifest."
        )

    observed_splits = set(
        canonical["split"].astype(str)
    )

    if observed_splits != _ALLOWED_SPLITS:
        raise ValueError(
            "Canonical split manifest harus "
            "memiliki train, validation, dan test."
        )

    canonical = canonical.sort_values(
        "scenario_group_id"
    ).reset_index(drop=True)

    if seed == primary_seed:
        return canonical

    train_count = int(
        (canonical["split"] == "train").sum()
    )

    validation_count = int(
        (
            canonical["split"]
            == "validation"
        ).sum()
    )

    test_groups = set(
        canonical.loc[
            canonical["split"] == "test",
            "scenario_group_id",
        ]
    )

    development_groups = sorted(
        set(
            canonical[
                "scenario_group_id"
            ]
        )
        - test_groups
    )

    expected_development_count = (
        train_count
        + validation_count
    )

    if (
        len(development_groups)
        != expected_development_count
    ):
        raise RuntimeError(
            "Canonical development pool size "
            "tidak konsisten."
        )

    rng = Random(seed)
    rng.shuffle(development_groups)

    train_groups = set(
        development_groups[
            :train_count
        ]
    )

    validation_groups = set(
        development_groups[
            train_count:
        ]
    )

    if (
        len(validation_groups)
        != validation_count
    ):
        raise RuntimeError(
            "Robustness validation size "
            "tidak konsisten."
        )

    records: list[
        dict[str, str]
    ] = []

    for group_id in sorted(
        train_groups
    ):
        records.append(
            {
                "scenario_group_id": group_id,
                "split": "train",
            }
        )

    for group_id in sorted(
        validation_groups
    ):
        records.append(
            {
                "scenario_group_id": group_id,
                "split": "validation",
            }
        )

    for group_id in sorted(
        test_groups
    ):
        records.append(
            {
                "scenario_group_id": group_id,
                "split": "test",
            }
        )

    result = pd.DataFrame(
        records
    ).sort_values(
        "scenario_group_id"
    ).reset_index(drop=True)

    observed_test_groups = set(
        result.loc[
            result["split"] == "test",
            "scenario_group_id",
        ]
    )

    if observed_test_groups != test_groups:
        raise RuntimeError(
            "Locked canonical test groups berubah."
        )

    counts = (
        result["split"]
        .value_counts()
        .to_dict()
    )

    expected_counts = {
        "train": train_count,
        "validation": validation_count,
        "test": len(test_groups),
    }

    if counts != expected_counts:
        raise RuntimeError(
            "Robustness split counts berubah: "
            f"{counts} != {expected_counts}"
        )

    return result


__all__ = [
    "build_locked_test_robustness_assignments",
]
