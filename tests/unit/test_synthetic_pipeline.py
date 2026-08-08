"""Tests for end-to-end synthetic dataset generation orchestration."""

import json
from pathlib import Path

import yaml

from afterlife_ai.synthetic.pipeline import (
    run_synthetic_dataset_pipeline,
)

BASE_CONFIG_PATH = Path("configs/synthetic_dataset_v2.yaml")
RECIPE_PATH = Path("configs/synthetic_outcome_v1.yaml")


def _small_config(
    tmp_path: Path,
) -> Path:
    payload = yaml.safe_load(
        BASE_CONFIG_PATH.read_text(encoding="utf-8")
    )

    payload["generation"]["scenario_groups"] = 20
    payload["generation"]["candidate_rows_min"] = 40
    payload["generation"]["candidate_rows_max"] = 160

    payload["artifacts"]["candidate_table"] = str(
        tmp_path / "candidate.csv"
    )
    payload["artifacts"]["oracle_table"] = str(
        tmp_path / "oracle.csv"
    )
    payload["artifacts"]["dataset_manifest"] = str(
        tmp_path / "manifest.json"
    )

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )

    return config_path


def test_pipeline_writes_dataset_and_evidence_manifest(
    tmp_path: Path,
) -> None:
    config_path = _small_config(tmp_path)
    evidence_path = tmp_path / "evidence.json"

    bundle, manifest = run_synthetic_dataset_pipeline(
        config_path=config_path,
        recipe_path=RECIPE_PATH,
        evidence_manifest_path=evidence_path,
    )

    assert bundle.scenario_group_count == 20
    assert 40 <= bundle.row_count <= 160

    assert (tmp_path / "candidate.csv").is_file()
    assert (tmp_path / "oracle.csv").is_file()
    assert (tmp_path / "manifest.json").is_file()
    assert evidence_path.is_file()

    evidence_payload = json.loads(
        evidence_path.read_text(encoding="utf-8")
    )

    assert evidence_payload == manifest


def test_pipeline_is_byte_reproducible(
    tmp_path: Path,
) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first_dir.mkdir()
    second_dir.mkdir()

    first_config = _small_config(first_dir)
    second_config = _small_config(second_dir)

    first_evidence = first_dir / "evidence.json"
    second_evidence = second_dir / "evidence.json"

    _, first_manifest = run_synthetic_dataset_pipeline(
        config_path=first_config,
        recipe_path=RECIPE_PATH,
        evidence_manifest_path=first_evidence,
    )
    _, second_manifest = run_synthetic_dataset_pipeline(
        config_path=second_config,
        recipe_path=RECIPE_PATH,
        evidence_manifest_path=second_evidence,
    )

    first_candidate = first_dir / "candidate.csv"
    second_candidate = second_dir / "candidate.csv"

    first_oracle = first_dir / "oracle.csv"
    second_oracle = second_dir / "oracle.csv"

    assert first_candidate.read_bytes() == second_candidate.read_bytes()
    assert first_oracle.read_bytes() == second_oracle.read_bytes()

    assert (
        first_manifest["candidate_artifact"]["sha256"]
        == second_manifest["candidate_artifact"]["sha256"]
    )
    assert (
        first_manifest["oracle_artifact"]["sha256"]
        == second_manifest["oracle_artifact"]["sha256"]
    )
