"""Deterministic artifact serialization for synthetic datasets."""

import csv
import hashlib
import json
from pathlib import Path

from afterlife_ai.synthetic.config import SyntheticDatasetConfig
from afterlife_ai.synthetic.dataset import SyntheticDatasetBundle
from afterlife_ai.synthetic.outcome import OutcomeRecipeConfig
from afterlife_ai.synthetic.schema_contract import ModelFeatureContract

_CANDIDATE_METADATA_FIELDS = [
    "scenario_group_id",
    "business_profile_id",
    "request_id",
    "lot_id",
    "candidate_id",
    "source_type",
]

_ORACLE_FIELDS = [
    "scenario_group_id",
    "business_profile_id",
    "request_id",
    "lot_id",
    "candidate_id",
    "source_type",
    "generator_success_probability",
]


def sha256_file(path: Path) -> str:
    """Return SHA-256 digest for one file."""

    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def _write_csv(
    path: Path,
    *,
    fieldnames: list[str],
    records: list[dict[str, object]],
) -> None:
    """Write deterministic UTF-8 CSV with stable column order."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=fieldnames,
            extrasaction="raise",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(records)


def build_dataset_manifest(
    *,
    bundle: SyntheticDatasetBundle,
    config: SyntheticDatasetConfig,
    recipe: OutcomeRecipeConfig,
    contract: ModelFeatureContract,
    candidate_path: Path,
    oracle_path: Path,
) -> dict[str, object]:
    """Build deterministic dataset metadata and artifact hashes."""

    return {
        "manifest_version": "1.0.0",
        "dataset_kind": "SYNTHETIC_GENERATED",
        "claim_boundary": (
            "Synthetic dataset generated from schema-v2 contracts and "
            "versioned synthetic rules. It is not real transaction data "
            "and does not establish real-world rescue probabilities."
        ),
        "feature_schema_version": config.feature_schema.version,
        "generator_config_version": config.config_version,
        "outcome_recipe_version": recipe.recipe_version,
        "primary_seed": config.randomness.primary_seed,
        "scenario_group_count": bundle.scenario_group_count,
        "candidate_row_count": bundle.row_count,
        "positive_count": bundle.positive_count,
        "negative_count": bundle.row_count - bundle.positive_count,
        "positive_rate": round(bundle.positive_rate, 8),
        "model_feature_count": len(contract.model_features),
        "categorical_feature_count": len(
            contract.allowed_categorical_features
        ),
        "numeric_feature_count": len(
            contract.allowed_numeric_features
        ),
        "target": contract.canonical_target,
        "latent_oracle_field": contract.latent_generator_field,
        "group_split_fields": contract.group_split_fields,
        "candidate_artifact": {
            "path": candidate_path.as_posix(),
            "sha256": sha256_file(candidate_path),
        },
        "oracle_artifact": {
            "path": oracle_path.as_posix(),
            "sha256": sha256_file(oracle_path),
        },
    }


def write_dataset_artifacts(
    *,
    bundle: SyntheticDatasetBundle,
    config: SyntheticDatasetConfig,
    recipe: OutcomeRecipeConfig,
    contract: ModelFeatureContract,
    candidate_path: Path,
    oracle_path: Path,
    manifest_path: Path,
) -> dict[str, object]:
    """Serialize candidate, oracle, and deterministic manifest artifacts."""

    candidate_fields = [
        *_CANDIDATE_METADATA_FIELDS,
        *contract.model_features,
        contract.canonical_target,
    ]

    candidate_records = [
        row.to_training_record(contract)
        for row in bundle.candidate_rows
    ]
    oracle_records = [
        row.to_oracle_record()
        for row in bundle.oracle_rows
    ]

    _write_csv(
        candidate_path,
        fieldnames=candidate_fields,
        records=candidate_records,
    )
    _write_csv(
        oracle_path,
        fieldnames=_ORACLE_FIELDS,
        records=oracle_records,
    )

    manifest = build_dataset_manifest(
        bundle=bundle,
        config=config,
        recipe=recipe,
        contract=contract,
        candidate_path=candidate_path,
        oracle_path=oracle_path,
    )

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return manifest


__all__ = [
    "build_dataset_manifest",
    "sha256_file",
    "write_dataset_artifacts",
]
