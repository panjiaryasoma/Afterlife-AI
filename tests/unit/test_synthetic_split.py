"""Tests for deterministic scenario-group splitting."""

from pathlib import Path

import pandas as pd
import pytest

from afterlife_ai.synthetic.config import (
    load_synthetic_dataset_config,
)
from afterlife_ai.synthetic.split import (
    assign_grouped_splits,
    build_split_manifest,
)

CONFIG_PATH = Path("configs/synthetic_dataset_v2.yaml")


def _candidate_frame(group_count: int = 100) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for group_number in range(1, group_count + 1):
        group_id = f"SG-{group_number:05d}"

        for candidate_number in range(1, 4):
            rows.append(
                {
                    "scenario_group_id": group_id,
                    "candidate_id": (
                        f"CAND-{group_number:05d}-"
                        f"{candidate_number:02d}"
                    ),
                    "simulated_rescue_outcome": (
                        candidate_number % 2
                    ),
                }
            )

    return pd.DataFrame(rows)


def test_group_split_is_deterministic() -> None:
    config = load_synthetic_dataset_config(CONFIG_PATH)
    candidate = _candidate_frame()

    first = assign_grouped_splits(
        candidate,
        config=config,
    )
    second = assign_grouped_splits(
        candidate,
        config=config,
    )

    pd.testing.assert_frame_equal(first, second)


def test_each_group_appears_exactly_once() -> None:
    config = load_synthetic_dataset_config(CONFIG_PATH)
    candidate = _candidate_frame()

    assignments = assign_grouped_splits(
        candidate,
        config=config,
    )

    assert assignments["scenario_group_id"].is_unique
    assert len(assignments) == 100


def test_group_split_has_no_overlap() -> None:
    config = load_synthetic_dataset_config(CONFIG_PATH)
    candidate = _candidate_frame()

    assignments = assign_grouped_splits(
        candidate,
        config=config,
    )

    train = set(
        assignments.loc[
            assignments["split"] == "train",
            "scenario_group_id",
        ]
    )
    validation = set(
        assignments.loc[
            assignments["split"] == "validation",
            "scenario_group_id",
        ]
    )
    test = set(
        assignments.loc[
            assignments["split"] == "test",
            "scenario_group_id",
        ]
    )

    assert train.isdisjoint(validation)
    assert train.isdisjoint(test)
    assert validation.isdisjoint(test)

    assert train | validation | test == set(
        candidate["scenario_group_id"]
    )


def test_2400_groups_produce_exact_group_counts() -> None:
    config = load_synthetic_dataset_config(CONFIG_PATH)
    candidate = _candidate_frame(group_count=2400)

    assignments = assign_grouped_splits(
        candidate,
        config=config,
    )

    counts = assignments["split"].value_counts().to_dict()

    assert counts == {
        "train": 1680,
        "validation": 360,
        "test": 360,
    }


def test_manifest_reports_zero_leakage(
    tmp_path: Path,
) -> None:
    config = load_synthetic_dataset_config(CONFIG_PATH)
    candidate = _candidate_frame()

    candidate_path = tmp_path / "candidate.csv"
    candidate.to_csv(candidate_path, index=False)

    assignments = assign_grouped_splits(
        candidate,
        config=config,
    )

    manifest = build_split_manifest(
        candidate_path=candidate_path,
        assignments=assignments,
        config=config,
    )

    assert manifest["group_leakage"] is False
    assert manifest["group_leakage_count"] == 0
    assert (
        manifest["test_split_policy"]
        == "LOCKED_FINAL_EVALUATION"
    )
    assert (
        manifest[
            "test_outcomes_inspected_for_model_selection"
        ]
        is False
    )


def test_split_assignment_does_not_expose_outcomes() -> None:
    config = load_synthetic_dataset_config(CONFIG_PATH)
    candidate = _candidate_frame()

    assignments = assign_grouped_splits(
        candidate,
        config=config,
    )

    assert list(assignments.columns) == [
        "scenario_group_id",
        "split",
        "row_count",
    ]

    assert "simulated_rescue_outcome" not in assignments.columns
    assert "positive_count" not in assignments.columns
    assert "negative_count" not in assignments.columns
    assert "positive_rate" not in assignments.columns



def test_missing_group_column_is_rejected() -> None:
    config = load_synthetic_dataset_config(CONFIG_PATH)

    candidate = pd.DataFrame(
        {
            "candidate_id": ["CAND-001"],
            "simulated_rescue_outcome": [1],
        }
    )

    with pytest.raises(
        ValueError,
        match="Required split column",
    ):
        assign_grouped_splits(
            candidate,
            config=config,
        )
