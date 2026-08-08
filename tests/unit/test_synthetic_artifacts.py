"""Tests for deterministic synthetic dataset artifact writing."""

import csv
import json
from pathlib import Path

from afterlife_ai.synthetic.artifacts import (
    sha256_file,
    write_dataset_artifacts,
)
from afterlife_ai.synthetic.config import (
    load_synthetic_dataset_config,
)
from afterlife_ai.synthetic.dataset import (
    assemble_synthetic_dataset,
)
from afterlife_ai.synthetic.outcome import load_outcome_recipe
from afterlife_ai.synthetic.scenarios import (
    generate_scenario_candidates,
)
from afterlife_ai.synthetic.schema_contract import (
    load_model_feature_contract,
)

CONFIG_PATH = Path("configs/synthetic_dataset_v2.yaml")
SCHEMA_PATH = Path("docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml")
RECIPE_PATH = Path("configs/synthetic_outcome_v1.yaml")


def _small_bundle():
    config = load_synthetic_dataset_config(CONFIG_PATH)
    contract = load_model_feature_contract(SCHEMA_PATH)
    recipe = load_outcome_recipe(RECIPE_PATH)

    candidates = generate_scenario_candidates(
        seed=config.randomness.primary_seed,
        scenario_groups=10,
        candidates_per_group_min=2,
        candidates_per_group_max=4,
        contract=contract,
    )

    bundle = assemble_synthetic_dataset(
        candidates,
        outcome_seed=1_000_045,
        recipe=recipe,
        contract=contract,
    )

    return bundle, config, recipe, contract


def test_artifact_writer_creates_expected_files(
    tmp_path: Path,
) -> None:
    bundle, config, recipe, contract = _small_bundle()

    candidate_path = tmp_path / "candidate.csv"
    oracle_path = tmp_path / "oracle.csv"
    manifest_path = tmp_path / "manifest.json"

    write_dataset_artifacts(
        bundle=bundle,
        config=config,
        recipe=recipe,
        contract=contract,
        candidate_path=candidate_path,
        oracle_path=oracle_path,
        manifest_path=manifest_path,
    )

    assert candidate_path.is_file()
    assert oracle_path.is_file()
    assert manifest_path.is_file()


def test_candidate_csv_excludes_oracle_probability(
    tmp_path: Path,
) -> None:
    bundle, config, recipe, contract = _small_bundle()

    candidate_path = tmp_path / "candidate.csv"
    oracle_path = tmp_path / "oracle.csv"
    manifest_path = tmp_path / "manifest.json"

    write_dataset_artifacts(
        bundle=bundle,
        config=config,
        recipe=recipe,
        contract=contract,
        candidate_path=candidate_path,
        oracle_path=oracle_path,
        manifest_path=manifest_path,
    )

    with candidate_path.open(
        encoding="utf-8",
        newline="",
    ) as file_handle:
        reader = csv.DictReader(file_handle)
        assert reader.fieldnames is not None

        assert "generator_success_probability" not in reader.fieldnames
        assert contract.canonical_target in reader.fieldnames

        expected_columns = (
            6
            + len(contract.model_features)
            + 1
        )
        assert len(reader.fieldnames) == expected_columns


def test_oracle_csv_contains_only_oracle_contract(
    tmp_path: Path,
) -> None:
    bundle, config, recipe, contract = _small_bundle()

    candidate_path = tmp_path / "candidate.csv"
    oracle_path = tmp_path / "oracle.csv"
    manifest_path = tmp_path / "manifest.json"

    write_dataset_artifacts(
        bundle=bundle,
        config=config,
        recipe=recipe,
        contract=contract,
        candidate_path=candidate_path,
        oracle_path=oracle_path,
        manifest_path=manifest_path,
    )

    with oracle_path.open(
        encoding="utf-8",
        newline="",
    ) as file_handle:
        reader = csv.DictReader(file_handle)
        assert reader.fieldnames is not None

        assert reader.fieldnames == [
            "scenario_group_id",
            "business_profile_id",
            "request_id",
            "lot_id",
            "candidate_id",
            "source_type",
            "generator_success_probability",
        ]


def test_manifest_hashes_match_written_files(
    tmp_path: Path,
) -> None:
    bundle, config, recipe, contract = _small_bundle()

    candidate_path = tmp_path / "candidate.csv"
    oracle_path = tmp_path / "oracle.csv"
    manifest_path = tmp_path / "manifest.json"

    manifest = write_dataset_artifacts(
        bundle=bundle,
        config=config,
        recipe=recipe,
        contract=contract,
        candidate_path=candidate_path,
        oracle_path=oracle_path,
        manifest_path=manifest_path,
    )

    assert (
        manifest["candidate_artifact"]["sha256"]
        == sha256_file(candidate_path)
    )
    assert (
        manifest["oracle_artifact"]["sha256"]
        == sha256_file(oracle_path)
    )


def test_manifest_is_valid_json_and_has_counts(
    tmp_path: Path,
) -> None:
    bundle, config, recipe, contract = _small_bundle()

    candidate_path = tmp_path / "candidate.csv"
    oracle_path = tmp_path / "oracle.csv"
    manifest_path = tmp_path / "manifest.json"

    write_dataset_artifacts(
        bundle=bundle,
        config=config,
        recipe=recipe,
        contract=contract,
        candidate_path=candidate_path,
        oracle_path=oracle_path,
        manifest_path=manifest_path,
    )

    payload = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    assert payload["candidate_row_count"] == bundle.row_count
    assert (
        payload["scenario_group_count"]
        == bundle.scenario_group_count
    )
    assert payload["model_feature_count"] == 30
    assert payload["dataset_kind"] == "SYNTHETIC_GENERATED"


def test_same_bundle_produces_byte_identical_artifacts(
    tmp_path: Path,
) -> None:
    bundle, config, recipe, contract = _small_bundle()

    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first_candidate = first_dir / "candidate.csv"
    first_oracle = first_dir / "oracle.csv"
    first_manifest = first_dir / "manifest.json"

    second_candidate = second_dir / "candidate.csv"
    second_oracle = second_dir / "oracle.csv"
    second_manifest = second_dir / "manifest.json"

    write_dataset_artifacts(
        bundle=bundle,
        config=config,
        recipe=recipe,
        contract=contract,
        candidate_path=first_candidate,
        oracle_path=first_oracle,
        manifest_path=first_manifest,
    )
    write_dataset_artifacts(
        bundle=bundle,
        config=config,
        recipe=recipe,
        contract=contract,
        candidate_path=second_candidate,
        oracle_path=second_oracle,
        manifest_path=second_manifest,
    )

    assert first_candidate.read_bytes() == second_candidate.read_bytes()
    assert first_oracle.read_bytes() == second_oracle.read_bytes()

    first_payload = json.loads(
        first_manifest.read_text(encoding="utf-8")
    )
    second_payload = json.loads(
        second_manifest.read_text(encoding="utf-8")
    )

    first_payload["candidate_artifact"]["path"] = "candidate.csv"
    first_payload["oracle_artifact"]["path"] = "oracle.csv"
    second_payload["candidate_artifact"]["path"] = "candidate.csv"
    second_payload["oracle_artifact"]["path"] = "oracle.csv"

    assert first_payload == second_payload
