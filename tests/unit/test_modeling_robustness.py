"""Tests for locked-test robustness split construction."""

import pandas as pd

from afterlife_ai.modeling.robustness import (
    build_locked_test_robustness_assignments,
)


def _canonical() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "scenario_group_id": [
                "G01",
                "G02",
                "G03",
                "G04",
                "G05",
                "G06",
                "G07",
                "G08",
            ],
            "split": [
                "train",
                "train",
                "train",
                "train",
                "validation",
                "validation",
                "test",
                "test",
            ],
        }
    )


def test_primary_seed_preserves_canonical_assignments() -> None:
    canonical = _canonical()

    result = (
        build_locked_test_robustness_assignments(
            canonical,
            seed=42,
            primary_seed=42,
        )
    )

    expected = canonical.sort_values(
        "scenario_group_id"
    ).reset_index(drop=True)

    pd.testing.assert_frame_equal(
        result,
        expected,
    )


def test_robustness_seed_keeps_test_groups_locked() -> None:
    canonical = _canonical()

    result = (
        build_locked_test_robustness_assignments(
            canonical,
            seed=137,
            primary_seed=42,
        )
    )

    test_groups = set(
        result.loc[
            result["split"] == "test",
            "scenario_group_id",
        ]
    )

    assert test_groups == {
        "G07",
        "G08",
    }

    assert (
        result["split"].value_counts().to_dict()
        == {
            "train": 4,
            "validation": 2,
            "test": 2,
        }
    )


def test_robustness_split_is_deterministic() -> None:
    canonical = _canonical()

    first = build_locked_test_robustness_assignments(
        canonical,
        seed=2026,
        primary_seed=42,
    )

    second = build_locked_test_robustness_assignments(
        canonical,
        seed=2026,
        primary_seed=42,
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_train_validation_never_overlap_test() -> None:
    result = (
        build_locked_test_robustness_assignments(
            _canonical(),
            seed=137,
            primary_seed=42,
        )
    )

    test_groups = set(
        result.loc[
            result["split"] == "test",
            "scenario_group_id",
        ]
    )

    development_groups = set(
        result.loc[
            result["split"].isin(
                ["train", "validation"]
            ),
            "scenario_group_id",
        ]
    )

    assert not (
        test_groups
        & development_groups
    )
