"""Deterministic grouped train/validation/test splitting."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from afterlife_ai.synthetic.config import SyntheticDatasetConfig

_SPLIT_ORDER = ("train", "validation", "test")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def assign_grouped_splits(
    candidate: pd.DataFrame,
    *,
    config: SyntheticDatasetConfig,
) -> pd.DataFrame:
    """Assign each scenario group to exactly one deterministic split."""

    group_column = config.split.unit

    if group_column not in candidate.columns:
        raise ValueError(
            f"Required split column tidak ditemukan: {group_column}"
        )

    groups = sorted(
        candidate[group_column].astype(str).unique().tolist()
    )

    if not groups:
        raise ValueError("Dataset tidak memiliki scenario groups.")

    rng = np.random.default_rng(config.randomness.primary_seed)

    shuffled = np.array(groups, dtype=object)
    rng.shuffle(shuffled)

    group_count = len(shuffled)

    train_count = round(group_count * config.split.train)
    validation_count = round(
        group_count * config.split.validation
    )
    test_count = group_count - train_count - validation_count

    if min(train_count, validation_count, test_count) <= 0:
        raise ValueError(
            "Semua grouped split harus memiliki minimal satu group."
        )

    assignments: dict[str, str] = {}

    train_end = train_count
    validation_end = train_end + validation_count

    for group_id in shuffled[:train_end]:
        assignments[str(group_id)] = "train"

    for group_id in shuffled[train_end:validation_end]:
        assignments[str(group_id)] = "validation"

    for group_id in shuffled[validation_end:]:
        assignments[str(group_id)] = "test"

    group_stats = (
        candidate.groupby(group_column, sort=True)
        .agg(
            row_count=("candidate_id", "size"),
        )
        .reset_index()
    )

    group_stats["scenario_group_id"] = (
        group_stats[group_column].astype(str)
    )

    group_stats["split"] = group_stats[
        "scenario_group_id"
    ].map(assignments)

    if group_stats["split"].isna().any():
        raise RuntimeError(
            "Sebagian scenario group tidak mendapat split assignment."
        )

    result = group_stats[
        [
            "scenario_group_id",
            "split",
            "row_count",
        ]
    ].copy()

    split_rank = {
        split: rank
        for rank, split in enumerate(_SPLIT_ORDER)
    }

    result["_split_rank"] = result["split"].map(split_rank)

    result = (
        result.sort_values(
            ["_split_rank", "scenario_group_id"],
            kind="stable",
        )
        .drop(columns="_split_rank")
        .reset_index(drop=True)
    )

    validate_grouped_split(result)

    return result


def validate_grouped_split(assignments: pd.DataFrame) -> None:
    """Validate that group assignments are complete and leakage-free."""

    required_columns = {
        "scenario_group_id",
        "split",
    }

    missing = required_columns - set(assignments.columns)

    if missing:
        raise ValueError(
            "Split assignment kehilangan required columns: "
            f"{sorted(missing)}"
        )

    if assignments["scenario_group_id"].duplicated().any():
        raise ValueError(
            "Satu scenario_group_id tidak boleh muncul lebih dari sekali."
        )

    invalid_splits = set(assignments["split"]) - set(_SPLIT_ORDER)

    if invalid_splits:
        raise ValueError(
            f"Invalid split labels: {sorted(invalid_splits)}"
        )

    for split in _SPLIT_ORDER:
        if not (assignments["split"] == split).any():
            raise ValueError(
                f"Split {split!r} tidak memiliki scenario group."
            )


def build_split_manifest(
    *,
    candidate_path: Path,
    assignments: pd.DataFrame,
    config: SyntheticDatasetConfig,
) -> dict[str, object]:
    """Build grouped-split evidence without exposing test outcomes."""

    total_groups = len(assignments)
    total_rows = int(assignments["row_count"].sum())

    split_summary: dict[str, object] = {}

    group_sets: dict[str, set[str]] = {}

    for split in _SPLIT_ORDER:
        frame = assignments[assignments["split"] == split]

        groups = set(
            frame["scenario_group_id"].astype(str)
        )
        group_sets[split] = groups

        split_summary[split] = {
            "group_count": int(len(frame)),
            "group_fraction": (
                len(frame) / total_groups
            ),
            "row_count": int(frame["row_count"].sum()),
            "row_fraction": (
                float(frame["row_count"].sum())
                / total_rows
            ),
        }

    train_validation_overlap = (
        group_sets["train"] & group_sets["validation"]
    )
    train_test_overlap = (
        group_sets["train"] & group_sets["test"]
    )
    validation_test_overlap = (
        group_sets["validation"] & group_sets["test"]
    )

    leakage_count = (
        len(train_validation_overlap)
        + len(train_test_overlap)
        + len(validation_test_overlap)
    )

    if leakage_count:
        raise RuntimeError("Group leakage terdeteksi.")

    return {
        "manifest_version": "1.0.0",
        "split_unit": config.split.unit,
        "split_seed": config.randomness.primary_seed,
        "random_row_split_allowed": (
            config.split.random_row_split_allowed
        ),
        "test_split_policy": config.split.test_split_policy,
        "candidate_artifact_sha256": _sha256_file(
            candidate_path
        ),
        "total_group_count": total_groups,
        "total_row_count": total_rows,
        "configured_fraction": {
            "train": config.split.train,
            "validation": config.split.validation,
            "test": config.split.test,
        },
        "splits": split_summary,
        "group_leakage_count": leakage_count,
        "group_leakage": False,
        "test_outcomes_inspected_for_model_selection": False,
        "claim_boundary": (
            "Split assignments are deterministic grouped partitions. "
            "The test partition is reserved for final locked evaluation."
        ),
    }


def write_split_artifacts(
    *,
    assignments: pd.DataFrame,
    manifest: dict[str, object],
    processed_assignment_path: Path,
    evidence_assignment_path: Path,
    evidence_manifest_path: Path,
) -> None:
    """Write stable grouped-split artifacts."""

    processed_assignment_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    evidence_assignment_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    evidence_manifest_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    assignments.to_csv(
        processed_assignment_path,
        index=False,
        lineterminator="\n",
    )
    assignments.to_csv(
        evidence_assignment_path,
        index=False,
        lineterminator="\n",
    )

    evidence_manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


__all__ = [
    "assign_grouped_splits",
    "build_split_manifest",
    "validate_grouped_split",
    "write_split_artifacts",
]
